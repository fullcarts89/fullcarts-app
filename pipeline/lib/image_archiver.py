"""Download, resize, and archive claim images to Supabase Storage."""
import io
import re
from typing import Any, Dict, Optional

import requests as http_requests

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("image_archiver")

STORAGE_BUCKET = "claim-images"
MAX_IMAGE_DIM = 1200
WEBP_QUALITY = 80
DOWNLOAD_TIMEOUT = 15

_IMAGE_PATTERNS = [
    r"i\.redd\.it/",
    r"i\.imgur\.com/",
    r"preview\.redd\.it/",
    r"external-preview\.redd\.it/",
    r"\.jpg$",
    r"\.jpeg$",
    r"\.png$",
    r"\.webp$",
    r"\.gif$",
]
_IMAGE_RE = re.compile("|".join(_IMAGE_PATTERNS), re.IGNORECASE)


def extract_image_url(raw_payload):
    # type: (Dict[str, Any]) -> Optional[str]
    """Extract best image URL from a Reddit post payload."""
    url = raw_payload.get("url", "")
    if url and _IMAGE_RE.search(url):
        return url

    media_metadata = raw_payload.get("media_metadata", {})
    if isinstance(media_metadata, dict):
        for meta in media_metadata.values():
            if isinstance(meta, dict):
                source = meta.get("s", {})
                if isinstance(source, dict):
                    img_url = source.get("u", "")
                    if img_url:
                        return img_url.replace("&amp;", "&")

    preview = raw_payload.get("preview", {})
    if isinstance(preview, dict):
        images = preview.get("images", [])
        if images and isinstance(images, list):
            first = images[0]
            if isinstance(first, dict):
                source = first.get("source", {})
                if isinstance(source, dict):
                    img_url = source.get("url", "")
                    if img_url:
                        return img_url.replace("&amp;", "&")

    thumbnail = raw_payload.get("thumbnail", "")
    if thumbnail and thumbnail.startswith("http") and _IMAGE_RE.search(thumbnail):
        return thumbnail

    return None


def download_image(url):
    # type: (str) -> Optional[bytes]
    """Download image bytes. Returns None on failure."""
    try:
        resp = http_requests.get(url, timeout=DOWNLOAD_TIMEOUT, headers={
            "User-Agent": "FullCarts/1.0 (evidence archival)"
        })
        if resp.status_code == 200 and len(resp.content) > 1000:
            content_type = resp.headers.get("content-type", "")
            if "image" in content_type or "octet" in content_type or not content_type:
                return resp.content
        return None
    except Exception as exc:
        log.debug("Download failed for %s: %s", url[:80], str(exc)[:100])
        return None


def resize_to_webp(image_bytes):
    # type: (bytes) -> Optional[bytes]
    """Resize to max 1200px and convert to WebP."""
    try:
        from PIL import Image

        img = Image.open(io.BytesIO(image_bytes))

        if img.mode in ("RGBA", "P", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            if img.mode == "P":
                img = img.convert("RGBA")
            background.paste(img, mask=img.split()[-1] if "A" in img.mode else None)
            img = background
        elif img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > MAX_IMAGE_DIM:
            if w > h:
                new_w = MAX_IMAGE_DIM
                new_h = int(h * MAX_IMAGE_DIM / w)
            else:
                new_h = MAX_IMAGE_DIM
                new_w = int(w * MAX_IMAGE_DIM / h)
            img = img.resize((new_w, new_h), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=WEBP_QUALITY)
        return buf.getvalue()
    except Exception as exc:
        log.debug("Image conversion failed: %s", str(exc)[:100])
        return None


def archive_claim_image(claim_id, raw_payload):
    # type: (str, Dict[str, Any]) -> Optional[str]
    """Download, resize, upload, and return storage path. Best-effort."""
    image_url = extract_image_url(raw_payload)
    if not image_url:
        return None

    raw_bytes = download_image(image_url)
    if raw_bytes is None:
        return None

    webp_bytes = resize_to_webp(raw_bytes)
    if webp_bytes is None:
        return None

    storage_path = "{}.webp".format(claim_id)
    client = get_client()
    try:
        client.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=webp_bytes,
            file_options={"content-type": "image/webp", "upsert": "true"},
        )
        return storage_path
    except Exception as exc:
        log.debug("Upload failed for %s: %s", claim_id[:8], str(exc)[:100])
        return None
