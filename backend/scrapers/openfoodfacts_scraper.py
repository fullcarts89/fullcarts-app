#!/usr/bin/env python3
"""
FullCarts Open Food Facts Weight-Change Monitor
=================================================
Checks products in the FullCarts database against Open Food Facts to
detect weight/size discrepancies that may indicate shrinkflation.

No API key required — Open Food Facts is free and open.

How it works:
  1. Fetch all products from the FullCarts `products` table
  2. For each product with a real UPC (not REDDIT-*), query Open Food Facts
  3. Compare the OFF weight with the stored current_size
  4. If OFF reports a different (smaller) size, create a product_version entry

Usage:
  python -m backend.scrapers.openfoodfacts_scraper
  python -m backend.scrapers.openfoodfacts_scraper --dry-run
  python -m backend.scrapers.openfoodfacts_scraper --upc 048500205020
"""

import os
import sys
import re
import time
import logging
import argparse
from datetime import datetime, timezone
from typing import Optional, List, Tuple

import requests

sys.path.insert(0, ".")

from backend.lib.supabase_client import get_client

log = logging.getLogger("fullcarts.off")

USER_AGENT = "FullCartsBot/1.0 (fullcarts.org community shrinkflation tracker)"

OFF_API = "https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
OFF_SEARCH = "https://world.openfoodfacts.org/cgi/search.pl"

# Regex to extract numeric weight from OFF quantity strings like "12 oz", "340 g"
WEIGHT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(oz|fl\.?\s*oz|g|gram[s]?|kg|ml|l|lb[s]?|ct|count)",
    re.IGNORECASE,
)

UNIT_CONVERSIONS = {
    "kg": ("g", 1000),
    "l": ("ml", 1000),
    "lb": ("oz", 16),
    "lbs": ("oz", 16),
}


def normalize_off_weight(quantity_str: str) -> Tuple[Optional[float], Optional[str]]:
    """Extract numeric weight and unit from an OFF quantity string."""
    if not quantity_str:
        return None, None

    m = WEIGHT_PATTERN.search(quantity_str)
    if not m:
        return None, None

    value = float(m.group(1))
    unit = m.group(2).lower().strip().rstrip("s")

    # Normalize compound units
    if unit in ("fl oz", "fl. oz"):
        unit = "fl oz"

    # Convert kg→g, l→ml, lb→oz for consistency
    if unit in UNIT_CONVERSIONS:
        new_unit, factor = UNIT_CONVERSIONS[unit]
        value = round(value * factor, 2)
        unit = new_unit

    return value, unit


def fetch_off_product(barcode: str) -> Optional[dict]:
    """Fetch a product from Open Food Facts by barcode."""
    url = OFF_API.format(barcode=barcode)
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == 1:
            return data.get("product", {})
        return None
    except Exception as e:
        log.warning(f"OFF lookup failed for {barcode}: {e}")
        return None


