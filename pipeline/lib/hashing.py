"""Content hashing for deduplication."""
import hashlib
import json
from typing import Any


def content_hash(payload: Any) -> str:
    """SHA-256 of JSON-serialized payload for deduplication.

    Keys are sorted and non-serializable values are coerced to strings
    to ensure deterministic output.
    """
    raw = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()
