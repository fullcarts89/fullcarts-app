#!/usr/bin/env python3
"""Analyze ingredient list changes across USDA releases to detect skimpflation.

FDA requires ingredients to be listed in descending order by weight.
If a key ingredient drops in position between releases, it signals
that less of that ingredient is being used — a form of skimpflation.

Approach:
  1. Download all 7 USDA release ZIPs (or query usda_product_history table)
  2. Extract {UPC: ingredients} from branded_food.csv in each
  3. For UPCs appearing in 2+ releases with DIFFERENT ingredient lists,
     parse ingredient order and detect position changes
  4. Flag cases where a top-3 ingredient drops 2+ positions

Usage:
    # From database (preferred — uses usda_product_history table):
    python -m pipeline.scripts.ingredient_analysis --from-db
    python -m pipeline.scripts.ingredient_analysis --from-db --brand "CAMPBELL'S"

    # From ZIP files (downloads ~10GB):
    python -m pipeline.scripts.ingredient_analysis
    python -m pipeline.scripts.ingredient_analysis --brand "CAMPBELL'S"
"""
import argparse
import csv
import hashlib
import io
import json
import logging
import os
import re
import sys
import tempfile
import time
import zipfile
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx
import requests

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pipeline.config import USDA_FDC_BASE, USDA_RELEASES, USER_AGENT

LOG = logging.getLogger("ingredient_analysis")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)


# ── Ingredient Parsing ──────────────────────────────────────────────────────


def parse_ingredients(raw: str) -> List[str]:
    """Parse an FDA ingredient string into an ordered list of top-level ingredients.

    Handles nested parenthetical sub-ingredients like:
        "WATER, POTATOES (DEHYDRATED POTATO FLAKES, ...), CREAM"
    Returns: ["WATER", "POTATOES", "CREAM"]

    Only returns top-level ingredients (not sub-ingredients inside parentheses).
    """
    if not raw or not raw.strip():
        return []

    # Normalize
    text = raw.upper().strip()
    # Remove trailing period
    text = text.rstrip(".")

    # Remove content inside parentheses/brackets for top-level parsing
    # But preserve nested parens by doing iterative removal
    cleaned = text
    max_iters = 10
    for _ in range(max_iters):
        # Remove innermost parenthetical groups
        new = re.sub(r'\([^()]*\)', '', cleaned)
        new = re.sub(r'\[[^\[\]]*\]', '', new)
        if new == cleaned:
            break
        cleaned = new

    # Split on commas
    parts = [p.strip() for p in cleaned.split(",")]

    # Clean up each ingredient
    result = []
    for part in parts:
        # Remove "CONTAINS 2% OR LESS OF:" type prefixes
        part = re.sub(
            r'^CONTAINS?\s+\d+%?\s+OR\s+LESS\s+(OF:?\s*)?',
            '',
            part,
            flags=re.IGNORECASE
        ).strip()
        # Remove "LESS THAN 2% OF:" type prefixes
        part = re.sub(
            r'^LESS\s+THAN\s+\d+%?\s+(OF:?\s*)?',
            '',
            part,
            flags=re.IGNORECASE
        ).strip()
        # Skip empty parts and pure punctuation
        if part and len(part) > 1 and not part.startswith("*"):
            result.append(part)

    return result


def normalize_ingredient(name: str) -> str:
    """Normalize an ingredient name for comparison.

    "ENRICHED WHEAT FLOUR" and "ENRICHED BLEACHED WHEAT FLOUR"
    should probably be treated as different ingredients.
    But "SUGAR" and "SUGAR." should match.
    """
    s = name.upper().strip()
    s = re.sub(r'[^\w\s]', '', s)  # Remove punctuation
    s = re.sub(r'\s+', ' ', s)     # Collapse whitespace
    return s.strip()


# ── USDA ZIP Processing ─────────────────────────────────────────────────────


