#!/usr/bin/env python3
"""Detect skimpflation by analyzing ingredient position changes across USDA releases.

Two-pass approach for efficiency:
  Pass 1: Fetch (gtin_upc, ingredients_hash) for earliest + latest releases (~small data)
  Pass 2: Fetch full ingredient data ONLY for UPCs where hash changed (~1K rows)

Runs the ingredient parsing and position analysis from ingredient_analysis.py.

Usage:
    python -m pipeline.scripts.skimpflation_analysis
    python -m pipeline.scripts.skimpflation_analysis --brand "CAMPBELL'S"
    python -m pipeline.scripts.skimpflation_analysis --output results.json
"""
import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pipeline.config import USDA_RELEASES
from pipeline.scripts.ingredient_analysis import (
    detect_ingredient_changes,
    parse_ingredients,
    normalize_ingredient,
)

LOG = logging.getLogger("skimpflation_analysis")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

# Suppress httpx info logging (too noisy with 800+ requests)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

_PAGE_SIZE = 1000


def _read_key():
    # type: () -> str
    """Read the Supabase service role key."""
    key = os.environ.get("SUPABASE_KEY", "")
    if key:
        return key
    env_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "web", ".env.local"
    )
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    return line.split("=", 1)[1]
    return ""


def _make_client(key, url):
    # type: (str, str) -> httpx.Client
    return httpx.Client(
        base_url=url,
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
        },
        timeout=60.0,
        http2=True,
    )


def fetch_hashes(client, release_date):
    # type: (httpx.Client, str) -> Dict[str, str]
    """Fetch {gtin_upc: ingredients_hash} for a single release. Paginates through all rows."""
    result = {}  # type: Dict[str, str]
    offset = 0

    while True:
        resp = client.get(
            "/rest/v1/usda_product_history",
            params={
                "select": "gtin_upc,ingredients_hash",
                "release_date": "eq.{}".format(release_date),
                "ingredients_hash": "not.is.null",
                "order": "gtin_upc.asc",
                "limit": str(_PAGE_SIZE),
                "offset": str(offset),
            },
        )
        if resp.status_code != 200:
            LOG.error("Hash query failed (HTTP %d): %s", resp.status_code, resp.text[:200])
            break

        rows = resp.json()
        if not rows:
            break

        for row in rows:
            upc = row.get("gtin_upc", "")
            h = row.get("ingredients_hash", "")
            if upc and h:
                result[upc] = h

        offset += len(rows)
        if len(rows) < _PAGE_SIZE:
            break

        if offset % 50000 == 0:
            LOG.info("    ... fetched %d hashes", offset)

    return result


