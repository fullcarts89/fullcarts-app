#!/usr/bin/env python3
"""Detect size/price changes from Kroger weekly observations.

Compares variant_observations (source_type='kroger_api') for the same
product across consecutive weeks. Flags size decreases >=2% or
price-per-unit increases >=5%. Creates claims for detected changes.

Usage:
    python -m pipeline.scripts.analyze_kroger_changes
    python -m pipeline.scripts.analyze_kroger_changes --dry-run
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from pipeline.lib.claim_writer import upsert_claim, upsert_raw_item
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import convert_to_base

log = get_logger("analyze_kroger_changes")

EXTRACTOR_VERSION = "kroger-change-v1"
SCRAPER_VERSION = "pipeline-v2.0-kroger-change"
SOURCE_TYPE = "kroger_change"
SIZE_DECREASE_THRESHOLD = 2.0   # percent
PPU_INCREASE_THRESHOLD = 5.0    # percent
_PAGE_SIZE = 1000
_LOOKBACK_DAYS = 30


def detect_changes(observations):
    # type: (List[Dict[str, Any]]) -> List[Dict[str, Any]]
    """Detect size/price changes in a list of observations for one variant+store.

    observations must be sorted by observed_date ascending.
    Each observation has: observed_date, size, size_unit, price, price_per_unit.

    Returns list of change dicts.
    """
    changes = []  # type: List[Dict[str, Any]]

    for i in range(1, len(observations)):
        old = observations[i - 1]
        new = observations[i]

        old_size = old.get("size")
        new_size = new.get("size")
        old_unit = old.get("size_unit", "")
        new_unit = new.get("size_unit", "")
        old_price = old.get("price")
        new_price = new.get("price")
        old_ppu = old.get("price_per_unit")
        new_ppu = new.get("price_per_unit")

        change_type = None

        # Check size decrease
        if old_size and new_size and old_size > 0:
            old_base, old_base_unit = convert_to_base(float(old_size), old_unit)
            new_base, new_base_unit = convert_to_base(float(new_size), new_unit)

            if old_base_unit == new_base_unit and old_base > 0:
                size_pct = ((new_base - old_base) / old_base) * 100.0
                if size_pct <= -SIZE_DECREASE_THRESHOLD:
                    change_type = "size_decrease"

        # Check price-per-unit increase (only if size didn't change)
        if change_type is None and old_ppu and new_ppu and old_ppu > 0:
            ppu_pct = ((float(new_ppu) - float(old_ppu)) / float(old_ppu)) * 100.0
            if ppu_pct >= PPU_INCREASE_THRESHOLD:
                change_type = "price_hike"

        if change_type is None:
            continue

        changes.append({
            "change_type": change_type,
            "old_date": str(old["observed_date"]),
            "new_date": str(new["observed_date"]),
            "old_size": float(old_size) if old_size else None,
            "old_size_unit": old_unit,
            "new_size": float(new_size) if new_size else None,
            "new_size_unit": new_unit,
            "old_price": float(old_price) if old_price else None,
            "new_price": float(new_price) if new_price else None,
            "old_ppu": float(old_ppu) if old_ppu else None,
            "new_ppu": float(new_ppu) if new_ppu else None,
            "store_location": old.get("store_location", ""),
        })

    return changes


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Detect size/price changes from Kroger weekly observations"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be generated without writing",
    )
    args = parser.parse_args()

    client = get_client()

    # Step 1: Load recent variant_observations for Kroger
    log.info("Loading Kroger observations (last %d days)...", _LOOKBACK_DAYS)
    observations = _load_kroger_observations(client)
    log.info("Loaded %d observations", len(observations))

    if not observations:
        log.info("No Kroger observations found. Done.")
        return

    # Step 2: Group by variant_id, then by store_location
    by_variant = defaultdict(lambda: defaultdict(list))  # type: Dict[str, Dict[str, List]]
    for obs in observations:
        vid = obs["variant_id"]
        store = obs.get("store_location") or "unknown"
        by_variant[vid][store].append(obs)

    log.info("Grouped into %d variants", len(by_variant))

    # Step 3: Detect changes per variant+store
    # Deduplicate: collect unique changes per variant (across stores)
    variant_changes = {}  # type: Dict[str, Dict[str, Any]]

    for variant_id, stores in by_variant.items():
        for store, obs_list in stores.items():
            # Sort by date ascending
            obs_list.sort(key=lambda o: str(o["observed_date"]))
            changes = detect_changes(obs_list)

            for change in changes:
                # Key: variant_id + old_date + new_date (dedupe across stores)
                change_key = "%s_%s_%s" % (variant_id, change["old_date"], change["new_date"])

                if change_key not in variant_changes:
                    variant_changes[change_key] = {
                        "variant_id": variant_id,
                        "change": change,
                        "store_count": 1,
                        "stores": [store],
                    }
                else:
                    variant_changes[change_key]["store_count"] += 1
                    variant_changes[change_key]["stores"].append(store)

    log.info("Detected %d unique changes across all variants", len(variant_changes))

    if not variant_changes:
        log.info("No changes detected. Done.")
        return

    # Step 4: Batch-load product metadata for flagged variants
    flagged_variant_ids = list(set(vc["variant_id"] for vc in variant_changes.values()))
    product_meta = _load_variant_metadata(client, flagged_variant_ids)
    log.info("Loaded metadata for %d/%d variants", len(product_meta), len(flagged_variant_ids))

    # Step 5: Generate claims
    created = 0
    skipped = 0

    for change_key, vc in variant_changes.items():
        variant_id = vc["variant_id"]
        change = vc["change"]
        store_count = vc["store_count"]
        meta = product_meta.get(variant_id, {})

        entity = meta.get("product_entities") or {}
        brand = entity.get("brand", "")
        product_name = entity.get("canonical_name", "")
        category = entity.get("category", "other") or "other"
        upc = meta.get("upc", "")

        # Build change description
        if change["change_type"] == "size_decrease":
            desc = "Kroger: %s %s %s%s -> %s%s" % (
                brand, product_name,
                change["old_size"], change["old_size_unit"],
                change["new_size"], change["new_size_unit"],
            )
            if change["old_size"] and change["new_size"] and change["old_size"] > 0:
                pct = ((change["new_size"] - change["old_size"]) / change["old_size"]) * 100
                desc += " (%.1f%%)" % pct
        else:
            desc = "Kroger: %s %s price per unit $%.2f -> $%.2f" % (
                brand, product_name,
                change["old_ppu"] or 0, change["new_ppu"] or 0,
            )
            if change["old_ppu"] and change["new_ppu"] and change["old_ppu"] > 0:
                pct = ((change["new_ppu"] - change["old_ppu"]) / change["old_ppu"]) * 100
                desc += " (+%.1f%%)" % pct

        if store_count > 1:
            desc += " (confirmed at %d stores)" % store_count

        if args.dry_run:
            log.info("[DRY RUN] %s", desc)
            created += 1
            continue

        # Create raw_item
        source_id = "kroger_chg_%s_%s_%s" % (
            variant_id, change["old_date"], change["new_date"],
        )
        raw_payload = {
            "variant_id": variant_id,
            "upc": upc,
            "brand": brand,
            "product_name": product_name,
            "change_type": change["change_type"],
            "old_date": change["old_date"],
            "new_date": change["new_date"],
            "old_size": change["old_size"],
            "old_size_unit": change["old_size_unit"],
            "new_size": change["new_size"],
            "new_size_unit": change["new_size_unit"],
            "old_price": change["old_price"],
            "new_price": change["new_price"],
            "store_count": store_count,
        }

        raw_item_id = upsert_raw_item(
            SOURCE_TYPE, source_id, raw_payload, SCRAPER_VERSION,
        )
        if raw_item_id is None:
            skipped += 1
            continue

        # Create claim
        claim_fields = {
            "brand": brand or None,
            "product_name": product_name or None,
            "category": category,
            "old_size": change["old_size"],
            "old_size_unit": change["old_size_unit"] or None,
            "new_size": change["new_size"],
            "new_size_unit": change["new_size_unit"] or None,
            "old_price": change["old_price"],
            "new_price": change["new_price"],
            "retailer": "Kroger",
            "upc": upc or None,
            "observed_date": change["new_date"],
            "change_description": desc,
            "confidence": {
                "brand": 0.99,
                "product_name": 0.99,
                "size_change": 0.90,
                "overall": 0.85,
            },
        }

        claim_id = upsert_claim(raw_item_id, EXTRACTOR_VERSION, claim_fields)
        if claim_id:
            created += 1
        else:
            skipped += 1

    log.info("Done: created=%d, skipped=%d", created, skipped)


def _load_kroger_observations(client):
    # type: (Any) -> List[Dict[str, Any]]
    """Load recent Kroger variant_observations, paginated by id."""
    from datetime import timedelta
    cutoff = (datetime.now(timezone.utc) - timedelta(days=_LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    all_obs = []  # type: List[Dict[str, Any]]
    last_id = ""

    while True:
        query = (
            client.table("variant_observations")
            .select("id,variant_id,observed_date,size,size_unit,price,price_per_unit,store_location")
            .eq("source_type", "kroger_api")
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
