#!/usr/bin/env python3
"""Generate claims from USDA size-change raw_items.

Reads existing usda_size_change raw_items (created by usda_variance.py),
applies noise filters (decreases only, 2-50% range, no flip-flops,
consecutive releases), and creates claims for plausible candidates.

Usage:
    python -m pipeline.scripts.generate_usda_size_claims
    python -m pipeline.scripts.generate_usda_size_claims --dry-run
"""
import argparse
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

from pipeline.config import USDA_RELEASES
from pipeline.lib.claim_writer import upsert_claim
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("generate_usda_size_claims")

EXTRACTOR_VERSION = "usda-size-change-v1"
MIN_DECREASE_PCT = -50.0
MAX_DECREASE_PCT = -2.0
_PAGE_SIZE = 1000

# Build set of consecutive release date pairs for filtering
_RELEASE_DATES = [r[0] for r in USDA_RELEASES]
_CONSECUTIVE_PAIRS = set()  # type: Set[Tuple[str, str]]
for i in range(len(_RELEASE_DATES) - 1):
    _CONSECUTIVE_PAIRS.add((_RELEASE_DATES[i], _RELEASE_DATES[i + 1]))

# Map USDA branded_food_category to FullCarts claim categories
_CATEGORY_MAP = {
    "snack": "snacks",
    "chip": "chips",
    "cereal": "cereal",
    "cookie": "cookies",
    "cracker": "crackers",
    "candy": "candy",
    "confection": "candy",
    "chocolate": "candy",
    "beverage": "beverages",
    "drink": "beverages",
    "water": "beverages",
    "soda": "beverages",
    "juice": "beverages",
    "coffee": "beverages",
    "tea": "beverages",
    "dairy": "dairy",
    "milk": "dairy",
    "cheese": "dairy",
    "yogurt": "dairy",
    "ice cream": "ice cream",
    "frozen": "frozen meals",
    "canned": "canned goods",
    "soup": "canned goods",
    "bread": "bread",
    "bakery": "bread",
    "pasta": "pasta",
    "noodle": "pasta",
    "condiment": "condiments",
    "sauce": "condiments",
    "dressing": "condiments",
    "meat": "meat",
    "poultry": "meat",
    "seafood": "meat",
    "produce": "produce",
    "fruit": "produce",
    "vegetable": "produce",
}


def _map_category(usda_category):
    # type: (Optional[str]) -> str
    """Map USDA branded_food_category to FullCarts claim category."""
    if not usda_category:
        return "other"
    cat_lower = usda_category.lower()
    for keyword, fc_cat in _CATEGORY_MAP.items():
        if keyword in cat_lower:
            return fc_cat
    return "other"


def _load_all_size_changes(client):
    # type: (Any) -> List[Dict[str, Any]]
    """Load all usda_size_change raw_items, paginated by id."""
    all_items = []  # type: List[Dict[str, Any]]
    last_id = ""

    while True:
        query = (
            client.table("raw_items")
            .select("id,raw_payload")
            .eq("source_type", "usda_size_change")
        )
        if last_id:
            query = query.gt("id", last_id)

        resp = query.order("id").range(0, _PAGE_SIZE - 1).execute()
        rows = resp.data or []
        if not rows:
            break

        all_items.extend(rows)
        last_id = rows[-1]["id"]

        if len(rows) < _PAGE_SIZE:
            break

    return all_items


def _build_flipflop_set(items):
    # type: (List[Dict[str, Any]]) -> Set[str]
    """Find UPCs that have BOTH increases and decreases (flip-flops = noise)."""
    upcs_with_decrease = set()  # type: Set[str]
    upcs_with_increase = set()  # type: Set[str]

    for item in items:
        payload = item.get("raw_payload") or {}
        upc = payload.get("gtin_upc", "")
        direction = payload.get("direction", "")
        if not upc:
            continue
        if direction == "decrease":
            upcs_with_decrease.add(upc)
        elif direction == "increase":
            upcs_with_increase.add(upc)

    return upcs_with_decrease & upcs_with_increase


def _enrich_from_usda_products(client, upcs):
    # type: (Any, List[str]) -> Dict[str, Dict[str, Any]]
    """Batch-lookup product info from usda_products table by UPC."""
    product_map = {}  # type: Dict[str, Dict[str, Any]]
    if not upcs:
        return product_map

    # Query in batches of 50 UPCs
    for i in range(0, len(upcs), 50):
        batch = upcs[i:i + 50]
        resp = (
            client.table("usda_products")
            .select("gtin_upc,brand_name,brand_owner,description,branded_food_category")
            .in_("gtin_upc", batch)
            .execute()
        )
        for row in (resp.data or []):
            upc = row.get("gtin_upc", "")
            if upc and upc not in product_map:
                product_map[upc] = row

    return product_map


