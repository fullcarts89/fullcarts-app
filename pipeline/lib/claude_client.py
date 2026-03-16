"""Claude API client wrapper for claim extraction.

Provides rate-limited, retry-enabled access to Claude Haiku for
extracting structured shrinkflation claims from raw text and images.
"""
import json
import os
import time
from typing import Any, Dict, List, Optional

from pipeline.lib.logging_setup import get_logger

log = get_logger("claude_client")


class CreditExhaustedError(Exception):
    """Raised when the Anthropic API reports insufficient credits."""
    pass


# ── Configuration ────────────────────────────────────────────────────────────

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# Rate limiting: ~2 requests/sec to stay well under Haiku's 4000 RPM limit
_MIN_REQUEST_INTERVAL = 0.5  # seconds between requests
_last_request_time = 0.0

# Retry configuration
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 2  # seconds — exponential backoff: 2, 4, 8


def _get_session():
    # type: () -> Any
    """Lazy-init a requests session with auth headers."""
    import requests

    session = requests.Session()
    session.headers.update({
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    })
    return session


_session = None  # type: Optional[Any]


def _ensure_session():
    # type: () -> Any
    global _session
    if _session is None:
        _session = _get_session()
    return _session


def _rate_limit():
    # type: () -> None
    """Enforce minimum interval between API calls."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < _MIN_REQUEST_INTERVAL:
        time.sleep(_MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def extract_claim_text(
    system_prompt,  # type: str
    user_message,  # type: str
    max_tokens=1024,  # type: int
):
    # type: (...) -> Optional[Dict[str, Any]]
    """Call Claude Haiku with a text prompt and return parsed JSON response.

    Args:
        system_prompt: System prompt with extraction instructions.
        user_message: The text to extract claims from.
        max_tokens: Maximum tokens in response.

    Returns:
        Parsed JSON dict from Claude's response, or None on failure.
    """
    return _call_claude(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": user_message}],
        max_tokens=max_tokens,
    )


def extract_claim_vision(
    system_prompt,  # type: str
    text_content,  # type: str
    image_url,  # type: str
    max_tokens=1024,  # type: int
):
    # type: (...) -> Optional[Dict[str, Any]]
    """Call Claude Haiku with text + image and return parsed JSON response.

    Args:
        system_prompt: System prompt with extraction instructions.
        text_content: Text context (title, body).
        image_url: URL of the image to analyze.
        max_tokens: Maximum tokens in response.

    Returns:
        Parsed JSON dict from Claude's response, or None on failure.
    """
    content = []  # type: List[Dict[str, Any]]

    if text_content.strip():
        content.append({"type": "text", "text": text_content})

    content.append({
        "type": "image",
        "source": {
            "type": "url",
            "url": image_url,
        },
    })

    return _call_claude(
        system_prompt=system_prompt,
        messages=[{"role": "user", "content": content}],
        max_tokens=max_tokens,
    )


def _call_claude(
    system_prompt,  # type: str
    messages,  # type: List[Dict[str, Any]]
    max_tokens,  # type: int
):
    # type: (...) -> Optional[Dict[str, Any]]
    """Make an API call to Claude with retry and rate limiting.

    Returns parsed JSON from the response text, or None on failure.
    """
    session = _ensure_session()

    payload = {
        "model": HAIKU_MODEL,
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": messages,
    }

    for attempt in range(_MAX_RETRIES):
        _rate_limit()

        try:
            resp = session.post(
                ANTHROPIC_API_URL,
                json=payload,
                timeout=30,
            )

            if resp.status_code == 200:
                data = resp.json()
                text = _extract_text(data)
                if text is None:
                    log.warning("No text content in Claude response")
                    return None
                return _parse_json_response(text)

            if resp.status_code == 429 or resp.status_code >= 500:
                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                log.warning(
                    "Claude API %d (attempt %d/%d). Retrying in %ds...",
                    resp.status_code, attempt + 1, _MAX_RETRIES, delay,
                )
                time.sleep(delay)
                continue

            # Detect credit exhaustion — abort immediately
            if resp.status_code == 400 and "credit balance" in resp.text:
                log.error("Anthropic API credits exhausted. Aborting.")
                raise CreditExhaustedError(resp.text[:300])

            # Non-retryable error
            log.error(
                "Claude API error %d: %s",
                resp.status_code, resp.text[:500],
            )
            return None

        except CreditExhaustedError:
            raise
        except Exception as exc:
            delay = _RETRY_BASE_DELAY * (2 ** attempt)
            log.warning(
                "Claude API exception (attempt %d/%d): %s. Retrying in %ds...",
                attempt + 1, _MAX_RETRIES, str(exc)[:200], delay,
            )
            time.sleep(delay)

    log.error("Claude API failed after %d retries", _MAX_RETRIES)
    return None


def _extract_text(response_data):
    # type: (Dict[str, Any]) -> Optional[str]
    """Extract text content from Claude API response."""
    content = response_data.get("content", [])
    for block in content:
        if block.get("type") == "text":
            return block.get("text", "")
    return None


def _parse_json_response(text):
    # type: (str) -> Any
    """Parse JSON from Claude's response text.

    Handles responses wrapped in markdown code blocks.
    Returns a dict (single claim) or list of dicts (multi-claim).
    """
    text = text.strip()

    # Strip markdown code block if present
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first line (```json or ```) and last line (```)
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
        elif len(lines) == 2:
            text = lines[1].rstrip("`").strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        log.warning("Failed to parse Claude JSON response: %s", str(exc)[:200])
        log.debug("Raw response: %s", text[:500])
        return None
