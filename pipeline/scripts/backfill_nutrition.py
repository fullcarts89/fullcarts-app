#!/usr/bin/env python3
"""Backfill nutrition columns on usda_product_history from USDA ZIPs.

For each release ZIP, reads food_nutrient.csv, filters to key nutrients,
pivots by fdc_id, maps fdc_id -> gtin_upc via branded_food.csv, and
PATCHes existing rows in usda_product_history.

Usage:
    python -m pipeline.scripts.backfill_nutrition
    python -m pipeline.scripts.backfill_nutrition --release 2025-12-18
    python -m pipeline.scripts.backfill_nutrition --dry-run
"""
import argparse
import csv
import io
import logging
import os
import sys
import tempfile
import time
import zipfile
from typing import Any, Dict, List, Optional, Tuple

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pipeline.config import USDA_FDC_BASE, USDA_RELEASES, USER_AGENT
from pipeline.scripts.build_usda_history import download_zip, try_download_full_csv

LOG = logging.getLogger("backfill_nutrition")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

# Nutrient IDs -> column names (values are per 100g basis in USDA data)
KEY_NUTRIENTS = {
    "1003": "protein_g",
    "1004": "total_fat_g",
    "1005": "carbs_g",
    "1008": "calories_kcal",
    "1079": "fiber_g",
    "1087": "calcium_mg",
    "1093": "sodium_mg",
    "2000": "sugars_g",
    "1258": "saturated_fat_g",
    "1253": "cholesterol_mg",
}

_BATCH_SIZE = 500
_RECYCLE_EVERY = 4000  # batches


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


def _make_client(key, url):
    # type: (str, str) -> httpx.Client
    return httpx.Client(
        base_url=url,
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates",
        },
        timeout=60.0,
        http2=True,
    )


def extract_fdc_to_upc(zip_path):
    # type: (str) -> Tuple[Dict[str, str], Dict[str, str]]
    """Build fdc_id -> gtin_upc and upc -> fdc_id mappings from branded_food.csv."""
    fdc_to_upc = {}  # type: Dict[str, str]
    upc_to_fdc = {}  # type: Dict[str, str]
    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_name = next(
            (n for n in zf.namelist() if n.endswith("branded_food.csv")), None
        )
        if not csv_name:
            return fdc_to_upc, upc_to_fdc
        with zf.open(csv_name) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text)
            for row in reader:
                fdc_id = (row.get("fdc_id") or "").strip()
                upc = (row.get("gtin_upc") or "").strip()
                if fdc_id and upc:
                    if fdc_id not in fdc_to_upc:
                        fdc_to_upc[fdc_id] = upc
                    if upc not in upc_to_fdc:
                        upc_to_fdc[upc] = fdc_id
    LOG.info("  fdc_id -> UPC mapping: %d entries", len(fdc_to_upc))
    return fdc_to_upc, upc_to_fdc