def download_release(release_date: str, filename: str, cache_dir: str) -> str:
    """Download a USDA release ZIP if not cached. Returns local path."""
    local_path = os.path.join(cache_dir, filename)
    if os.path.exists(local_path):
        LOG.info("  Cached: %s", local_path)
        return local_path

    url = f"{USDA_FDC_BASE}{filename}"
    LOG.info("  Downloading %s ...", url)
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=300)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(local_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            f.write(chunk)
            downloaded += len(chunk)
            if total > 0:
                pct = 100 * downloaded / total
                if downloaded % (50 * 1024 * 1024) < 1024 * 1024:
                    LOG.info("    ... %.0f%% (%d MB)", pct, downloaded // (1024 * 1024))

    LOG.info("  Downloaded %.1f MB", os.path.getsize(local_path) / (1024 * 1024))
    return local_path


def extract_ingredients_from_zip(
    zip_path: str, brand_filter: Optional[str] = None
) -> Dict[str, Tuple[str, str, str]]:
    """Extract {UPC: (ingredients, brand_name, description)} from a USDA ZIP.

    Only includes products that have non-empty ingredient lists.
    """
    result = {}  # type: Dict[str, Tuple[str, str, str]]

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Find branded_food.csv
        bf_name = next(
            (n for n in zf.namelist() if n.endswith("branded_food.csv")),
            None
        )
        if not bf_name:
            LOG.warning("branded_food.csv not found in %s", zip_path)
            return result

        with zf.open(bf_name) as bf_file:
            reader = csv.DictReader(io.TextIOWrapper(bf_file, encoding="utf-8"))
            for row in reader:
                upc = (row.get("gtin_upc") or "").strip()
                ingredients = (row.get("ingredients") or "").strip()
                brand = (row.get("brand_name") or "").strip()
                desc = (row.get("description") or "").strip()

                if not upc or not ingredients:
                    continue

                if brand_filter and brand_filter.upper() not in brand.upper():
                    continue

                result[upc] = (ingredients, brand, desc)

    return result


# ── Analysis ─────────────────────────────────────────────────────────────────


def detect_ingredient_changes(
    releases: List[Tuple[str, Dict[str, Tuple[str, str, str]]]]
) -> List[Dict[str, Any]]:
    """Compare ingredient lists across releases for the same UPC.

    Returns a list of detected changes, sorted by significance.
    """
    changes = []  # type: List[Dict[str, Any]]

    # Build UPC → {release_date: (ingredients, brand, desc)}
    upc_history = defaultdict(dict)  # type: Dict[str, Dict[str, Tuple[str, str, str]]]
    for release_date, upc_map in releases:
        for upc, data in upc_map.items():
            upc_history[upc][release_date] = data

    LOG.info("Analyzing %d UPCs with ingredient data across releases...", len(upc_history))

    # Filter to UPCs that appear in 2+ releases
    multi_release_upcs = {
        upc: history
        for upc, history in upc_history.items()
        if len(history) >= 2
    }
    LOG.info("  %d UPCs appear in 2+ releases", len(multi_release_upcs))

    # For each UPC, compare earliest vs latest ingredient list
    ingredient_changed_count = 0
    for upc, history in multi_release_upcs.items():
        sorted_dates = sorted(history.keys())
        earliest_date = sorted_dates[0]
        latest_date = sorted_dates[-1]

        earliest_raw, brand_e, desc_e = history[earliest_date]
        latest_raw, brand_l, desc_l = history[latest_date]

        # Quick hash check — skip if ingredients are identical
        if hashlib.md5(earliest_raw.encode()).hexdigest() == \
           hashlib.md5(latest_raw.encode()).hexdigest():
            continue

        ingredient_changed_count += 1

        # Parse into ordered ingredient lists
        early_parsed = parse_ingredients(earliest_raw)
        late_parsed = parse_ingredients(latest_raw)

        if not early_parsed or not late_parsed:
            continue

        # Normalize for comparison
        early_norm = [normalize_ingredient(i) for i in early_parsed]
        late_norm = [normalize_ingredient(i) for i in late_parsed]

        # Find position changes for top ingredients
        # Focus on top 5 ingredients from earliest release
        position_changes = []
        for pos, ingredient in enumerate(early_norm[:5]):
            # Find this ingredient in the latest list
            try:
                new_pos = late_norm.index(ingredient)
                drop = new_pos - pos
                if drop > 0:  # Dropped (moved later in list = less of it)
                    position_changes.append({
                        "ingredient": early_parsed[pos],
                        "old_position": pos + 1,
                        "new_position": new_pos + 1,
                        "drop": drop,
                    })
            except ValueError:
                # Ingredient was removed entirely
                position_changes.append({
                    "ingredient": early_parsed[pos],
                    "old_position": pos + 1,
                    "new_position": None,
                    "drop": None,
                    "removed": True,
                })

        # Also detect new ingredients that appeared at the top
        new_at_top = []
        for pos, ingredient in enumerate(late_norm[:3]):
            if ingredient not in early_norm[:10]:
                new_at_top.append({
                    "ingredient": late_parsed[pos],
                    "position": pos + 1,
                })

        # Score significance
        # A top-3 ingredient dropping 2+ positions is highly significant
        significance = 0
        for pc in position_changes:
            if pc.get("removed"):
                if pc["old_position"] <= 3:
                    significance += 10
                else:
                    significance += 3
            elif pc["drop"] and pc["drop"] >= 2:
                if pc["old_position"] <= 3:
                    significance += 5 * pc["drop"]
                else:
                    significance += pc["drop"]

        if significance > 0 or position_changes:
            changes.append({
                "upc": upc,
                "brand": brand_l or brand_e,
                "description": desc_l or desc_e,
                "earliest_date": earliest_date,
                "latest_date": latest_date,
                "releases_seen": len(history),
                "early_top5": early_parsed[:5],
                "late_top5": late_parsed[:5],
                "early_ingredients_raw": earliest_raw[:500],
                "late_ingredients_raw": latest_raw[:500],
                "position_changes": position_changes,
                "new_at_top": new_at_top,
                "significance": significance,
            })

    LOG.info("  %d UPCs had ingredient changes", ingredient_changed_count)
    LOG.info("  %d UPCs had position changes in top ingredients", len(changes))

    # Sort by significance (most significant first)
    changes.sort(key=lambda x: x["significance"], reverse=True)
    return changes


# ── Database Mode ─────────────────────────────────────────────────────────────


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


def load_from_db(brand_filter=None):
    # type: (Optional[str]) -> List[Tuple[str, Dict[str, Tuple[str, str, str]]]]
    """Load ingredient data from usda_product_history table.

    Returns list of (release_date, {upc: (ingredients, brand, desc)}) tuples.
    Uses pagination to handle PostgREST's 1000-row limit.
    """
    key = _read_key()
    url = os.environ.get("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")

    if not key:
        LOG.error("No SUPABASE_KEY found. Set env var or check web/.env.local")
        sys.exit(1)

    client = httpx.Client(
        base_url=url,
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
        },
        timeout=60.0,
        http2=True,
    )

    # Get distinct release dates
    resp = client.get(
        "/rest/v1/usda_product_history",
        params={
            "select": "release_date",
            "order": "release_date.asc",
            "limit": "20",
        },
        headers={"Prefer": "return=representation"},
    )
    # Deduplicate release dates from sample
    release_dates = sorted(set(
        r["release_date"] for r in resp.json() if r.get("release_date")
    ))
    # Better: query known releases from config
    release_dates = [d for d, _f in USDA_RELEASES]
    LOG.info("Loading from DB for %d releases: %s", len(release_dates), release_dates)

    all_releases = []  # type: List[Tuple[str, Dict[str, Tuple[str, str, str]]]]
    _PAGE_SIZE = 1000

    for i, rd in enumerate(release_dates):
        LOG.info("[%d/%d] Loading release %s from DB...", i + 1, len(release_dates), rd)
        upc_map = {}  # type: Dict[str, Tuple[str, str, str]]
        offset = 0

        while True:
            params = {
                "select": "gtin_upc,ingredients,brand_name,description",
                "release_date": "eq.{}".format(rd),
                "ingredients": "not.is.null",
                "order": "gtin_upc.asc",
                "limit": str(_PAGE_SIZE),
                "offset": str(offset),
            }  # type: Dict[str, str]
            if brand_filter:
                params["brand_name"] = "ilike.*{}*".format(brand_filter)

            resp = client.get("/rest/v1/usda_product_history", params=params)
            if resp.status_code != 200:
                LOG.error("DB query failed (HTTP %d): %s", resp.status_code, resp.text[:200])
                break

            rows = resp.json()
            if not rows:
                break

            for row in rows:
                upc = row.get("gtin_upc", "")
                ingredients = row.get("ingredients", "")
                brand = row.get("brand_name", "") or ""
                desc = row.get("description", "") or ""
                if upc and ingredients:
                    upc_map[upc] = (ingredients, brand, desc)

            offset += _PAGE_SIZE
            if len(rows) < _PAGE_SIZE:
                break

            if offset % 50000 == 0:
                LOG.info("    ... loaded %d products so far", offset)

        LOG.info("  Loaded %d products with ingredients from %s", len(upc_map), rd)
        all_releases.append((rd, upc_map))

    client.close()
    return all_releases


# ── Main ─────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="USDA Ingredient Change Analysis")
    parser.add_argument("--from-db", action="store_true",
                        help="Load from usda_product_history table (preferred)")
    parser.add_argument("--dry-run", action="store_true", help="Parse only, skip downloads")
    parser.add_argument("--brand", type=str, default=None, help="Filter by brand name (partial match)")
    parser.add_argument("--cache-dir", type=str, default=None, help="Directory for cached ZIPs")
    parser.add_argument("--output", type=str, default="ingredient_changes.json", help="Output file")
    parser.add_argument("--limit", type=int, default=None, help="Limit releases to process")
    args = parser.parse_args()

    LOG.info("=" * 60)
    LOG.info("USDA Ingredient Skimpflation Analysis")
    LOG.info("=" * 60)
    if args.brand:
        LOG.info("Brand filter: %s", args.brand)
    LOG.info("")

    total_start = time.time()

    if args.from_db:
        # Load from usda_product_history table
        LOG.info("Mode: Database (usda_product_history)")
        LOG.info("")
        all_releases = load_from_db(brand_filter=args.brand)
    else:
        # Download ZIPs and extract
        cache_dir = args.cache_dir or os.path.join(tempfile.gettempdir(), "usda_ingredient_cache")
        os.makedirs(cache_dir, exist_ok=True)

        releases_to_process = USDA_RELEASES
        if args.limit:
            releases_to_process = releases_to_process[:args.limit]

        LOG.info("Mode: ZIP download")
        LOG.info("Releases: %d", len(releases_to_process))
        LOG.info("Cache dir: %s", cache_dir)
        LOG.info("")

        all_releases = []  # type: List[Tuple[str, Dict[str, Tuple[str, str, str]]]]

        for i, (release_date, filename) in enumerate(releases_to_process):
            LOG.info("[%d/%d] Processing release %s", i + 1, len(releases_to_process), release_date)

            zip_path = download_release(release_date, filename, cache_dir)
            upc_map = extract_ingredients_from_zip(zip_path, brand_filter=args.brand)

            LOG.info("  Extracted %d products with ingredients", len(upc_map))
            all_releases.append((release_date, upc_map))

    # Step 2: Analyze changes
    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("Analyzing ingredient changes across %d releases...", len(all_releases))
    LOG.info("=" * 60)

    changes = detect_ingredient_changes(all_releases)

    # Step 3: Output results
    elapsed = time.time() - total_start

    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("RESULTS")
    LOG.info("=" * 60)
    LOG.info("Total time: %.1f minutes", elapsed / 60)
    LOG.info("Significant ingredient changes found: %d", len(changes))
    LOG.info("")

    if changes:
        # Show top 20 most significant
        LOG.info("Top changes (by significance score):")
        LOG.info("-" * 60)
        for i, c in enumerate(changes[:30]):
            LOG.info("")
            LOG.info("#%d  [score=%d] %s — %s", i + 1, c["significance"], c["brand"], c["description"][:60])
            LOG.info("    UPC: %s | Releases: %s → %s (%d total)",
                     c["upc"], c["earliest_date"], c["latest_date"], c["releases_seen"])
            LOG.info("    EARLY top-5: %s", " | ".join(c["early_top5"]))
            LOG.info("    LATE  top-5: %s", " | ".join(c["late_top5"]))
            for pc in c["position_changes"]:
                if pc.get("removed"):
                    LOG.info("    ⚠️  %s: position #%d → REMOVED",
                             pc["ingredient"], pc["old_position"])
                elif pc["drop"] and pc["drop"] > 0:
                    LOG.info("    📉 %s: position #%d → #%d (dropped %d)",
                             pc["ingredient"], pc["old_position"], pc["new_position"], pc["drop"])
            for nt in c.get("new_at_top", []):
                LOG.info("    🆕 %s: NEW at position #%d", nt["ingredient"], nt["position"])

    # Save full results to JSON
    output_path = os.path.join(os.path.dirname(__file__), "..", "..", args.output)
    with open(output_path, "w") as f:
        json.dump({
            "analysis_date": time.strftime("%Y-%m-%d"),
            "releases_analyzed": [r[0] for r in all_releases],
            "brand_filter": args.brand,
            "total_changes": len(changes),
            "changes": changes[:200],  # Top 200
        }, f, indent=2)
    LOG.info("")
    LOG.info("Full results saved to: %s", output_path)


if __name__ == "__main__":
    main()
