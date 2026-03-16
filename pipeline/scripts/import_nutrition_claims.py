#!/usr/bin/env python3
"""Import USDA nutrition-based skimpflation results as claims.

Calls the nutrition_skimpflation() DB function, creates synthetic raw_items
with source_type='usda_nutrition', and writes claims with high confidence.

Usage:
    python -m pipeline.scripts.import_nutrition_claims
    python -m pipeline.scripts.import_nutrition_claims --dry-run
    python -m pipeline.scripts.import_nutrition_claims --min-score 10
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List

from pipeline.lib.hashing import content_hash
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("import_nutrition_claims")

EXTRACTOR_VERSION = "usda-nutrition-v1"
SCRAPER_VERSION = "pipeline-v2.0-nutrition"


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Import USDA nutrition skimpflation results as claims"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be imported without writing",
    )
    parser.add_argument(
        "--min-score", type=float, default=5.0,
        help="Minimum skimpflation score threshold (default: 5)",
    )
    parser.add_argument(
        "--early", type=str, default="2022-10-28",
        help="Early release date (default: 2022-10-28)",
    )
    parser.add_argument(
        "--late", type=str, default="2025-12-18",
        help="Late release date (default: 2025-12-18)",
    )
    args = parser.parse_args()

    client = get_client()

    # Step 1: Call the DB function to get nutrition skimpflation results
    log.info(
        "Calling nutrition_skimpflation(%s, %s, %s)...",
        args.early, args.late, args.min_score,
    )
    results = _fetch_nutrition_results(client, args.early, args.late, args.min_score)
    log.info("Got %d nutrition skimpflation results", len(results))

    if not results:
        log.info("No results to import. Done.")
        return

    # Step 2: Create raw_items + claims for each result
    imported = 0
    skipped = 0

    for result in results:
        upc = result.get("gtin_upc", "")
        if not upc:
            skipped += 1
            continue

        source_id = "nutrition_{}_{}_{}" .format(upc, args.early, args.late)

        if args.dry_run:
            log.info(
                "[DRY RUN] %s | %s | score=%.1f",
                result.get("brand_name", "?"),
                (result.get("description") or "?")[:50],
                result.get("skimp_score", 0),
            )
            imported += 1
            continue

        # Create raw_item for this result
        raw_payload = {
            "gtin_upc": upc,
            "brand_name": result.get("brand_name"),
            "description": result.get("description"),
            "skimp_score": result.get("skimp_score"),
            "protein_drop_pct": result.get("protein_drop_pct"),
            "fiber_drop_pct": result.get("fiber_drop_pct"),
            "sugar_rise_pct": result.get("sugar_rise_pct"),
            "sodium_rise_pct": result.get("sodium_rise_pct"),
            "old_protein": result.get("old_protein"),
            "new_protein": result.get("new_protein"),
            "old_fiber": result.get("old_fiber"),
            "new_fiber": result.get("new_fiber"),
            "old_sugar": result.get("old_sugar"),
            "new_sugar": result.get("new_sugar"),
            "old_sodium": result.get("old_sodium"),
            "new_sodium": result.get("new_sodium"),
            "old_calories": result.get("old_calories"),
            "new_calories": result.get("new_calories"),
            "early_release": args.early,
            "late_release": args.late,
        }

        raw_item_id = _upsert_raw_item(client, source_id, raw_payload)
        if raw_item_id is None:
            skipped += 1
            continue

        # Create claim
        change_parts = []  # type: List[str]
        if result.get("protein_drop_pct"):
            change_parts.append("protein -%.0f%%" % result["protein_drop_pct"])
        if result.get("fiber_drop_pct"):
            change_parts.append("fiber -%.0f%%" % result["fiber_drop_pct"])
        if result.get("sugar_rise_pct"):
            change_parts.append("sugar +%.0f%%" % result["sugar_rise_pct"])
        if result.get("sodium_rise_pct"):
            change_parts.append("sodium +%.0f%%" % result["sodium_rise_pct"])
        change_desc = "Nutrition changes: %s" % ", ".join(change_parts)

        claim_row = {
            "raw_item_id": raw_item_id,
            "extractor_version": EXTRACTOR_VERSION,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "brand": result.get("brand_name"),
            "product_name": result.get("description"),
            "category": "other",
            "upc": upc,
            "change_description": change_desc,
            "confidence": {
                "brand": 0.95,
                "product_name": 0.95,
                "size_change": 0.0,
                "overall": 0.85,
            },
            "status": "pending",
        }

        try:
            (
                client.table("claims")
                .upsert(claim_row, on_conflict="raw_item_id,extractor_version")
                .execute()
            )
            imported += 1
        except Exception as exc:
            log.error("Failed to write claim for UPC %s: %s", upc, str(exc)[:200])
            skipped += 1

    log.info("Done: imported=%d, skipped=%d", imported, skipped)


def _fetch_nutrition_results(client, early, late, min_score):
    # type: (Any, str, str, float) -> List[Dict[str, Any]]
    """Call the nutrition_skimpflation() RPC function."""
    try:
        resp = client.rpc(
            "nutrition_skimpflation",
            {"early_date": early, "late_date": late, "min_score": min_score},
        ).execute()
        return resp.data or []
    except Exception as exc:
        log.error("RPC call failed: %s", str(exc)[:300])
        # Fallback: try reading from local JSON if available
        return _try_local_json()


def _try_local_json():
    # type: () -> List[Dict[str, Any]]
    """Fallback: read from nutrition_skimpflation.json if RPC times out."""
    import os
    path = os.path.join(
        os.path.dirname(__file__), "..", "..", "nutrition_skimpflation.json"
    )
    if not os.path.exists(path):
        log.warning("No local fallback file found at %s", path)
        return []

    log.info("Using local fallback: %s", path)
    with open(path) as f:
        data = json.load(f)

    results = []
    for item in data.get("changes", []):
        # Map local JSON format to DB function format
        row = {
            "gtin_upc": item.get("upc"),
            "brand_name": item.get("brand"),
            "description": item.get("description"),
            "skimp_score": item.get("score"),
        }
        # Extract individual nutrient changes
        for ch in item.get("changes", []):
            nutrient = ch.get("nutrient", "")
            pct = ch.get("pct_change", 0)
            if nutrient == "protein_g" and pct < 0:
                row["protein_drop_pct"] = abs(pct)
                row["old_protein"] = ch.get("early_value")
                row["new_protein"] = ch.get("late_value")
            elif nutrient == "fiber_g" and pct < 0:
                row["fiber_drop_pct"] = abs(pct)
                row["old_fiber"] = ch.get("early_value")
                row["new_fiber"] = ch.get("late_value")
            elif nutrient == "sugars_g" and pct > 0:
                row["sugar_rise_pct"] = pct
                row["old_sugar"] = ch.get("early_value")
                row["new_sugar"] = ch.get("late_value")
            elif nutrient == "sodium_mg" and pct > 0:
                row["sodium_rise_pct"] = pct
                row["old_sodium"] = ch.get("early_value")
                row["new_sodium"] = ch.get("late_value")
        results.append(row)

    return results


def _upsert_raw_item(client, source_id, raw_payload):
    # type: (Any, str, Dict[str, Any]) -> str
    """Insert or find raw_item for this nutrition result.

    Returns the raw_item ID.
    """
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "source_type": "usda_nutrition",
        "source_id": source_id,
        "captured_at": now,
        "raw_payload": raw_payload,
        "content_hash": content_hash(raw_payload),
        "scraper_version": SCRAPER_VERSION,
    }

    try:
        resp = (
            client.table("raw_items")
            .upsert(row, on_conflict="source_type,source_id")
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]

        # If upsert returned empty (already existed), fetch the ID
        existing = (
            client.table("raw_items")
            .select("id")
            .eq("source_type", "usda_nutrition")
            .eq("source_id", source_id)
            .limit(1)
            .execute()
        )
        if existing.data:
            return existing.data[0]["id"]

        log.error("Could not get raw_item ID for source_id=%s", source_id)
        return None
    except Exception as exc:
        log.error("Failed to upsert raw_item %s: %s", source_id, str(exc)[:200])
        return None


if __name__ == "__main__":
    main()
