"""Walmart Affiliate API signature-based authentication.

The Walmart API uses RSA-SHA256 signatures instead of OAuth.  Each request
must include four headers:
  WM_CONSUMER.ID         — the consumer ID (UUID)
  WM_SEC.AUTH_SIGNATURE  — Base64-encoded RSA-SHA256 signature
  WM_SEC.KEY_VERSION     — always "1"
  WM_CONSUMER.INTIMESTAMP — current Unix timestamp in milliseconds

The signature is computed over:
    consumerId\ntimestamp\nkeyVersion\n
"""
import base64
import os
import time
from typing import Dict, Optional

from pipeline.config import (
    WALMART_CONSUMER_ID,
    WALMART_PRIVATE_KEY,
    WALMART_PRIVATE_KEY_FILE,
)
from pipeline.lib.logging_setup import get_logger

log = get_logger("walmart_auth")


def _load_private_key_bytes():
    # type: () -> Optional[bytes]
    """Load the RSA private key from env var or PEM file."""
    # Prefer environment variable (GitHub Actions / CI)
    key_str = WALMART_PRIVATE_KEY
    if key_str:
        # Env var may have literal \\n instead of real newlines
        key_str = key_str.replace("\\n", "\n")
        return key_str.encode("utf-8")

    # Fall back to PEM file on disk
    pem_path = WALMART_PRIVATE_KEY_FILE
    if pem_path and os.path.isfile(pem_path):
        with open(pem_path, "rb") as f:
            return f.read()

    return None


def get_auth_headers():
    # type: () -> Optional[Dict[str, str]]
    """Generate Walmart API auth headers for a single request.

    Returns a dict of headers, or None if credentials are missing.
    """
    if not WALMART_CONSUMER_ID:
        log.error("WALMART_CONSUMER_ID not set")
        return None

    key_bytes = _load_private_key_bytes()
    if key_bytes is None:
        log.error(
            "Walmart private key not found — set WALMART_PRIVATE_KEY env var "
            "or place walmart_private_key.pem in the repo root"
        )
        return None

    try:
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding
    except ImportError:
        log.error(
            "cryptography package not installed — "
            "run: pip install cryptography"
        )
        return None

    timestamp_ms = str(int(time.time() * 1000))
    key_version = "1"

    # Build the string to sign: consumerId\ntimestamp\nkeyVersion\n
    message = "%s\n%s\n%s\n" % (WALMART_CONSUMER_ID, timestamp_ms, key_version)

    try:
        private_key = serialization.load_pem_private_key(key_bytes, password=None)
        signature = private_key.sign(
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        sig_b64 = base64.b64encode(signature).decode("utf-8")
    except Exception as exc:
        log.error("Failed to sign Walmart request: %s", exc)
        return None

    return {
        "WM_CONSUMER.ID": WALMART_CONSUMER_ID,
        "WM_SEC.AUTH_SIGNATURE": sig_b64,
        "WM_SEC.KEY_VERSION": key_version,
        "WM_CONSUMER.INTIMESTAMP": timestamp_ms,
    }
