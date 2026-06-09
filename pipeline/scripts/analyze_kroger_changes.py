#!/usr/bin/env python3
"""Detect size/price changes from Kroger weekly observations.

v2 (2026-05-17): guarded against oscillation/unit-flip noise that polluted v1.

Compares variant_observations (source_type='kroger_api') for the same product
across consecutive weeks. Flags a transition only when ALL of the following
hold:

  1. The unit *family* is stable across the change (mass → mass, volume →
     volume, count → count). Cross-family transitions like oz → fl oz are
     skipped — Kroger's API toggles between two representations for the same
     SKU and the size value is meaningless in that case.
  2. The old size was stable for at least 3 consecutive observations before
     the change.
  3. The new size is stable for at least 1 observation after the change AND
     does not revert to the old size within the lookback window. (Pure
     oscillation between two values gets filtered out.)
  4. The new size never appeared *before* the change in the lookback series.
     If it had, this isn't a one-way transition, it's flapping.

v1 fired on any adjacent-week delta ≥2%. Real shrinkflation is a one-way
event (200g → 180g, and it stays at 180g). Kroger's API noise looks like
weekly oscillation. The four guards above keep the former and drop the
latter.

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

EXTRACTOR_VERSION = "kroger-change-v2"
SCRAPER_VERSION = "pipeline-v2.0-kroger-change"
SOURCE_TYPE = "kroger_change"
SIZE_DECREASE_THRESHOLD = 2.0   # percent
PPU_INCREASE_THRESHOLD = 5.0    # percent

# Minimum consecutive prior observations at the same size before we'll trust
# the "old" baseline. v1 used 1 (i.e. any adjacent change), which is what let
# Kroger's API toggling 14oz↔8oz week to week generate hundreds of fake
# shrinkflation events.
_MIN_PRIOR_STABLE = 3
_MIN_POST_STABLE = 1

_PAGE_SIZE = 1000
_LOOKBACK_DAYS = 30


# Unit family map. Crossing families is never legitimate shrinkflation —
# it's a data-quality problem in the source feed.
_UNIT_FAMILIES = {
    # mass
    "g": "mass", "kg": "mass", "mg": "mass", "oz": "mass", "lb": "mass",
    # volume
    "ml": "volume", "l": "volume", "fl oz": "volume",
    "pt": "volume", "qt": "volume", "gal": "volume",
    # count
    "ct": "count", "count": "count", "pack": "count",
    "sheets": "count", "rolls": "count",
}


def _unit_family(unit):
    # type: (Optional[str]) -> Optional[str]
    if not unit:
        return None
    return _UNIT_FAMILIES.get(unit.strip().lower())


def _size_key(observation):
    # type: (Dict[str, Any]) -> Optional[Tuple[float, str]]
    """Return a comparable (base_value, base_unit) tuple for an observation.

    Returns None if the observation has no size or its unit family is unknown.
    """
    size = observation.get("size")
    unit = observation.get("size_unit")
    if size is None or not unit:
        return None
    fam = _unit_family(unit)
    if fam is None:
        return None
    base_value, base_unit = convert_to_base(float(size), unit)
    return (round(base_value, 4), base_unit)


def detect_changes(observations):
    # type: (List[Dict[str, Any]]) -> List[Dict[str, Any]]
    """Detect size/price changes in a sorted observation list for one variant+store.

    observations must be sorted by observed_date ascending.

    Applies the v2 guards: unit family stability, prior stability ≥3 obs,
    post stability ≥1 obs, no later revert to old size, new size unseen
    earlier in series.
    """
    changes = []  # type: List[Dict[str, Any]]
    n = len(observations)
    if n < _MIN_PRIOR_STABLE + 1:
        return changes

    # Precompute a comparable key per observation. None = unparseable size or
    # cross-family unit. We index into this for the oscillation checks below.
    keys = [_size_key(o) for o in observations]  # type: List[Optional[Tuple[float, str]]]

    for i in range(_MIN_PRIOR_STABLE, n):
        prev = observations[i - 1]
        cur = observations[i]

        prev_key = keys[i - 1]
        cur_key = keys[i]

        # Guard 1: both sides must have a parseable size + a known family.
        if prev_key is None or cur_key is None:
            continue

        # Guard 1 (cont.): same unit family on both sides.
        if prev_key[1] != cur_key[1]:
            continue

        # Same key = no change.
        if prev_key == cur_key:
            continue

        old_base, _ = prev_key
        new_base, _ = cur_key
        if old_base <= 0:
            continue

        # Guard 2: prior stability — the old size must have held for the last
        # _MIN_PRIOR_STABLE observations.
        prior_stable = all(
            keys[j] == prev_key
            for j in range(max(0, i - _MIN_PRIOR_STABLE), i)
        )
        if not prior_stable:
            continue

        # Guard 3a: post stability — the new size must persist for at least
        # _MIN_POST_STABLE additional observations after i, OR be the final
        # observation (we'll trust the latest snapshot).
        if i < n - 1:
            post_window = keys[i + 1 : i + 1 + _MIN_POST_STABLE]
            if not all(k == cur_key for k in post_window if k is not None):
                continue

        # Guard 3b: no revert. If the old size reappears anywhere AFTER i in
        # the lookback window, this is flapping, not a one-way change.
        if any(k == prev_key for k in keys[i + 1 :] if k is not None):
            continue

        # Guard 4: new size unseen before i. If the new size already appeared
        # earlier in the series, this is oscillation.
        if any(k == cur_key for k in keys[:i] if k is not None):
            continue

        # Compute deltas and classify.
        size_pct = ((new_base - old_base) / old_base) * 100.0
        change_type = None
        if size_pct <= -SIZE_DECREASE_THRESHOLD:
            change_type = "size_decrease"

        # Price-per-unit increase fallback (only if no size change qualified).
        old_ppu = prev.get("price_per_unit")
        new_ppu = cur.get("price_per_unit")
        if change_type is None and old_ppu and new_ppu and float(old_ppu) > 0:
            ppu_pct = ((float(new_ppu) - float(old_ppu)) / float(old_ppu)) * 100.0
            if ppu_pct >= PPU_INCREASE_THRESHOLD:
                change_type = "price_hike"

        if change_type is None:
            continue

        old_size = prev.get("size")
        new_size = cur.get("size")
        old_price = prev.get("price")
        new_price = cur.get("price")

        changes.append({
            "change_type": change_type,
            "old_date": str(prev["observed_date"]),
            "new_date": str(cur["observed_date"]),
            "old_size": float(old_size) if old_size else None,
            "old_size_unit": prev.get("size_unit", ""),
            "new_size": float(new_size) if new_size else None,
            "new_size_unit": cur.get("size_unit", ""),
            "old_price": float(old_price) if old_price else None,
            "new_price": float(new_price) if new_price else None,
            "old_ppu": float(old_ppu) if old_ppu else None,
            "new_ppu": float(new_ppu) if new_ppu else None,
            "store_location": prev.get("store_location", ""),
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

        # Title + source_url so the admin claims UI can render a useful card.
        # See web/src/app/admin/claims/page.tsx (title falls back to "Untitled"
        # if absent, link falls back to "#" if source_url is null).
        title = "%s %s" % (brand or "", product_name or "")
        title = title.strip() or ("Kroger UPC %s" % upc if upc else "Kroger change")
        source_url = "https://www.kroger.com/p/%s" % upc if upc else None

        if args.dry_run:
            log.info("[DRY RUN] %s", desc)
            created += 1
            continue

        # Create raw_item
        source_id = "kroger_chg_%s_%s_%s" % (
            variant_id, change["old_date"], change["new_date"],
        )
        raw_payload = {
            "title": title,
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
            source_url=source_url,
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
            .select(
                "id,upc,variant_name,entity_id,"
                "product_entities!pack_variants_entity_id_fkey"
                "(id,canonical_name,brand,category)"
            )
            .in_("id", batch)
            .execute()
        )
        for row in (resp.data or []):
            meta[row["id"]] = row

    return meta


if __name__ == "__main__":
    main()