def fetch_full_data(client, release_date, upcs, brand_filter=None):
    # type: (httpx.Client, str, Set[str], Optional[str]) -> Dict[str, Tuple[str, str, str]]
    """Fetch full ingredient data for specific UPCs in a release.

    Returns {upc: (ingredients, brand_name, description)}.
    Fetches in batches of UPCs to avoid URL length limits.
    """
    result = {}  # type: Dict[str, Tuple[str, str, str]]
    upc_list = sorted(upcs)

    # PostgREST `in` filter has URL length limits. Batch by 50 UPCs at a time.
    batch_size = 50
    for i in range(0, len(upc_list), batch_size):
        batch = upc_list[i:i + batch_size]
        upc_filter = "({})".format(",".join(batch))

        params = {
            "select": "gtin_upc,ingredients,brand_name,description",
            "release_date": "eq.{}".format(release_date),
            "gtin_upc": "in.{}".format(upc_filter),
        }  # type: Dict[str, str]

        if brand_filter:
            params["brand_name"] = "ilike.*{}*".format(brand_filter)

        resp = client.get("/rest/v1/usda_product_history", params=params)
        if resp.status_code != 200:
            LOG.error("Full data query failed (HTTP %d): %s", resp.status_code, resp.text[:200])
            continue

        for row in resp.json():
            upc = row.get("gtin_upc", "")
            ingredients = row.get("ingredients", "")
            brand = row.get("brand_name", "") or ""
            desc = row.get("description", "") or ""
            if upc and ingredients:
                result[upc] = (ingredients, brand, desc)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Detect skimpflation via ingredient position changes across USDA releases"
    )
    parser.add_argument(
        "--brand", type=str, default=None,
        help="Filter by brand name (partial match)",
    )
    parser.add_argument(
        "--output", type=str, default="skimpflation_results.json",
        help="Output JSON file (default: skimpflation_results.json)",
    )
    parser.add_argument(
        "--min-significance", type=int, default=0,
        help="Minimum significance score to include (default: 0 = all changes)",
    )
    args = parser.parse_args()

    key = _read_key()
    url = os.environ.get("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
    if not key:
        LOG.error("No SUPABASE_KEY found. Set env var or check web/.env.local")
        sys.exit(1)

    # Use earliest and latest releases
    earliest_date = USDA_RELEASES[0][0]   # 2022-10-28
    latest_date = USDA_RELEASES[-1][0]    # 2025-12-18

    LOG.info("=" * 60)
    LOG.info("USDA Skimpflation Analysis (Ingredient Position Changes)")
    LOG.info("=" * 60)
    LOG.info("Comparing: %s vs %s", earliest_date, latest_date)
    if args.brand:
        LOG.info("Brand filter: %s", args.brand)
    LOG.info("")

    start = time.time()
    client = _make_client(key, url)

    # ── Pass 1: Fetch ingredient hashes ──────────────────────────────────────
    LOG.info("Pass 1: Fetching ingredient hashes...")

    LOG.info("  Loading hashes for %s...", earliest_date)
    t0 = time.time()
    early_hashes = fetch_hashes(client, earliest_date)
    LOG.info("  Loaded %d hashes in %.1fs", len(early_hashes), time.time() - t0)

    LOG.info("  Loading hashes for %s...", latest_date)
    t0 = time.time()
    late_hashes = fetch_hashes(client, latest_date)
    LOG.info("  Loaded %d hashes in %.1fs", len(late_hashes), time.time() - t0)

    # Find UPCs present in both releases with different hashes
    common_upcs = set(early_hashes.keys()) & set(late_hashes.keys())
    changed_upcs = set()  # type: Set[str]
    for upc in common_upcs:
        if early_hashes[upc] != late_hashes[upc]:
            changed_upcs.add(upc)

    LOG.info("")
    LOG.info("  UPCs in earliest release:  %d", len(early_hashes))
    LOG.info("  UPCs in latest release:    %d", len(late_hashes))
    LOG.info("  UPCs in both releases:     %d", len(common_upcs))
    LOG.info("  UPCs with changed ingredients: %d", len(changed_upcs))
    LOG.info("")

    if not changed_upcs:
        LOG.info("No ingredient changes detected. Exiting.")
        client.close()
        return

    # ── Pass 2: Fetch full ingredient data for changed UPCs ──────────────────
    LOG.info("Pass 2: Fetching full ingredient data for %d changed UPCs...", len(changed_upcs))

    LOG.info("  Loading early ingredients...")
    t0 = time.time()
    early_data = fetch_full_data(client, earliest_date, changed_upcs, args.brand)
    LOG.info("  Loaded %d products in %.1fs", len(early_data), time.time() - t0)

    LOG.info("  Loading late ingredients...")
    t0 = time.time()
    late_data = fetch_full_data(client, latest_date, changed_upcs, args.brand)
    LOG.info("  Loaded %d products in %.1fs", len(late_data), time.time() - t0)

    client.close()

    # ── Analysis: Detect position changes ────────────────────────────────────
    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("Analyzing ingredient position changes...")
    LOG.info("=" * 60)

    # Format data for detect_ingredient_changes()
    all_releases = [
        (earliest_date, early_data),
        (latest_date, late_data),
    ]  # type: List[Tuple[str, Dict[str, Tuple[str, str, str]]]]

    changes = detect_ingredient_changes(all_releases)

    # Filter by significance
    if args.min_significance > 0:
        changes = [c for c in changes if c["significance"] >= args.min_significance]

    elapsed = time.time() - start

    # ── Output ───────────────────────────────────────────────────────────────
    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("SKIMPFLATION ANALYSIS RESULTS")
    LOG.info("=" * 60)
    LOG.info("Total time: %.1f minutes", elapsed / 60)
    LOG.info("UPCs with ingredient changes: %d", len(changed_upcs))
    LOG.info("UPCs with position changes: %d", len(changes))
    LOG.info("")

    if changes:
        # Categorize results
        high_sig = [c for c in changes if c["significance"] >= 10]
        med_sig = [c for c in changes if 5 <= c["significance"] < 10]
        low_sig = [c for c in changes if 0 < c["significance"] < 5]
        LOG.info("Significance breakdown:")
        LOG.info("  HIGH (>=10): %d products", len(high_sig))
        LOG.info("  MEDIUM (5-9): %d products", len(med_sig))
        LOG.info("  LOW (1-4): %d products", len(low_sig))
        LOG.info("")

        LOG.info("Top 50 changes (by significance score):")
        LOG.info("-" * 60)
        for i, c in enumerate(changes[:50]):
            LOG.info("")
            LOG.info(
                "#%d  [score=%d] %s",
                i + 1, c["significance"],
                c.get("brand", "Unknown"),
            )
            desc = c.get("description", "")
            if desc:
                LOG.info("    Product: %s", desc[:80])
            LOG.info(
                "    UPC: %s | Releases: %s -> %s",
                c["upc"], c["earliest_date"], c["latest_date"],
            )
            LOG.info("    EARLY top-5: %s", " | ".join(c["early_top5"]))
            LOG.info("    LATE  top-5: %s", " | ".join(c["late_top5"]))
            for pc in c["position_changes"]:
                if pc.get("removed"):
                    LOG.info(
                        "    >> %s: position #%d -> REMOVED",
                        pc["ingredient"], pc["old_position"],
                    )
                elif pc.get("drop") and pc["drop"] > 0:
                    LOG.info(
                        "    >> %s: #%d -> #%d (dropped %d)",
                        pc["ingredient"], pc["old_position"],
                        pc["new_position"], pc["drop"],
                    )
            for nt in c.get("new_at_top", []):
                LOG.info(
                    "    ++ %s: NEW at position #%d",
                    nt["ingredient"], nt["position"],
                )

    # Save JSON
    output_path = os.path.join(os.path.dirname(__file__), "..", "..", args.output)
    with open(output_path, "w") as f:
        json.dump({
            "analysis_date": time.strftime("%Y-%m-%d"),
            "earliest_release": earliest_date,
            "latest_release": latest_date,
            "brand_filter": args.brand,
            "total_upcs_compared": len(common_upcs),
            "upcs_with_ingredient_changes": len(changed_upcs),
            "upcs_with_position_changes": len(changes),
            "significance_breakdown": {
                "high_10_plus": len([c for c in changes if c["significance"] >= 10]),
                "medium_5_to_9": len([c for c in changes if 5 <= c["significance"] < 10]),
                "low_1_to_4": len([c for c in changes if 0 < c["significance"] < 5]),
            },
            "changes": changes[:500],
        }, f, indent=2)
    LOG.info("")
    LOG.info("Full results saved to: %s", output_path)


if __name__ == "__main__":
    main()
