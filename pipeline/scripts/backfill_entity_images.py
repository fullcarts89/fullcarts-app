#!/usr/bin/env python3
"""Backfill product_entities.image_url from available sources.

Priority order:
  1. Supabase Storage (claim-images bucket) — curated from Reddit posts
  2. Kroger API product images (from raw_items.raw_payload)
  3. Walmart API product images (from raw_items.raw_payload)
  4. Open Food Facts product images (from raw_items.raw_payload)

Usage:
    python -m pipeline.scripts.backfill_entity_images
    python -m pipeline.scripts.backfill_entity_images --dry-run
    python -m pipeline.scripts.backfill_entity_images --limit 500
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("backfill_entity_images")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
STORAGE_BUCKET = "claim-images"
PAGE_SIZE = 200


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _public_storage_url(path: str) -> str:
    """Build the public URL for a Supabase Storage object."""
    return "{}/storage/v1/object/public/{}/{}".format(
        SUPABASE_URL, STORAGE_BUCKET, path
    )


def _fetch_entities_without_images(sb, limit: int = 0) -> List[Dict[str, Any]]:
    """Fetch product_entities where image_url IS NULL.

    Paginates via id-keyset to bypass PostgREST's per-request row cap
    (default 1000). Ordered by id (not brand) so updating a row's image_url
    in-flight doesn't shift the cursor.
    """
    out = []  # type: List[Dict[str, Any]]
    last_id = None
    while True:
        q = (
            sb.table("product_entities")
            .select("id, brand, canonical_name")
            .is_("image_url", "null")
            .order("id")
            .limit(PAGE_SIZE)
        )
        if last_id is not None:
            q = q.gt("id", last_id)
        resp = q.execute()
        batch = resp.data or []
        if not batch:
            break
        out.extend(batch)
        last_id = batch[-1]["id"]
        if limit > 0 and len(out) >= limit:
            return out[:limit]
        if len(batch) < PAGE_SIZE:
            break
    return out


def _try_claim_image(sb, entity_id: str) -> Optional[str]:
    """Check if any matched claim has an image in Supabase Storage."""
    resp = (
        sb.table("claims")
        .select("image_storage_path")
        .eq("matched_entity_id", entity_id)
        .not_.is_("image_storage_path", "null")
        .limit(1)
        .execute()
    )
    if resp.data and resp.data[0].get("image_storage_path"):
        return _public_storage_url(resp.data[0]["image_storage_path"])
    return None


def _try_api_image(sb, entity_id: str, source_type: str) -> Optional[str]:
    """Check raw_items for an image URL from a retail API source.

    Joins entity -> pack_variants -> raw_items via UPC matching.
    """
    # Get UPCs for this entity's variants
    variants = (
        sb.table("pack_variants")
        .select("upc")
        .eq("entity_id", entity_id)
        .not_.is_("upc", "null")
        .execute()
    )
    upcs = [v["upc"] for v in (variants.data or []) if v.get("upc")]
    if not upcs:
        return None

    for upc in upcs[:3]:
        resp = (
            sb.table("raw_items")
            .select("raw_payload")
            .eq("source_type", source_type)
            .ilike("source_id", "%{}%".format(upc))
            .limit(1)
            .execute()
        )
        if not resp.data:
            continue

        payload = resp.data[0].get("raw_payload") or {}
        url = _extract_image_from_payload(payload, source_type)
        if url:
            return url

    return None


def _extract_image_from_payload(
    payload: Dict[str, Any], source_type: str
) -> Optional[str]:
    """Extract image URL from a raw_items payload by source type."""
    if source_type == "kroger_api":
        images = payload.get("images") or []
        if images:
            sizes = images[0].get("sizes") or []
            if sizes:
                return sizes[0].get("url")
        return None

    if source_type == "walmart":
        return payload.get("largeImage") or payload.get("mediumImage")

    if source_type == "openfoodfacts":
        return payload.get("image_url") or payload.get("image_front_url")

    return None


def main():
    parser = argparse.ArgumentParser(description="Backfill entity images")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    args = parser.parse_args()

    sb = _get_client()

    LOG.info("Fetching entities without images...")
    entities = _fetch_entities_without_images(sb, limit=args.limit)
    LOG.info("Found %d entities missing images", len(entities))

    if not entities:
        LOG.info("All entities have images. Done.")
        return

    stats = {"updated": 0, "still_missing": 0, "errors": 0}
    sources_tried = [
        ("claim", None),
        ("kroger_api", "kroger_api"),
        ("walmart", "walmart"),
        ("openfoodfacts", "openfoodfacts"),
    ]

    for i, entity in enumerate(entities):
        eid = entity["id"]
        image_url = None

        try:
            # Try each source in priority order
            for source_name, source_type in sources_tried:
                if source_name == "claim":
                    image_url = _try_claim_image(sb, eid)
                else:
                    image_url = _try_api_image(sb, eid, source_type)

                if image_url:
                    break

            if image_url:
                if not args.dry_run:
                    sb.table("product_entities").update(
                        {"image_url": image_url}
                    ).eq("id", eid).execute()
                stats["updated"] += 1
                if stats["updated"] <= 5:
                    LOG.info(
                        "  [%s] %s / %s → %s",
                        "DRY" if args.dry_run else "SET",
                        entity.get("brand", "?"),
                        entity.get("canonical_name", "?"),
                        source_name,
                    )
            else:
                stats["still_missing"] += 1

        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 10:
                LOG.error("Error on entity %s: %s", eid[:8], e)

        if (i + 1) % 100 == 0:
            LOG.info(
                "  Progress: %d/%d (updated=%d, missing=%d)",
                i + 1, len(entities), stats["updated"], stats["still_missing"],
            )

    mode = "DRY RUN" if args.dry_run else "LIVE"
    LOG.info("\n%s RESULTS:", mode)
    for k, v in stats.items():
        LOG.info("  %s: %d", k, v)


if __name__ == "__main__":
    main()
