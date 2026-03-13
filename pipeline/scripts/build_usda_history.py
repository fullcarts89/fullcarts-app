#!/usr/bin/env python3
"""Build the usda_product_history table from all USDA FDC releases.

Downloads all 7 USDA release ZIPs, extracts branded_food.csv + food.csv,
joins them on fdc_id, and uploads per-(UPC, release_date) rows including
ingredients, descriptions, and weights.

This enables:
  - Cross-release ingredient comparison (skimpflation detection)
  - Historical weight tracking per product
  - Full product name + ingredient lookup for claim verification

Usage:
    python -m pipeline.scripts.build_usda_history
    python -m pipeline.scripts.build_usda_history --release 2025-12-18
    python -m pipeline.scripts.build_usda_history --dry-run
"""
import argparse
import csv
import hashlib
import io
import logging
import os
import sys
import tempfile
import time
import zipfile
from typing import Any, Dict, Iterator, List, Optional, Tuple

import httpx
import requests

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pipeline.config import USDA_FDC_BASE, USDA_RELEASES, USER_AGENT
from pipeline.lib.units import parse_package_weight

LOG = logging.getLogger("build_usda_history")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

# Supabase batch size
_BATCH_SIZE = 500
_LOG_EVERY = 50000

# Connection recycling (prevents HTTP/2 connection exhaustion on large uploads)
_RECYCLE_EVERY = 4000  # batches


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
    """Create a fresh httpx client for Supabase REST API."""
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


# ── ZIP Download & Extraction ────────────────────────────────────────────────


