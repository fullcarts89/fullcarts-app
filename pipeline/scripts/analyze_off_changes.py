#!/usr/bin/env python3
"""Detect size changes from Open Food Facts daily observations.

Compares variant_observations (source_type='openfoodfacts') for the same
product across consecutive dates. Flags size decreases >=2%.
Creates claims for detected changes.

Usage:
    python -m pipeline.scripts.analyze_off_changes
    python -m pipeline.scripts.analyze_off_changes --dry-run
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.lib.claim_writer import upsert_claim, upsert_raw_item
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import convert_to_base

log = get_logger("analyze_off_changes")

EXTRACTOR_VERSION = "off-change-v1"
SCRAPER_VERSION = "pipeline-v2.0-off-change"
SOURCE_TYPE = "off_change"
SIZE_DECREASE_THRESHOLD = 2.0   # percent
_PAGE_SIZE = 1000
_LOOKBACK_DAYS = 90


def detect_changes(observations):
    # type: (List[Dict[str, Any]]) -> Optional[Dict[str, Any]]
    """Detect the most recent size decrease for a variant.

    observations must be sorted by observed_date ascending.
    Returns a single change dict for the most recent decrease, or None.
    Only flags the latest change to avoid duplicate claims for ongoing trends.
    """
    latest_change = None  # type: Optional[Dict[str, Any]]

    for i in range(1, len(observations)):
        old = observations[i - 1]
        new = observations[i]

        old_size = old.get("size")
        new_size = new.get("size")
        old_unit = old.get("size_unit", "")
        new_unit = new.get("size_unit", "")

        if not old_size or not new_size or float(old_size) <= 0:
            continue

        old_base, old_base_unit = convert_to_base(float(old_size), old_unit)
        new_base, new_base_unit = convert_to_base(float(new_size), new_unit)

        if old_base_unit != new_base_unit or old_base <= 0:
            continue

        pct_change = ((new_base - old_base) / old_base) * 100.0

        if pct_change <= -SIZE_DECREASE_THRESHOLD:
            latest_change = {
                "old_date": str(old["observed_date"]),
                "new_date": str(new["observed_date"]),
                "old_size": float(old_size),
                "old_size_unit": old_unit,
                "new_size": float(new_size),
                "new_size_unit": new_unit,
                "pct_change": round(pct_change, 2),
            }

    return latest_change


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Detect size changes from Open Food Facts observations"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be generated without writing",
    )
    args = parser.parse_args()

    client = get_client()

    # Step 1: Load recent OFF variant_observations
    log.info("Loading OFF observations (last %d days)...", _LOOKBACK_DAYS)
    observations = _load_off_observations(client)
    log.info("Loaded %d observations", len(observations))

    if not observations:
        log.info("No OFF observations found. Done.")
        return

    # Step 2: Group by variant_id
    by_variant = defaultdict(list)  # type: Dict[str, List[Dict[str, Any]]]
    for obs in observations:
        by_variant[obs["variant_id"]].append(obs)

    log.info("Grouped into %d variants", len(by_variant))

    # Step 3: Detect changes per variant (most recent only)
    variant_changes = {}  # type: Dict[str, Dict[str, Any]]

    for variant_id, obs_list in by_variant.items():
        if len(obs_list) < 2:
            continue

        # Sort by date ascending
        obs_list.sort(key=lambda o: str(o["observed_date"]))
        change = detect_changes(obs_list)

        if change is not None:
            variant_changes[variant_id] = change

    log.info("Detected %d variants with size decreases", len(variant_changes))

    if not variant_changes:
        log.info("No changes detected. Done.")
        return

    # Step 4: Batch-load product metadata
    flagged_variant_ids = list(variant_changes.keys())
    product_meta = _load_variant_metadata(client, flagged_variant_ids)
    log.info("Loaded metadata for %d/%d variants", len(product_meta), len(flagged_variant_ids))

    # Step 5: Generate claims
    created = 0
    skipped = 0

    for variant_id, change in variant_changes.items():
        meta = product_meta.get(variant_id, {})
        entity = meta.get("product_entities") or {}
        brand = entity.get("brand", "")
        product_name = entity.get("canonical_name", "")
        category = entity.get("category", "other") or "other"
        upc = meta.get("upc", "")

        desc = "Open Food Facts: %s %s %s%s -> %s%s (%.1f%%)" % (
            brand, product_name,
            change["old_size"], change["old_size_unit"],
            change["new_size"], change["new_size_unit"],
            change["pct_change"],
        )

        if args.dry_run:
            log.info("[DRY RUN] %s", desc)
            created += 1
            continue

        # Create raw_item
        source_id = "off_chg_%s_%s_%s" % (
            variant_id, change["old_date"], change["new_date"],
        )
        raw_payload = {
            "variant_id": variant_id,
            "upc": upc,
            "brand": brand,
            "product_name": product_name,
            "old_date": change["old_date"],
            "new_date": change["new_date"],
            "old_size": change["old_size"],
            "old_size_unit": change["old_size_unit"],
            "new_size": change["new_size"],
            "new_size_unit": change["new_size_unit"],
            "pct_change": change["pct_change"],
        }

        raw_item_id = upsert_raw_item(
            SOURCE_TYPE, source_id, raw_payload, SCRAPER_VERSION,
        )
        if raw_item_id is None:
            skipped += 1
            continue

        # Create claim (no retailer, no price for OFF)
        claim_fields = {
            "brand": brand or None,
            "product_name": product_name or None,
            "category": category,
            "old_size": change["old_size"],
            "old_size_unit": change["old_size_unit"] or None,
            "new_size": change["new_size"],
            "new_size_unit": change["new_size_unit"] or None,
            "upc": upc or None,
            "observed_date": change["new_date"],
            "change_description": desc,
            "confidence": {
                "brand": 0.90,
                "product_name": 0.85,
                "size_change": 0.75,
                "overall": 0.70,
            },
        }

        claim_id = upsert_claim(raw_item_id, EXTRACTOR_VERSION, claim_fields)
        if claim_id:
            created += 1
        else:
            skipped += 1

    log.info("Done: created=%d, skipped=%d", created, skipped)


def _load_off_observations(client):
    # type: (Any) -> List[Dict[str, Any]]
    """Load recent OFF variant_observations, paginated by id."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=_LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    all_obs = []  # type: List[Dict[str, Any]]
    last_id = ""

    while True:
        query = (
            client.table("variant_observations")
            .select("id,variant_id,observed_date,size,size_unit")
            .eq("source_type", "openfoodfacts")
            .gte("observed_date", cutoff)
        )
        if last_id:
            query = query.gt("id", last_id)

        resp = query.order("id").range(0, _PAGE_SIZE - 1).execute()
        rows = resp.data or []
        if not rows:
            break

        all_obs.extend(rows)
        last_id = rows[-1]["id"]

        if len(rows) < _PAGE_SIZE:
            break

    return all_obs


def _load_variant_metadata(client, variant_ids):
    # type: (Any, List[str]) -> Dict[str, Dict[str, Any]]
    """Batch-load pack_variants + product_entities for given variant_ids."""
    meta = {}  # type: Dict[str, Dict[str, Any]]

    for i in range(0, len(variant_ids), 50):
        batch = variant_ids[i:i + 50]
        resp = (
            client.table("pack_variants")
            .select("id,upc,variant_name,entity_id,product_entities(id,canonical_name,brand,category)")
            .in_("id", batch)
            .execute()
        )
        for row in (resp.data or []):
            meta[row["id"]] = row

    return meta


if __name__ == "__main__":
    main()