def filter_and_generate(items, flipflop_upcs):
    # type: (List[Dict[str, Any]], Set[str]) -> List[Dict[str, Any]]
    """Apply noise filters and return plausible candidates.

    Returns list of dicts with keys: raw_item_id, payload (raw_payload fields).
    """
    candidates = []  # type: List[Dict[str, Any]]

    for item in items:
        payload = item.get("raw_payload") or {}
        upc = payload.get("gtin_upc", "")
        direction = payload.get("direction", "")
        pct_change = payload.get("pct_change", 0)
        old_date = payload.get("old_date", "")
        new_date = payload.get("new_date", "")

        # Filter 1: decreases only
        if direction != "decrease":
            continue

        # Filter 2: realistic range (-50% to -2%)
        if pct_change > MAX_DECREASE_PCT or pct_change < MIN_DECREASE_PCT:
            continue

        # Filter 3: no flip-flops
        if upc in flipflop_upcs:
            continue

        # Filter 4: consecutive releases only
        if (old_date, new_date) not in _CONSECUTIVE_PAIRS:
            continue

        candidates.append({
            "raw_item_id": item["id"],
            "payload": payload,
        })

    return candidates


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Generate claims from USDA size-change analysis"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be generated without writing",
    )
    args = parser.parse_args()

    client = get_client()

    # Step 1: Load all usda_size_change raw_items
    log.info("Loading usda_size_change raw_items...")
    all_items = _load_all_size_changes(client)
    log.info("Loaded %d usda_size_change raw_items", len(all_items))

    if not all_items:
        log.info("No size change data. Done.")
        return

    # Step 2: Build flip-flop filter
    flipflop_upcs = _build_flipflop_set(all_items)
    log.info("Found %d flip-flop UPCs (will be skipped)", len(flipflop_upcs))

    # Step 3: Apply filters
    candidates = filter_and_generate(all_items, flipflop_upcs)
    log.info(
        "After filtering: %d candidates from %d raw items "
        "(filters: decrease-only, 2-50%% range, no flip-flops, consecutive releases)",
        len(candidates), len(all_items),
    )

    if not candidates:
        log.info("No candidates after filtering. Done.")
        return

    # Step 4: Enrich with product info from usda_products
    candidate_upcs = list(set(
        c["payload"].get("gtin_upc", "") for c in candidates if c["payload"].get("gtin_upc")
    ))
    product_map = _enrich_from_usda_products(client, candidate_upcs)
    log.info("Enriched %d/%d UPCs from usda_products", len(product_map), len(candidate_upcs))

    # Step 5: Generate claims
    created = 0
    skipped = 0

    for candidate in candidates:
        payload = candidate["payload"]
        raw_item_id = candidate["raw_item_id"]
        upc = payload.get("gtin_upc", "")

        # Get enriched product info or fall back to raw_payload
        product = product_map.get(upc, {})
        brand = (
            product.get("brand_name")
            or product.get("brand_owner")
            or payload.get("brand_owner", "")
        )
        product_name = product.get("description") or payload.get("description", "")
        category = _map_category(product.get("branded_food_category"))

        old_size = payload.get("old_size")
        old_unit = payload.get("old_unit", "")
        new_size = payload.get("new_size")
        new_unit = payload.get("new_unit", "")
        pct_change = payload.get("pct_change", 0)
        old_date = payload.get("old_date", "")
        new_date = payload.get("new_date", "")

        change_desc = "USDA: %s %s%s -> %s%s (%.1f%%) between %s and %s" % (
            product_name[:60] if product_name else "Unknown",
            old_size, old_unit,
            new_size, new_unit,
            pct_change,
            old_date, new_date,
        )

        if args.dry_run:
            log.info(
                "[DRY RUN] %s | %s | %s%s -> %s%s (%.1f%%)",
                brand[:30] if brand else "?",
                product_name[:40] if product_name else "?",
                old_size, old_unit,
                new_size, new_unit,
                pct_change,
            )
            created += 1
            continue

        claim_fields = {
            "brand": brand or None,
            "product_name": product_name or None,
            "category": category,
            "old_size": old_size,
            "old_size_unit": old_unit or None,
            "new_size": new_size,
            "new_size_unit": new_unit or None,
            "upc": upc or None,
            "observed_date": new_date or None,
            "change_description": change_desc,
            "confidence": {
                "brand": 0.90,
                "product_name": 0.85,
                "size_change": 0.65,
                "overall": 0.60,
            },
        }

        claim_id = upsert_claim(raw_item_id, EXTRACTOR_VERSION, claim_fields)
        if claim_id:
            created += 1
        else:
            skipped += 1

    log.info("Done: created=%d, skipped=%d", created, skipped)


if __name__ == "__main__":
    main()
