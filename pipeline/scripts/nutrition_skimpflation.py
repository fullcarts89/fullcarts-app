#!/usr/bin/env python3
"""Detect skimpflation via nutrition value changes across USDA releases.

Queries usda_product_history directly for products where key nutrient
values changed significantly between the earliest and latest releases.

Stronger signal than ingredient position analysis because nutrition
values are quantitative (not text-based).

Usage:
    python -m pipeline.scripts.nutrition_skimpflation
    python -m pipeline.scripts.nutrition_skimpflation --min-drop 10
"""
import argparse
import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

LOG = logging.getLogger("nutrition_skimpflation")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

RELEASES = [
    "2022-10-28", "2023-04-20", "2023-10-26", "2024-04-18",
    "2024-10-31", "2025-04-24", "2025-12-18",
]

# Nutrients where a DROP suggests skimpflation (less of the good stuff)
DROP_SIGNALS = ["protein_g", "fiber_g", "calcium_mg"]

# Nutrients where an INCREASE suggests skimpflation (more cheap filler)
RISE_SIGNALS = ["sugars_g", "sodium_mg"]

# All nutrient columns
ALL_NUTRIENTS = [
    "calories_kcal", "protein_g", "total_fat_g", "saturated_fat_g",
    "carbs_g", "fiber_g", "sugars_g", "calcium_mg", "sodium_mg",
    "cholesterol_mg",
]

PAGE_SIZE = 1000


def _read_key():
    # type: () -> str
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


def fetch_release(client, release_date):
    # type: (httpx.Client, str) -> Dict[str, Dict[str, Any]]
    """Fetch all products with nutrition data for a release.

    Returns {upc: {col: value, ...}, ...}
    """
    fields = ",".join(
        ["gtin_upc", "brand_name", "description"] + ALL_NUTRIENTS
    )
    result = {}  # type: Dict[str, Dict[str, Any]]
    offset = 0

    while True:
        resp = client.get("/rest/v1/usda_product_history", params={
            "select": fields,
            "release_date": "eq.{}".format(release_date),
            "protein_g": "not.is.null",
            "order": "gtin_upc.asc",
            "limit": str(PAGE_SIZE),
            "offset": str(offset),
        })
        if resp.status_code != 200:
            LOG.error("Error at offset %d: %d", offset, resp.status_code)
            break
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            upc = r.get("gtin_upc", "")
            if upc:
                result[upc] = r
        offset += len(rows)
        if len(rows) < PAGE_SIZE:
            break
        if offset % 100000 == 0:
            LOG.info("  ... %d rows", offset)

    return result


def analyze_changes(early, late, min_drop_pct):
    # type: (Dict[str, Dict], Dict[str, Dict], float) -> List[Dict[str, Any]]
    """Compare nutrition values between releases.

    Returns list of products with significant changes, sorted by impact.
    """
    common_upcs = set(early.keys()) & set(late.keys())
    LOG.info("Common UPCs with nutrition data: %d", len(common_upcs))

    changes = []  # type: List[Dict[str, Any]]

    for upc in common_upcs:
        e = early[upc]
        l = late[upc]

        nutrient_changes = []  # type: List[Dict[str, Any]]
        skimpflation_score = 0.0

        for col in ALL_NUTRIENTS:
            e_val = e.get(col)
            l_val = l.get(col)

            if e_val is None or l_val is None:
                continue

            try:
                e_val = float(e_val)
                l_val = float(l_val)
            except (ValueError, TypeError):
                continue

            if e_val == 0:
                continue

            pct_change = ((l_val - e_val) / e_val) * 100

            # Skip tiny changes (rounding noise)
            if abs(pct_change) < min_drop_pct:
                continue

            change = {
                "nutrient": col,
                "early_value": round(e_val, 2),
                "late_value": round(l_val, 2),
                "pct_change": round(pct_change, 1),
            }
            nutrient_changes.append(change)

            # Score: drops in quality nutrients = positive score
            if col in DROP_SIGNALS and pct_change < 0:
                skimpflation_score += abs(pct_change)
            elif col in RISE_SIGNALS and pct_change > 0:
                skimpflation_score += pct_change

        if nutrient_changes and skimpflation_score > 0:
            changes.append({
                "upc": upc,
                "brand": e.get("brand_name", "") or "",
                "description": e.get("description", "") or "",
                "score": round(skimpflation_score, 1),
                "changes": nutrient_changes,
            })

    changes.sort(key=lambda x: -x["score"])
    return changes