def search_off_by_name(name: str, brand: Optional[str] = None) -> List[dict]:
    """Search Open Food Facts by product name."""
    query = f"{brand} {name}" if brand else name
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 5,
        "fields": "code,product_name,brands,quantity,product_quantity,product_quantity_unit",
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(OFF_SEARCH, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return data.get("products", [])
    except Exception as e:
        log.warning(f"OFF search failed for '{query}': {e}")
        return []


def check_product(sb, product: dict, dry_run: bool = False) -> Optional[dict]:
    """Check a single product against Open Food Facts.

    Returns a dict with discrepancy details if found, else None.
    """
    upc = product["upc"]
    current_size = product.get("current_size")
    unit = product.get("unit", "oz")
    name = product.get("name", "")
    brand = product.get("brand")

    # Try barcode lookup first (only for real UPCs)
    off_product = None
    if not upc.startswith("REDDIT-"):
        off_product = fetch_off_product(upc)
        time.sleep(0.5)  # Rate limit

    # Fall back to name search — but only for real products with meaningful
    # names.  REDDIT-* products have Reddit post titles as names (e.g.
    # "Shrinkflation strikes again!") which return unrelated OFF results.
    if not off_product and name and not upc.startswith("REDDIT-"):
        results = search_off_by_name(name, brand)
        if results:
            off_product = results[0]
        time.sleep(0.5)

    if not off_product:
        return None

    # Extract weight from OFF
    quantity = off_product.get("quantity") or ""
    off_size, off_unit = normalize_off_weight(quantity)

    # Also try numeric fields
    if off_size is None:
        pq = off_product.get("product_quantity")
        pqu = off_product.get("product_quantity_unit")
        if pq:
            try:
                off_size = float(pq)
                off_unit = (pqu or "g").lower()
                if off_unit in UNIT_CONVERSIONS:
                    new_unit, factor = UNIT_CONVERSIONS[off_unit]
                    off_size = round(off_size * factor, 2)
                    off_unit = new_unit
            except (ValueError, TypeError):
                pass

    if off_size is None:
        log.debug(f"  No weight data for {upc} on OFF")
        return None

    # Compare units — only meaningful if same unit type
    if off_unit and unit and off_unit.lower() != unit.lower():
        log.debug(f"  Unit mismatch for {upc}: ours={unit}, OFF={off_unit}")
        return None

    # Check for meaningful discrepancy (OFF reports different size)
    if current_size is None:
        return None

    current_size = float(current_size)
    diff_pct = ((off_size - current_size) / current_size * 100) if current_size > 0 else 0

    # Only flag if OFF size is notably different (>2% threshold)
    if abs(diff_pct) < 2.0:
        return None

    off_name = off_product.get("product_name", "")
    off_brands = off_product.get("brands", "")
    log.info(f"  Discrepancy: {name} ({brand})")
    log.info(f"    FullCarts: {current_size} {unit}")
    log.info(f"    OFF:       {off_size} {off_unit} — '{off_name}' ({off_brands})")
    log.info(f"    Delta:     {diff_pct:+.1f}%")

    detail = {
        "name": name, "brand": brand, "upc": upc,
        "current_size": current_size, "unit": unit,
        "off_size": off_size, "off_unit": off_unit or unit,
        "delta": diff_pct,
    }

    if dry_run:
        return detail

    # Record as a new product_version
    try:
        sb.table("product_versions").upsert({
            "product_upc": upc,
            "observed_date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
            "size": off_size,
            "unit": off_unit or unit,
            "source": "openfoodfacts",
            "source_url": f"https://world.openfoodfacts.org/product/{upc}",
            "notes": f"Weight from Open Food Facts: {quantity}",
            "created_by": "off_monitor",
        }, on_conflict="product_upc,observed_date,source").execute()

        log.info(f"    Recorded new version for {upc}")
        return detail
    except Exception as exc:
        log.warning(f"    Failed to record version for {upc}: {exc}")
        return None


def write_step_summary(discrepancy_list: List[dict], total_checked: int, dry_run: bool):
    """Write a GitHub Actions Step Summary with discrepancy details."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    lines = []
    mode = "DRY RUN" if dry_run else "Live"
    lines.append(f"## Open Food Facts Monitor Results ({mode})\n")
    lines.append(f"**{total_checked}** products checked, "
                 f"**{len(discrepancy_list)}** discrepancies found\n")

    if discrepancy_list:
        lines.append("| # | Product | Brand | FullCarts Size | OFF Size | Delta |")
        lines.append("|---|---------|-------|---------------|----------|-------|")
        for i, d in enumerate(discrepancy_list, 1):
            lines.append(f"| {i} | {d['name'][:40]} | {d['brand'] or '—'} "
                         f"| {d['current_size']} {d['unit']} "
                         f"| {d['off_size']} {d['off_unit']} "
                         f"| {d['delta']:+.1f}% |")
    else:
        lines.append("*No discrepancies found.*\n")

    with open(summary_path, "a") as f:
        f.write("\n".join(lines) + "\n")


def run(upc: Optional[str] = None, dry_run: bool = False):
    """Check all products (or a specific one) against Open Food Facts."""
    sb = get_client()

    if upc:
        result = sb.table("products").select("*").eq("upc", upc).execute()
    else:
        # Get all products, prioritizing real UPCs over REDDIT-* generated ones
        result = sb.table("products").select("*").execute()

    products = result.data or []
    log.info(f"Checking {len(products)} products against Open Food Facts")

    # Sort: real UPCs first, then REDDIT-* ones
    products.sort(key=lambda p: (p["upc"].startswith("REDDIT-"), p["upc"]))

    discrepancies = 0
    discrepancy_list = []
    checked = 0

    for product in products:
        checked += 1
        detail = check_product(sb, product, dry_run=dry_run)
        if detail:
            discrepancies += 1
            discrepancy_list.append(detail)

        # Progress logging every 25 products
        if checked % 25 == 0:
            log.info(f"  Progress: {checked}/{len(products)} checked, {discrepancies} discrepancies")

    log.info(f"\nDone: checked {checked} products, found {discrepancies} discrepancies")
    write_step_summary(discrepancy_list, checked, dry_run)


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Check FullCarts products against Open Food Facts for weight changes"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show discrepancies without writing")
    parser.add_argument("--upc", type=str,
                        help="Check a specific product UPC only")
    args = parser.parse_args()

    run(upc=args.upc, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
