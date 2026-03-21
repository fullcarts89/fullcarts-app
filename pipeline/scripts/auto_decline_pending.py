#!/usr/bin/env python3
"""One-time script to auto-decline pending claims that don't meet quality bar.

Rules:
- News/GDELT claims with no brand or no size/price change -> discarded
- Reddit claims with no image in raw_payload -> discarded

Usage:
    python -m pipeline.scripts.auto_decline_pending [--dry-run]
"""
import argparse
from typing import Any, Dict, List, Set

from pipeline.lib.image_archiver import extract_image_url
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("auto_decline_pending")

PAGE_SIZE = 1000


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Auto-decline low-quality pending claims"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be declined without updating",
    )
    args = parser.parse_args()

    client = get_client()

    # Fetch all pending claims with their raw_items
    pending_claims = _fetch_pending_claims_with_raw(client)
    log.info("Found %d pending claims to evaluate", len(pending_claims))

    to_decline = []  # type: List[str]

    for claim in pending_claims:
        raw = claim.get("raw_items") or {}
        source_type = raw.get("source_type", "")
        payload = raw.get("raw_payload", {})

        if source_type in ("news", "gdelt"):
            brand = claim.get("brand")
            if not brand:
                to_decline.append(claim["id"])
                log.debug("Decline %s: %s claim with no brand", claim["id"][:8], source_type)
                continue
            has_size = claim.get("old_size") is not None and claim.get("new_size") is not None
            has_price = claim.get("old_price") is not None and claim.get("new_price") is not None
            if not has_size and not has_price:
                to_decline.append(claim["id"])
                log.debug("Decline %s: %s claim with no size/price change", claim["id"][:8], source_type)
                continue

        if source_type == "reddit":
            image_url = extract_image_url(payload)
            if not image_url:
                to_decline.append(claim["id"])
                log.debug("Decline %s: reddit claim with no image", claim["id"][:8])
                continue

    log.info("Will decline %d of %d pending claims", len(to_decline), len(pending_claims))

    if args.dry_run:
        log.info("[DRY RUN] No changes made")
        return

    # Batch update in chunks
    batch_size = 100
    declined = 0
    for i in range(0, len(to_decline), batch_size):
        batch = to_decline[i:i + batch_size]
        try:
            client.table("claims").update(
                {"status": "discarded"}
            ).in_("id", batch).execute()
            declined += len(batch)
            log.info("Declined %d/%d", declined, len(to_decline))
        except Exception as exc:
            log.error("Failed to decline batch at offset %d: %s", i, str(exc)[:200])

    log.info("Done: declined %d claims", declined)


def _fetch_pending_claims_with_raw(client):
    # type: (Any) -> List[Dict[str, Any]]
    """Fetch all pending claims joined with raw_items source info."""
    all_claims = []  # type: List[Dict[str, Any]]
    offset = 0

    while True:
        resp = (
            client.table("claims")
            .select(
                "id,brand,product_name,old_size,new_size,old_price,new_price,"
                "raw_items(source_type,raw_payload)"
            )
            .eq("status", "pending")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        if not resp.data:
            break

        all_claims.extend(resp.data)

        if len(resp.data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return all_claims


if __name__ == "__main__":
    main()