def main():
    parser = argparse.ArgumentParser(
        description="Detect skimpflation via nutrition changes"
    )
    parser.add_argument(
        "--min-drop", type=float, default=5.0,
        help="Minimum percent change to flag (default: 5%%)",
    )
    parser.add_argument(
        "--top", type=int, default=100,
        help="Show top N results (default: 100)",
    )
    parser.add_argument(
        "--early", type=str, default=None,
        help="Early release date (default: auto-detect earliest with data)",
    )
    parser.add_argument(
        "--late", type=str, default=None,
        help="Late release date (default: auto-detect latest with data)",
    )
    parser.add_argument(
        "--output", type=str, default="nutrition_skimpflation.json",
        help="Output file (default: nutrition_skimpflation.json)",
    )
    args = parser.parse_args()

    key = _read_key()
    url = os.environ.get(
        "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
    )
    if not key:
        LOG.error("No SUPABASE_KEY found")
        sys.exit(1)

    client = httpx.Client(
        base_url=url,
        headers={"apikey": key, "Authorization": "Bearer {}".format(key)},
        timeout=60.0,
        http2=True,
    )

    # Auto-detect which releases have nutrition data
    if args.early and args.late:
        earliest = args.early
        latest = args.late
    else:
        LOG.info("Detecting releases with nutrition data ...")
        available = []  # type: List[str]
        for rd in RELEASES:
            resp = client.get("/rest/v1/usda_product_history", params={
                "select": "protein_g",
                "release_date": "eq.{}".format(rd),
                "protein_g": "not.is.null",
                "limit": "1",
            })
            if resp.status_code == 200 and resp.json():
                available.append(rd)
                LOG.info("  %s: has nutrition data", rd)
            else:
                LOG.info("  %s: no nutrition data yet", rd)
        if len(available) < 2:
            LOG.error("Need at least 2 releases with nutrition data")
            sys.exit(1)
        earliest = args.early or available[0]
        latest = args.late or available[-1]

    LOG.info("Comparing %s vs %s", earliest, latest)

    LOG.info("Fetching %s ...", earliest)
    t0 = time.time()
    early = fetch_release(client, earliest)
    LOG.info("  %d products in %.0fs", len(early), time.time() - t0)

    LOG.info("Fetching %s ...", latest)
    t0 = time.time()
    late = fetch_release(client, latest)
    LOG.info("  %d products in %.0fs", len(late), time.time() - t0)

    client.close()

    LOG.info("Analyzing changes (min %.0f%% change) ...", args.min_drop)
    changes = analyze_changes(early, late, args.min_drop)
    LOG.info("Products with skimpflation signals: %d", len(changes))

    # Save full results
    output = {
        "earliest_release": earliest,
        "latest_release": latest,
        "min_drop_pct": args.min_drop,
        "total_common_upcs": len(set(early.keys()) & set(late.keys())),
        "total_flagged": len(changes),
        "changes": changes,
    }

    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)
    LOG.info("Saved to %s", args.output)

    # Print top results
    print()
    print("=" * 80)
    print("TOP {} SKIMPFLATION SIGNALS (nutrition-based)".format(
        min(args.top, len(changes))
    ))
    print("Comparing {} vs {} | Min {}% change".format(
        earliest, latest, args.min_drop
    ))
    print("=" * 80)
    print()

    for i, c in enumerate(changes[:args.top]):
        print("#{:<4d} {} — {}".format(
            i + 1, c["brand"], c["description"][:65]
        ))
        print("      Score: {:.0f}".format(c["score"]))
        for ch in c["changes"]:
            direction = "↓" if ch["pct_change"] < 0 else "↑"
            print("      {} {}: {} → {} ({:+.1f}%)".format(
                direction, ch["nutrient"],
                ch["early_value"], ch["late_value"], ch["pct_change"]
            ))
        print()


if __name__ == "__main__":
    main()