def extract_nutrients(zip_path, fdc_to_upc, upc_to_fdc):
    # type: (str, Dict[str, str], Dict[str, str]) -> Dict[str, Tuple[Dict[str, float], str]]
    """Extract key nutrients from food_nutrient.csv, keyed by UPC.

    Returns {upc: ({column_name: amount, ...}, fdc_id), ...}
    """
    result = {}  # type: Dict[str, Tuple[Dict[str, float], str]]
    branded_fdc_ids = set(fdc_to_upc.keys())

    with zipfile.ZipFile(zip_path, "r") as zf:
        fn_name = next(
            (n for n in zf.namelist() if n.endswith("food_nutrient.csv")), None
        )
        if not fn_name:
            LOG.warning("  food_nutrient.csv not found in ZIP")
            return result

        LOG.info("  Reading food_nutrient.csv ...")
        count = 0
        matched = 0
        with zf.open(fn_name) as raw:
            text = io.TextIOWrapper(raw, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text)
            for row in reader:
                count += 1
                fdc_id = (row.get("fdc_id") or "").strip()
                nutrient_id = (row.get("nutrient_id") or "").strip()

                if fdc_id not in branded_fdc_ids:
                    continue
                if nutrient_id not in KEY_NUTRIENTS:
                    continue

                upc = fdc_to_upc[fdc_id]
                amount_str = (row.get("amount") or "").strip()
                if not amount_str:
                    continue

                try:
                    amount = float(amount_str)
                except ValueError:
                    continue

                col = KEY_NUTRIENTS[nutrient_id]
                if upc not in result:
                    result[upc] = ({}, upc_to_fdc.get(upc, fdc_id))
                # Keep first value per UPC per nutrient (matches dedup logic)
                if col not in result[upc][0]:
                    result[upc][0][col] = amount
                    matched += 1

                if count % 5000000 == 0:
                    LOG.info("    ... scanned %dM rows, %d matched",
                             count // 1000000, matched)

    LOG.info("  Scanned %dM nutrient rows, %d UPCs with data",
             count // 1000000, len(result))
    return result


def upload_nutrients(key, url, release_date, nutrients, dry_run=False):
    # type: (str, str, str, Dict[str, Dict[str, float]], bool) -> Tuple[int, int]
    """UPSERT nutrition data into usda_product_history rows."""
    if dry_run:
        LOG.info("  DRY RUN: would update %d rows", len(nutrients))
        return len(nutrients), 0

    client = _make_client(key, url)
    uploaded = 0
    errors = 0
    batch = []  # type: List[Dict[str, Any]]
    batch_count = 0

    # All nutrient column names — every row must have the same keys
    all_cols = sorted(KEY_NUTRIENTS.values())

    for upc, (cols, fdc_id) in nutrients.items():
        row = {
            "gtin_upc": upc,
            "fdc_id": fdc_id,
            "release_date": release_date,
        }
        # Ensure every nutrient column is present (None for missing)
        for col in all_cols:
            row[col] = cols.get(col)
        batch.append(row)

        if len(batch) >= _BATCH_SIZE:
            resp = client.post(
                "/rest/v1/usda_product_history",
                json=batch,
                params={"on_conflict": "gtin_upc,release_date"},
            )
            if resp.status_code in (200, 201):
                uploaded += len(batch)
            else:
                LOG.error("  Upload error (HTTP %d): %s",
                          resp.status_code, resp.text[:200])
                errors += len(batch)

            batch = []
            batch_count += 1

            if uploaded % 50000 == 0 and uploaded > 0:
                LOG.info("    ... updated %d rows", uploaded)

            if batch_count % _RECYCLE_EVERY == 0:
                LOG.info("    Recycling HTTP connection ...")
                client.close()
                client = _make_client(key, url)

    # Remaining batch
    if batch:
        resp = client.post(
            "/rest/v1/usda_product_history",
            json=batch,
            params={"on_conflict": "gtin_upc,release_date"},
        )
        if resp.status_code in (200, 201):
            uploaded += len(batch)
        else:
            errors += len(batch)

    client.close()
    return uploaded, errors


def process_release(release_date, filename, cache_dir, key, url, dry_run):
    # type: (str, str, str, str, str, bool) -> Tuple[int, int]
    """Process one release: extract nutrients and update DB rows."""
    LOG.info("Processing release %s ...", release_date)

    zip_path = download_zip(release_date, filename, cache_dir)
    if zip_path is None:
        return 0, 0

    # Build fdc_id -> UPC mapping
    fdc_to_upc, upc_to_fdc = extract_fdc_to_upc(zip_path)
    if not fdc_to_upc:
        LOG.error("  No fdc_id -> UPC mapping found")
        return 0, 0

    # Extract nutrients
    nutrients = extract_nutrients(zip_path, fdc_to_upc, upc_to_fdc)
    if not nutrients:
        LOG.warning("  No nutrient data found")
        return 0, 0

    # Upload
    uploaded, errs = upload_nutrients(
        key, url, release_date, nutrients, dry_run=dry_run
    )
    LOG.info("  Release %s: %d updated, %d errors", release_date, uploaded, errs)
    return uploaded, errs


def main():
    parser = argparse.ArgumentParser(
        description="Backfill nutrition columns on usda_product_history"
    )
    parser.add_argument(
        "--release", type=str, default=None,
        help="Process a specific release date (e.g. 2025-12-18)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Extract but don't upload",
    )
    parser.add_argument(
        "--cache-dir", type=str, default=None,
        help="Directory for caching downloaded ZIPs",
    )
    args = parser.parse_args()

    key = _read_key()
    url = os.environ.get(
        "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
    )
    if not key and not args.dry_run:
        LOG.error("No SUPABASE_KEY found")
        sys.exit(1)

    cache_dir = args.cache_dir or os.path.join(
        tempfile.gettempdir(), "usda_history_cache"
    )
    os.makedirs(cache_dir, exist_ok=True)

    if args.release:
        releases = [(d, f) for d, f in USDA_RELEASES if d == args.release]
        if not releases:
            LOG.error("Release %s not found", args.release)
            sys.exit(1)
    else:
        releases = list(USDA_RELEASES)

    LOG.info("=" * 60)
    LOG.info("Nutrition Backfill")
    LOG.info("=" * 60)
    LOG.info("Releases: %d", len(releases))
    LOG.info("Cache: %s", cache_dir)

    start = time.time()
    total_up = 0
    total_err = 0

    for i, (rd, fn) in enumerate(releases):
        LOG.info("")
        LOG.info("[%d/%d] Release %s", i + 1, len(releases), rd)
        LOG.info("-" * 40)
        up, err = process_release(rd, fn, cache_dir, key, url, args.dry_run)
        total_up += up
        total_err += err

    elapsed = time.time() - start
    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("NUTRITION BACKFILL COMPLETE")
    LOG.info("Total updated: {:,}".format(total_up))
    LOG.info("Total errors:  {:,}".format(total_err))
    LOG.info("Elapsed:       {:.1f} minutes".format(elapsed / 60))


if __name__ == "__main__":
    main()