def download_zip(release_date, filename, cache_dir):
    # type: (str, str, str) -> Optional[str]
    """Download a USDA release ZIP if not cached. Returns local path."""
    local_path = os.path.join(cache_dir, filename)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        LOG.info("  Cached: %s (%.1f MB)", local_path,
                 os.path.getsize(local_path) / (1024 * 1024))
        return local_path

    url = "{}/{}".format(USDA_FDC_BASE, filename)
    LOG.info("  Downloading %s ...", url)

    try:
        resp = requests.get(
            url, stream=True, timeout=300,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
    except Exception as e:
        LOG.error("Download failed: %s", e)
        return None

    downloaded = 0
    with open(local_path, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                fh.write(chunk)
                downloaded += len(chunk)
                if downloaded % (100 * 1024 * 1024) == 0:
                    LOG.info("    ... %d MB", downloaded // (1024 * 1024))

    LOG.info("  Downloaded %.1f MB", os.path.getsize(local_path) / (1024 * 1024))
    return local_path


def try_download_full_csv(release_date, cache_dir):
    # type: (str, str) -> Optional[str]
    """Try downloading the full FDC CSV (which includes food.csv)."""
    filename = "FoodData_Central_csv_{}.zip".format(release_date)
    url = "{}/{}".format(USDA_FDC_BASE, filename)
    LOG.info("  Trying full CSV download: %s", url)

    try:
        resp = requests.head(url, timeout=30, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            return download_zip(release_date, filename, cache_dir)
        else:
            LOG.warning("  Full CSV not available (HTTP %d)", resp.status_code)
            return None
    except Exception as e:
        LOG.warning("  Full CSV check failed: %s", e)
        return None


def extract_food_descriptions(zip_path):
    # type: (str) -> Dict[str, str]
    """Extract fdc_id -> description from food.csv in a ZIP."""
    descriptions = {}  # type: Dict[str, str]

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_name = next(
            (n for n in zf.namelist() if n.endswith("food.csv")),
            None,
        )
        if csv_name is None:
            return descriptions

        LOG.info("  Extracting descriptions from %s ...", csv_name)
        with zf.open(csv_name) as raw_file:
            text_file = io.TextIOWrapper(raw_file, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text_file)
            for row in reader:
                fdc_id = (row.get("fdc_id") or "").strip()
                desc = (row.get("description") or "").strip()
                if fdc_id and desc:
                    descriptions[fdc_id] = desc

    LOG.info("  Extracted %d descriptions", len(descriptions))
    return descriptions


def stream_products(zip_path, descriptions, release_date):
    # type: (str, Dict[str, str], str) -> Iterator[Dict[str, Any]]
    """Stream branded_food.csv rows joined with food.csv descriptions.

    Yields dicts keyed by (gtin_upc, release_date) for usda_product_history.
    Unlike build_usda_products.py, this includes ALL products (even without
    package_weight) and stores ingredients.
    """
    seen_upcs = set()  # type: set

    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_name = next(
            (n for n in zf.namelist() if n.endswith("branded_food.csv")),
            None,
        )
        if csv_name is None:
            LOG.error("branded_food.csv not found in %s", zip_path)
            return

        with zf.open(csv_name) as raw_file:
            text_file = io.TextIOWrapper(raw_file, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text_file)

            count = 0
            skipped_no_upc = 0
            skipped_dup_upc = 0
            for row in reader:
                fdc_id = (row.get("fdc_id") or "").strip()
                upc = (row.get("gtin_upc") or "").strip()

                if not upc:
                    skipped_no_upc += 1
                    continue

                # Deduplicate by UPC within same release
                # (multiple fdc_ids can map to same UPC; keep first seen)
                if upc in seen_upcs:
                    skipped_dup_upc += 1
                    continue
                seen_upcs.add(upc)

                # Parse weight
                pw_raw = (row.get("package_weight") or "").strip()
                parsed_size, parsed_unit = parse_package_weight(pw_raw)

                # Ingredients
                ingredients = (row.get("ingredients") or "").strip() or None
                ing_hash = None
                if ingredients:
                    ing_hash = hashlib.md5(ingredients.encode("utf-8")).hexdigest()

                # Description from food.csv
                desc = descriptions.get(fdc_id, "") or None

                yield {
                    "gtin_upc": upc,
                    "fdc_id": fdc_id,
                    "release_date": release_date,
                    "brand_owner": (row.get("brand_owner") or "").strip() or None,
                    "brand_name": (row.get("brand_name") or "").strip() or None,
                    "description": desc,
                    "branded_food_category": (row.get("branded_food_category") or "").strip() or None,
                    "ingredients": ingredients,
                    "package_weight": pw_raw or None,
                    "parsed_size": parsed_size,
                    "parsed_size_unit": parsed_unit or None,
                    "serving_size": (row.get("serving_size") or "").strip() or None,
                    "serving_size_unit": (row.get("serving_size_unit") or "").strip() or None,
                    "ingredients_hash": ing_hash,
                }
                count += 1

                if count % _LOG_EVERY == 0:
                    LOG.info("    ... streamed %d products", count)

            LOG.info("  Streamed %d products (%d no UPC, %d dup UPC skipped)",
                     count, skipped_no_upc, skipped_dup_upc)


# ── Upload ───────────────────────────────────────────────────────────────────


def upload_batch(client, batch):
    # type: (httpx.Client, List[Dict[str, Any]]) -> bool
    """Upload a batch to usda_product_history. Returns True on success."""
    resp = client.post(
        "/rest/v1/usda_product_history",
        json=batch,
        params={
            "on_conflict": "gtin_upc,release_date",
        },
    )
    if resp.status_code in (200, 201):
        return True
    else:
        LOG.error("Upload failed (HTTP %d): %s", resp.status_code, resp.text[:300])
        return False


def upload_release(key, url, products, dry_run=False):
    # type: (str, str, Iterator[Dict[str, Any]], bool) -> Tuple[int, int]
    """Upload a release's products to usda_product_history.

    Returns (uploaded_count, error_count).
    """
    if dry_run:
        count = 0
        for _ in products:
            count += 1
        LOG.info("  DRY RUN: would upload %d products", count)
        return count, 0

    client = _make_client(key, url)
    uploaded = 0
    errors = 0
    batch = []  # type: List[Dict[str, Any]]
    batch_count = 0

    for product in products:
        batch.append(product)
        if len(batch) >= _BATCH_SIZE:
            ok = upload_batch(client, batch)
            if ok:
                uploaded += len(batch)
            else:
                errors += len(batch)
                # Retry individual rows
                for row in batch:
                    try:
                        ok2 = upload_batch(client, [row])
                        if ok2:
                            uploaded += 1
                            errors -= 1
                    except Exception:
                        pass

            batch = []
            batch_count += 1

            if uploaded % 10000 == 0 and uploaded > 0:
                LOG.info("    ... uploaded %d products", uploaded)

            # Recycle HTTP/2 connection periodically
            if batch_count % _RECYCLE_EVERY == 0:
                LOG.info("    Recycling HTTP connection at batch %d ...", batch_count)
                client.close()
                client = _make_client(key, url)

    # Upload remaining
    if batch:
        ok = upload_batch(client, batch)
        if ok:
            uploaded += len(batch)
        else:
            errors += len(batch)

    client.close()
    return uploaded, errors


# ── Main ─────────────────────────────────────────────────────────────────────


def process_release(release_date, filename, cache_dir, key, url, dry_run):
    # type: (str, str, str, str, str, bool) -> Tuple[int, int, Dict[str, int]]
    """Process a single USDA release. Returns (uploaded, errors, stats)."""
    LOG.info("Downloading release %s ...", release_date)

    # Download branded food ZIP
    zip_path = download_zip(release_date, filename, cache_dir)
    if zip_path is None:
        return 0, 0, {}

    # Get food.csv descriptions
    descriptions = extract_food_descriptions(zip_path)
    if not descriptions:
        # Try full CSV download for food.csv
        LOG.info("  food.csv not in branded food ZIP, trying full CSV...")
        full_zip = try_download_full_csv(release_date, cache_dir)
        if full_zip:
            descriptions = extract_food_descriptions(full_zip)
            # Don't delete full ZIP — might be reused if cached

    # Stream products and upload
    products = stream_products(zip_path, descriptions, release_date)
    uploaded, errors = upload_release(key, url, products, dry_run=dry_run)

    # Compute stats from a re-scan (or we could track during streaming)
    stats = {
        "uploaded": uploaded,
        "errors": errors,
    }

    return uploaded, errors, stats


def main():
    parser = argparse.ArgumentParser(
        description="Build usda_product_history from all USDA releases"
    )
    parser.add_argument(
        "--release", type=str, default=None,
        help="Process a specific release date (e.g. 2025-12-18)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Download and parse but don't upload",
    )
    parser.add_argument(
        "--cache-dir", type=str, default=None,
        help="Directory for caching downloaded ZIPs",
    )
    args = parser.parse_args()

    key = _read_key()
    url = os.environ.get("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
    if not key and not args.dry_run:
        LOG.error("No SUPABASE_KEY found. Set env var or check web/.env.local")
        sys.exit(1)

    if key:
        os.environ["SUPABASE_KEY"] = key

    # Cache dir for ZIPs (persist between runs)
    cache_dir = args.cache_dir or os.path.join(tempfile.gettempdir(), "usda_history_cache")
    os.makedirs(cache_dir, exist_ok=True)

    # Determine releases to process
    if args.release:
        releases = [(d, f) for d, f in USDA_RELEASES if d == args.release]
        if not releases:
            LOG.error("Release %s not found in config", args.release)
            sys.exit(1)
    else:
        releases = list(USDA_RELEASES)

    LOG.info("=" * 60)
    LOG.info("USDA Product History Builder")
    LOG.info("=" * 60)
    LOG.info("Releases to process: %d", len(releases))
    LOG.info("Cache dir: %s", cache_dir)
    LOG.info("")

    start = time.time()
    total_uploaded = 0
    total_errors = 0

    for i, (release_date, filename) in enumerate(releases):
        LOG.info("")
        LOG.info("[%d/%d] Release %s", i + 1, len(releases), release_date)
        LOG.info("-" * 40)

        uploaded, errors, stats = process_release(
            release_date, filename, cache_dir, key, url, args.dry_run
        )
        total_uploaded += uploaded
        total_errors += errors

        LOG.info("  Release %s: %d uploaded, %d errors", release_date, uploaded, errors)

    elapsed = time.time() - start

    LOG.info("")
    LOG.info("=" * 60)
    LOG.info("USDA PRODUCT HISTORY SUMMARY")
    LOG.info("=" * 60)
    LOG.info("Releases processed: %d", len(releases))
    LOG.info("Total uploaded:     {:,}".format(total_uploaded))
    LOG.info("Total errors:       {:,}".format(total_errors))
    LOG.info("Elapsed:            {:.1f} minutes".format(elapsed / 60))
    LOG.info("")
    LOG.info("Next: Run skimpflation analysis with:")
    LOG.info("  python -m pipeline.scripts.ingredient_analysis --from-db")


if __name__ == "__main__":
    main()
