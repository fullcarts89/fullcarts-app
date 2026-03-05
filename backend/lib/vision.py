"""
Vision analysis for shrinkflation product images using Claude API.

Downloads Reddit post images and uses Claude's vision capability to extract
product details (brand, product name, sizes, weights) that text parsing missed.

Only called when text-based NLP parsing produces weak results (fields_found < 2)
and the post has an image URL — keeping API costs minimal.
"""
import base64
import json
import logging
import os
import re
from io import BytesIO

import requests

log = logging.getLogger("fullcarts")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VISION_MODEL = os.getenv("VISION_MODEL", "claude-haiku-4-5-20251001")

# Only analyse images when text parsing is weak
VISION_MIN_FIELDS = int(os.getenv("VISION_MIN_FIELDS", "2"))

# Image download limits
MAX_IMAGE_BYTES = 5 * 1024 * 1024  # 5 MB
IMAGE_TIMEOUT = 10  # seconds

# Supported media types for Claude vision
_MIME_BY_EXT = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif", ".webp": "image/webp",
}

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = (
    "You are a product-label analyst specializing in shrinkflation detection. "
    "Extract structured data from product photos. Be precise — only report "
    "values you can clearly read or confidently infer from the image."
)

_USER_PROMPT = """\
Analyze this product image from a Reddit shrinkflation post.

Post title: {title}

Extract whatever you can see. Return ONLY valid JSON with these keys:
{{
  "brand": "brand name or null",
  "product": "product name or null",
  "old_size": numeric value or null,
  "new_size": numeric value or null,
  "unit": "oz/g/ml/lb/ct/sheets/rolls or null",
  "old_price": numeric value or null,
  "new_price": numeric value or null,
  "is_shrinkflation": true/false/null,
  "description": "One sentence describing what you see in the image",
  "visual_only": true if sizes are not readable but shrinkflation is visually apparent
}}

Rules:
- old_size should be the LARGER (previous) size, new_size the SMALLER (current) size
- If you see two packages side by side, compare them
- If you can only see one package with a size label, report it as new_size
- If sizes aren't readable but one product is visibly smaller, set visual_only: true
- For visual_only cases, describe what you observe in the description field
- Return null for any field you cannot determine
- Return ONLY the JSON object, no other text
"""


# ---------------------------------------------------------------------------
# Image download
# ---------------------------------------------------------------------------

def _download_image(url: str) -> tuple[bytes, str] | None:
    """Download an image, return (bytes, media_type) or None on failure."""
    try:
        resp = requests.get(url, timeout=IMAGE_TIMEOUT, headers={
            "User-Agent": "FullCartsBot/1.0 (shrinkflation tracker)",
        })
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "image/" not in content_type:
            # Try to guess from URL extension
            for ext, mime in _MIME_BY_EXT.items():
                if ext in url.lower():
                    content_type = mime
                    break
            else:
                log.debug(f"  Vision: skipping non-image content-type: {content_type}")
                return None

        data = resp.content
        if len(data) > MAX_IMAGE_BYTES:
            log.debug(f"  Vision: image too large ({len(data)} bytes)")
            return None

        # Normalize media type
        media_type = content_type.split(";")[0].strip()
        if media_type not in _MIME_BY_EXT.values():
            media_type = "image/jpeg"  # safe fallback

        return data, media_type

    except Exception as exc:
        log.debug(f"  Vision: image download failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Claude Vision API call
# ---------------------------------------------------------------------------

def _call_claude_vision(image_data: bytes, media_type: str, title: str) -> dict | None:
    """Send image to Claude vision API, return parsed JSON response or None."""
    if not ANTHROPIC_API_KEY:
        return None

    b64 = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "model": VISION_MODEL,
        "max_tokens": 512,
        "system": _SYSTEM_PROMPT,
        "messages": [{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64,
                    },
                },
                {
                    "type": "text",
                    "text": _USER_PROMPT.format(title=title),
                },
            ],
        }],
    }

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        body = resp.json()

        # Extract text from response
        text = ""
        for block in body.get("content", []):
            if block.get("type") == "text":
                text += block["text"]

        # Parse JSON from response (handle markdown code blocks)
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        return json.loads(text)

    except json.JSONDecodeError:
        log.debug(f"  Vision: could not parse JSON from response: {text[:200]}")
        return None
    except Exception as exc:
        log.debug(f"  Vision: API call failed: {exc}")
        return None


# ---------------------------------------------------------------------------
# Public interface
# ---------------------------------------------------------------------------

def analyze_image(image_url: str, title: str = "") -> dict | None:
    """Analyze a product image and return extracted data.

    Returns a dict with keys: brand, product, old_size, new_size, unit,
    old_price, new_price, is_shrinkflation, description, visual_only.
    Returns None if analysis fails or is unavailable.
    """
    if not ANTHROPIC_API_KEY:
        log.debug("  Vision: ANTHROPIC_API_KEY not set, skipping")
        return None

    if not image_url:
        return None

    result = _download_image(image_url)
    if not result:
        return None

    image_data, media_type = result
    return _call_claude_vision(image_data, media_type, title)


def should_analyze(parsed: dict, image_url: str | None) -> bool:
    """Decide whether vision analysis is warranted for this post.

    Returns True when:
    - There is an image URL
    - Text-based parsing produced fewer than VISION_MIN_FIELDS fields
    - The Anthropic API key is configured
    """
    if not ANTHROPIC_API_KEY:
        return False
    if not image_url:
        return False
    return parsed["fields_found"] < VISION_MIN_FIELDS


def merge_vision_into_parsed(parsed: dict, vision: dict) -> dict:
    """Merge vision analysis results into the NLP-parsed dict.

    Vision data fills in gaps — it does NOT overwrite fields that text
    parsing already extracted (text is more reliable for exact numbers).
    Returns the updated parsed dict and extra fields for staging.
    """
    if not vision:
        return parsed

    # Fill missing brand
    if not parsed["brand"] and vision.get("brand"):
        parsed["brand"] = vision["brand"]
        parsed["fields_found"] += 1

    # Fill missing product hint
    if not parsed["product_hint"] and vision.get("product"):
        parsed["product_hint"] = vision["product"]

    # Fill missing sizes
    if not parsed["old_size"] and vision.get("old_size") is not None:
        parsed["old_size"] = vision["old_size"]
        if not parsed["new_size"] and vision.get("new_size") is not None:
            parsed["new_size"] = vision["new_size"]
            parsed["fields_found"] += 2
            parsed["explicit_from_to"] = True
        else:
            parsed["fields_found"] += 1
    elif not parsed["new_size"] and vision.get("new_size") is not None:
        parsed["new_size"] = vision["new_size"]
        parsed["fields_found"] += 1

    # Fill units
    if vision.get("unit"):
        if not parsed["old_unit"]:
            parsed["old_unit"] = vision["unit"]
        if not parsed["new_unit"]:
            parsed["new_unit"] = vision["unit"]

    # Fill prices
    if not parsed["old_price"] and vision.get("old_price") is not None:
        parsed["old_price"] = vision["old_price"]
    if not parsed["new_price"] and vision.get("new_price") is not None:
        parsed["new_price"] = vision["new_price"]
        parsed["fields_found"] += 1

    return parsed
