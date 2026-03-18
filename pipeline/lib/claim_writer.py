"""Shared helpers for writing raw_items + claims from automated analyzers.

Extracts the 2-step upsert pattern used by import_nutrition_claims.py
into reusable functions so all analyzers follow the same conventions.
"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pipeline.lib.hashing import content_hash
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("claim_writer")


def upsert_raw_item(
    source_type,   # type: str
    source_id,     # type: str
    raw_payload,   # type: Dict[str, Any]
    scraper_version,  # type: str
    source_url=None,  # type: Optional[str]
    source_date=None,  # type: Optional[str]
):
    # type: (...) -> Optional[str]
    """Insert or find a raw_item. Returns the UUID or None on failure."""
    client = get_client()
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "source_type": source_type,
        "source_id": source_id,
        "captured_at": now,
        "raw_payload": raw_payload,
        "content_hash": content_hash(raw_payload),
        "scraper_version": scraper_version,
    }
    if source_url is not None:
        row["source_url"] = source_url
    if source_date is not None:
        row["source_date"] = source_date

    try:
        resp = (
            client.table("raw_items")
            .upsert(row, on_conflict="source_type,source_id")
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]

        # Upsert returned empty (already existed) — fetch the ID
        existing = (
            client.table("raw_items")
            .select("id")
            .eq("source_type", source_type)
            .eq("source_id", source_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            return existing.data[0]["id"]

        log.error("Could not get raw_item ID for %s/%s", source_type, source_id)
        return None
    except Exception as exc:
        log.error("Failed to upsert raw_item %s: %s", source_id, str(exc)[:200])
        return None


def upsert_claim(
    raw_item_id,       # type: str
    extractor_version,  # type: str
    claim_fields,      # type: Dict[str, Any]
    claim_index=0,     # type: int
):
    # type: (...) -> Optional[str]
    """Insert or update a claim. Returns the claim UUID or None on failure.

    claim_fields should contain keys like: brand, product_name, category,
    old_size, old_size_unit, new_size, new_size_unit, old_price, new_price,
    retailer, upc, observed_date, change_description, confidence.
    """
    client = get_client()
    row = {
        "raw_item_id": raw_item_id,
        "extractor_version": extractor_version,
        "claim_index": claim_index,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "status": "pending",
    }

    # Copy allowed claim fields
    for key in (
        "brand", "product_name", "category",
        "old_size", "old_size_unit", "new_size", "new_size_unit",
        "old_price", "new_price", "retailer", "upc",
        "observed_date", "change_description", "confidence",
    ):
        if key in claim_fields:
            row[key] = claim_fields[key]

    try:
        resp = (
            client.table("claims")
            .upsert(row, on_conflict="raw_item_id,extractor_version,claim_index")
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]
        return None
    except Exception as exc:
        log.error(
            "Failed to upsert claim for raw_item %s: %s",
            raw_item_id, str(exc)[:200],
        )
        return None
