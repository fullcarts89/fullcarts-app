#!/usr/bin/env python3
"""Build the usda_products lookup table from USDA FDC bulk downloads.

Downloads USDA branded food ZIP(s), extracts both branded_food.csv and food.csv,
joins them on fdc_id, and uploads to the usda_products Supabase table.

food.csv contains actual product descriptions (e.g. "Lay's Classic Potato Chips
10 Ounce Plastic Bag") that branded_food.csv lacks.

Usage:
    # Process latest release only (fastest, ~854K products)
    python -m pipeline.scripts.build_usda_products

    # Process all 7 releases (most complete, dedupes by fdc_id keeping latest)
    python -m pipeline.scripts.build_usda_products --all-releases

    # Dry run (download and parse but don't upload)
    python -m pipeline.scripts.build_usda_products --dry-run
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
from typing import Any, Dict, Iterator, List, Optional, Tuple

import requests

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pipeline.config import USDA_FDC_BASE, USDA_RELEASES, USER_AGENT
from pipeline.lib.units import parse_package_weight

LOG = logging.getLogger("build_usda_products")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

# Supabase batch size for upserts
_BATCH_SIZE = 500
_LOG_EVERY = 50000


def _get_supabase_client():
    """Get Supabase client with service role key."""
    from pipeline.lib.supabase_client import get_client
    return get_client()


def _read_key() -> str:
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
                if line.startswith("SUPABASE_KEY=") and not os.environ.get("SUPABASE_KEY"):
                    return line.split("=", 1)[1]
    return ""


def download_zip(release_date: str, filename: str, tmpdir: str) -> Optional[str]:
    """Download a USDA release ZIP. Returns local path or None."""
    url = "{}/{}".format(USDA_FDC_BASE, filename)
    LOG.info("Downloading %s from %s ...", filename, url)

    try:
        resp = requests.get(
            url, stream=True, timeout=300,
            headers={"User-Agent": USER_AGENT},
        )
        resp.raise_for_status()
    except Exception as e:
        LOG.error("Download failed: %s", e)
        return None

    zip_path = os.path.join(tmpdir, filename)
    downloaded = 0
    with open(zip_path, "wb") as fh:
        for chunk in resp.iter_content(chunk_size=1024 * 1024):
            if chunk:
                fh.write(chunk)
                downloaded += len(chunk)
                if downloaded % (100 * 1024 * 1024) == 0:
                    LOG.info("  ... downloaded %d MB", downloaded // (1024 * 1024))

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    LOG.info("Downloaded %s (%.1f MB)", filename, size_mb)
    return zip_path


def list_zip_contents(zip_path: str) -> List[str]:
    """List all files in a ZIP."""
    with zipfile.ZipFile(zip_path, "r") as zf:
        return zf.namelist()


def extract_food_descriptions(zip_path: str) -> Dict[str, str]:
    """Extract fdc_id -> description mapping from food.csv in the ZIP.

    Returns empty dict if food.csv is not in the ZIP.
    """
    descriptions = {}  # type: Dict[str, str]

    with zipfile.ZipFile(zip_path, "r") as zf:
        # Find food.csv (may be nested in a subdirectory)
        csv_name = next(
            (n for n in zf.namelist() if n.endswith("food.csv")),
            None,
        )
        if csv_name is None:
            LOG.warning("food.csv not found in %s", zip_path)
            return descriptions

        LOG.info("Extracting descriptions from %s ...", csv_name)
        with zf.open(csv_name) as raw_file:
            text_file = io.TextIOWrapper(raw_file, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text_file)
            for row in reader:
                fdc_id = (row.get("fdc_id") or "").strip()
                desc = (row.get("description") or "").strip()
                if fdc_id and desc:
                    descriptions[fdc_id] = desc

    LOG.info("Extracted %d descriptions from food.csv", len(descriptions))
    return descriptions


def stream_branded_food(
    zip_path: str,
    descriptions: Dict[str, str],
    release_date: str,
) -> Iterator[Dict[str, Any]]:
    """Stream branded_food.csv rows, enriched with food.csv descriptions.

    Yields dicts ready for Supabase upsert.
    """
    with zipfile.ZipFile(zip_path, "r") as zf:
        csv_name = next(
            (n for n in zf.namelist() if n.endswith("branded_food.csv")),
            None,
        )
        if csv_name is None:
            LOG.error("branded_food.csv not found in %s", zip_path)
            return

        LOG.info("Streaming branded_food.csv from %s ...", csv_name)
        with zf.open(csv_name) as raw_file:
            text_file = io.TextIOWrapper(raw_file, encoding="utf-8", errors="replace")
            reader = csv.DictReader(text_file)

            count = 0
            for row in reader:
                fdc_id = (row.get("fdc_id") or "").strip()
                upc = (row.get("gtin_upc") or "").strip()

                if not fdc_id:
                    continue

                # Parse package weight
                pw_raw = (row.get("package_weight") or "").strip()
                parsed_size, parsed_unit = parse_package_weight(pw_raw)

                # Get description from food.csv
                desc = descriptions.get(fdc_id, "")

                product = {
                    "fdc_id": fdc_id,
                    "gtin_upc": upc or None,
                    "brand_owner": (row.get("brand_owner") or "").strip() or None,
                    "brand_name": (row.get("brand_name") or "").strip() or None,
                    "description": desc or None,
                    "branded_food_category": (row.get("branded_food_category") or "").strip() or None,
                    "package_weight": pw_raw or None,
                    "parsed_size": parsed_size,
                    "parsed_size_unit": parsed_unit or None,
                    "serving_size": (row.get("serving_size") or "").strip() or None,
                    "serving_size_unit": (row.get("serving_size_unit") or "").strip() or None,
                    "ingredients": (row.get("ingredients") or "").strip() or None,
                    "release_date": release_date,
                }
                yield product
                count += 1

                if count % _LOG_EVERY == 0:
                    LOG.info("  ... streamed %d branded_food rows", count)

            LOG.info("Streamed %d total branded_food rows", count)


def create_table_if_needed(client) -> None:
    """Create usda_products table via Supabase RPC if it doesn't exist.

    We just try an insert and see if it works; if the table doesn't exist
    we'll need to run the migration manually.
    """
    try:
        resp = client.table("usda_products").select("fdc_id").limit(1).execute()
        LOG.info("usda_products table exists (%d rows in sample)", len(resp.data or []))
    except Exception as e:
        LOG.error(
            "usda_products table does not exist. Please run migration 026 first:\n"
            "  db/migrations/026_usda_products.sql\n"
            "Error: %s", e
        )
        sys.exit(1)


def upload_products(
    client, products: List[Dict[str, Any]], dry_run: bool = False
) -> int:
    """Upload products to usda_products table in batches. Returns count uploaded."""
    if dry_run:
        LOG.info("DRY RUN: would upload %d products", len(products))
        return 0

    total = len(products)
    uploaded = 0
    errors = 0

    for i in range(0, total, _BATCH_SIZE):
        batch = products[i:i + _BATCH_SIZE]
        try:
            client.table("usda_products").upsert(
                batch,
                on_conflict="fdc_id",
            ).execute()
            uploaded += len(batch)
        except Exception as e:
            errors += 1
            LOG.error(
                "Batch %d-%d failed: %s",
                i, i + len(batch), str(e)[:200],
            )
            # Retry individual rows on batch failure
            for row in batch:
                try:
                    client.table("usda_products").upsert(
                        [row],
                        on_conflict="fdc_id",
                    ).execute()
                    uploaded += 1
                except Exception as e2:
                    LOG.warning(
                        "Row fdc_id=%s failed: %s",
                        row.get("fdc_id"), str(e2)[:100],
                    )

        if uploaded % 10000 == 0 and uploaded > 0:
            LOG.info("  ... uploaded %d / %d products", uploaded, total)

    LOG.info(
        "Upload complete: %d / %d products (%d batch errors)",
        uploaded, total, errors,
    )
    return uploaded


def try_download_full_csv(release_date: str, tmpdir: str) -> Optional[str]:
    """Try downloading the full FDC CSV (which includes food.csv).

    The branded_food ZIP may not contain food.csv. The full CSV download
    has the pattern: FoodData_Central_csv_YYYY-MM-DD.zip
    """
    filename = "FoodData_Central_csv_{}.zip".format(release_date)
    url = "{}/{}".format(USDA_FDC_BASE, filename)
    LOG.info("Trying full CSV download: %s", url)

    try:
        resp = requests.head(url, timeout=30, headers={"User-Agent": USER_AGENT})
        if resp.status_code == 200:
            return download_zip(release_date, filename, tmpdir)
        else:
            LOG.warning("Full CSV not available (HTTP %d)", resp.status_code)
            return None
    except Exception as e:
        LOG.warning("Full CSV check failed: %s", e)
        return None


def process_release(
    release_date: str,
    release_filename: str,
    tmpdir: str,
    dry_run: bool = False,
) -> Tuple[int, List[Dict[str, Any]]]:
    """Process a single USDA release. Returns (count, products list)."""
    # Step 1: Download the branded food ZIP
    zip_path = download_zip(release_date, release_filename, tmpdir)
    if zip_path is None:
        return 0, []

    # List contents
    contents = list_zip_contents(zip_path)
    LOG.info("ZIP contents (%d files): %s", len(contents), contents[:20])

    # Step 2: Try to get food.csv descriptions
    descriptions = extract_food_descriptions(zip_path)

    if not descriptions:
        # food.csv not in branded food ZIP — try the full CSV download
        LOG.info("food.csv not in branded food ZIP, trying full CSV download...")
        full_zip = try_download_full_csv(release_date, tmpdir)
        if full_zip:
            descriptions = extract_food_descriptions(full_zip)
            # Clean up the large full ZIP after extracting descriptions
            try:
                os.remove(full_zip)
            except OSError:
                pass

    if not descriptions:
        LOG.warning(
            "No food.csv descriptions available for release %s. "
            "Products will be loaded without descriptions.",
            release_date,
        )

    # Step 3: Stream and collect products
    products = list(stream_branded_food(zip_path, descriptions, release_date))

    # Clean up ZIP
    try:
        os.remove(zip_path)
    except OSError:
        pass

    # Stats
    with_desc = sum(1 for p in products if p.get("description"))
    with_upc = sum(1 for p in products if p.get("gtin_upc"))
    with_size = sum(1 for p in products if p.get("parsed_size") is not None)

    LOG.info(
        "Release %s: %d products (%d with descriptions, %d with UPC, %d with size)",
        release_date, len(products), with_desc, with_upc, with_size,
    )

    return len(products), products


def main():
    parser = argparse.ArgumentParser(description="Build usda_products lookup table")
    parser.add_argument(
        "--all-releases", action="store_true",
        help="Process all 7 USDA releases (dedup by fdc_id, keep latest)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Download and parse but don't upload to Supabase",
    )
    parser.add_argument(
        "--release", type=str, default=None,
        help="Process a specific release date (e.g. 2025-12-18)",
    )
    args = parser.parse_args()

    # Ensure we have a Supabase key
    key = _read_key()
    if not key and not args.dry_run:
        LOG.error("No SUPABASE_KEY found. Set env var or check web/.env.local")
        sys.exit(1)

    if key:
        os.environ["SUPABASE_KEY"] = key

    start_time = time.time()

    # Determine which releases to process
    if args.release:
        releases = [(d, f) for d, f in USDA_RELEASES if d == args.release]
        if not releases:
            LOG.error("Release %s not found in config", args.release)
            sys.exit(1)
    elif args.all_releases:
        releases = list(USDA_RELEASES)
    else:
        # Default: latest release only
        releases = [USDA_RELEASES[-1]]

    LOG.info(
        "Processing %d release(s): %s",
        len(releases),
        [r[0] for r in releases],
    )

    # Process releases (latest last so it wins on dedup)
    all_products = {}  # type: Dict[str, Dict[str, Any]]

    with tempfile.TemporaryDirectory() as tmpdir:
        for release_date, filename in releases:
            count, products = process_release(
                release_date, filename, tmpdir, args.dry_run
            )
            # Dedup by fdc_id — later releases overwrite earlier ones
            for p in products:
                all_products[p["fdc_id"]] = p

    final_products = list(all_products.values())
    LOG.info(
        "Total unique products across all releases: %d", len(final_products)
    )

    # Upload
    if not args.dry_run:
        client = _get_supabase_client()
        create_table_if_needed(client)
        uploaded = upload_products(client, final_products, dry_run=args.dry_run)
    else:
        uploaded = 0

    elapsed = time.time() - start_time
    LOG.info(
        "Done in %.1f minutes. %d unique products, %d uploaded.",
        elapsed / 60, len(final_products), uploaded,
    )

    # Print summary stats
    brands = set()
    categories = set()
    with_desc = 0
    with_size = 0
    for p in final_products:
        if p.get("brand_name"):
            brands.add(p["brand_name"])
        if p.get("branded_food_category"):
            categories.add(p["branded_food_category"])
        if p.get("description"):
            with_desc += 1
        if p.get("parsed_size") is not None:
            with_size += 1

    print("\n" + "=" * 60)
    print("USDA PRODUCTS SUMMARY")
    print("=" * 60)
    print("Total products:     {:,}".format(len(final_products)))
    print("With descriptions:  {:,} ({:.1f}%)".format(
        with_desc, 100 * with_desc / max(len(final_products), 1)))
    print("With parsed size:   {:,} ({:.1f}%)".format(
        with_size, 100 * with_size / max(len(final_products), 1)))
    print("Unique brands:      {:,}".format(len(brands)))
    print("Unique categories:  {:,}".format(len(categories)))
    print("Elapsed:            {:.1f} minutes".format(elapsed / 60))


if __name__ == "__main__":
    main()
