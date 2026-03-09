#!/usr/bin/env python3
"""
FullCarts Change Detector
=========================
Compares consecutive product_versions for each product and creates
change_event records when size or price changes are detected.

This job is idempotent — running it multiple times will not create
duplicate events (guarded by the UNIQUE constraint on version pairs).

Modes:
  --all          Scan all products (default)
  --upc UPC      Scan a single product by UPC
  --dry-run      Compute changes but don't write to database

Data flow:
  product_versions (sorted by observed_date)
    → compare consecutive pairs
    → compute size_delta_pct, ppu_delta_pct
    → classify (shrinkflation / downsizing / upsizing / price_hike)
    → insert into change_events

Can also be run as a Postgres function: SELECT detect_all_changes();
This Python version adds logging, dry-run mode, and richer output.
"""

import sys
import logging
import argparse
from datetime import date

# Allow running from project root: python -m backend.jobs.change_detector
sys.path.insert(0, ".")

from backend.lib.supabase_client import get_client

log = logging.getLogger("fullcarts.change_detector")


# ---------------------------------------------------------------------------
# Classification logic (mirrors the SQL classify_change function)
# ---------------------------------------------------------------------------

def classify_change(old_size, new_size, old_price=None, new_price=None):
    """Classify a product change and compute deltas.

    Returns dict with:
        size_delta_pct, old_ppu, new_ppu, ppu_delta_pct,
        change_type, is_shrinkflation, severity
    """
    # Size delta (negative = shrunk)
    size_delta_pct = round(((new_size - old_size) / old_size) * 100, 2) if old_size > 0 else 0

    # Price per unit
    old_ppu = round(old_price / old_size, 4) if old_price and old_size > 0 else None
    new_ppu = round(new_price / new_size, 4) if new_price and new_size > 0 else None

    # PPU delta
    ppu_delta_pct = None
    if old_ppu and old_ppu > 0 and new_ppu is not None:
        ppu_delta_pct = round(((new_ppu - old_ppu) / old_ppu) * 100, 2)

    # Classification
    is_shrinkflation = False
    if new_size > old_size:
        change_type = "upsizing"
    elif new_size < old_size:
        if new_price is not None and old_price is not None and new_price < old_price:
            change_type = "downsizing"
        else:
            change_type = "shrinkflation"
            is_shrinkflation = True
    else:
        if new_price is not None and old_price is not None and new_price > old_price:
            change_type = "price_hike"
        else:
            change_type = "downsizing"

    # Severity
    severity = None
    if size_delta_pct < 0:
        abs_pct = abs(size_delta_pct)
        if abs_pct >= 15:
            severity = "major"
        elif abs_pct >= 5:
            severity = "moderate"
        else:
            severity = "minor"

    return {
        "size_delta_pct": size_delta_pct,
        "old_ppu": old_ppu,
        "new_ppu": new_ppu,
        "ppu_delta_pct": ppu_delta_pct,
        "change_type": change_type,
        "is_shrinkflation": is_shrinkflation,
        "severity": severity,
    }


# ---------------------------------------------------------------------------
# Core detection logic
# ---------------------------------------------------------------------------

def detect_changes_for_product(sb, upc, dry_run=False):
    """Detect new change events for a single product.

    Returns list of change_event dicts (inserted or would-be-inserted).
    """
    # Fetch all versions for this product, ordered by date
    resp = (
        sb.table("product_versions")
        .select("id, observed_date, size, unit, price, price_per_unit")
        .eq("product_upc", upc)
        .order("observed_date", desc=False)
        .execute()
    )
    versions = resp.data or []

    if len(versions) < 2:
        return []

    # Fetch existing change events to avoid duplicates
    existing_resp = (
        sb.table("change_events")
        .select("version_before_id, version_after_id")
        .eq("product_upc", upc)
        .execute()
    )
    existing_pairs = {
        (e["version_before_id"], e["version_after_id"])
        for e in (existing_resp.data or [])
    }

    new_events = []

    for i in range(1, len(versions)):
        v_before = versions[i - 1]
        v_after = versions[i]

        # Skip if sizes are the same
        if float(v_before["size"]) == float(v_after["size"]):
            continue

        # Skip if we already have this pair
        pair = (v_before["id"], v_after["id"])
        if pair in existing_pairs:
            continue

        old_price = float(v_before["price"]) if v_before.get("price") else None
        new_price = float(v_after["price"]) if v_after.get("price") else None

        classification = classify_change(
            float(v_before["size"]),
            float(v_after["size"]),
            old_price,
            new_price,
        )

        event = {
            "product_upc": upc,
            "version_before_id": v_before["id"],
            "version_after_id": v_after["id"],
            "detected_date": v_after["observed_date"],
            "old_size": float(v_before["size"]),
            "new_size": float(v_after["size"]),
            "unit": v_after["unit"],
            "size_delta_pct": classification["size_delta_pct"],
            "old_price": old_price,
            "new_price": new_price,
            "old_price_per_unit": classification["old_ppu"],
            "new_price_per_unit": classification["new_ppu"],
            "price_per_unit_delta_pct": classification["ppu_delta_pct"],
            "change_type": classification["change_type"],
            "is_shrinkflation": classification["is_shrinkflation"],
            "severity": classification["severity"],
        }

        new_events.append(event)
        log.info(
            f"  {classification['change_type'].upper():14} "
            f"{v_before['size']}{v_after['unit']} → {v_after['size']}{v_after['unit']} "
            f"({classification['size_delta_pct']:+.1f}%) "
            f"[{v_after['observed_date']}]"
        )

    # Insert new events
    if new_events and not dry_run:
        try:
            sb.table("change_events").insert(new_events).execute()
        except Exception as exc:
            log.warning(f"  Batch insert failed for {upc}, trying one-by-one: {exc}")
            for event in new_events:
                try:
                    sb.table("change_events").insert(event).execute()
                except Exception as exc2:
                    log.warning(f"    Single insert failed: {exc2}")

    return new_events


def detect_all_changes(sb, dry_run=False):
    """Detect changes across all products with version history.

    Returns (total_events_created, products_scanned).
    """
    # Get all distinct UPCs that have product_versions (paginated)
    upcs_set = set()
    offset = 0
    batch_size = 1000
    while True:
        resp = (sb.table("product_versions")
                .select("product_upc")
                .range(offset, offset + batch_size - 1)
                .execute())
        rows = resp.data or []
        upcs_set.update(row["product_upc"] for row in rows)
        if len(rows) < batch_size:
            break
        offset += batch_size
    upcs = sorted(upcs_set)

    log.info(f"Scanning {len(upcs)} products for changes...")

    total_events = 0
    products_with_changes = 0

    for upc in upcs:
        events = detect_changes_for_product(sb, upc, dry_run=dry_run)
        if events:
            total_events += len(events)
            products_with_changes += 1
            log.info(f"  {upc}: {len(events)} new event(s)")

    # Update repeat_offender flags
    if not dry_run and total_events > 0:
        _update_repeat_offenders(sb)

    return total_events, len(upcs)


def _update_repeat_offenders(sb):
    """Mark products with 2+ shrinkflation events as repeat offenders.

    Excludes retracted and false-positive events so that corrections
    don't inflate the repeat-offender count.
    """
    resp = (
        sb.table("change_events")
        .select("product_upc")
        .eq("is_shrinkflation", True)
        .neq("false_positive", True)
        .is_("retracted_at", "null")
        .execute()
    )

    # Count shrink events per product
    counts = {}
    for row in (resp.data or []):
        upc = row["product_upc"]
        counts[upc] = counts.get(upc, 0) + 1

    for upc, count in counts.items():
        try:
            # Also reset repeat_offender to False when count drops to 1
            sb.table("products").update(
                {"repeat_offender": count > 1}
            ).eq("upc", upc).execute()
        except Exception as exc:
            log.warning(f"  Failed to update repeat_offender for {upc}: {exc}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="FullCarts Change Detector — compares product versions and creates change events"
    )
    parser.add_argument("--upc", type=str, help="Scan a single product by UPC")
    parser.add_argument("--dry-run", action="store_true", help="Compute but don't write")
    args = parser.parse_args()

    sb = get_client()

    if args.upc:
        log.info(f"Scanning product: {args.upc}")
        events = detect_changes_for_product(sb, args.upc, dry_run=args.dry_run)
        log.info(f"{'Would create' if args.dry_run else 'Created'} {len(events)} event(s)")
    else:
        total, scanned = detect_all_changes(sb, dry_run=args.dry_run)
        log.info(f"\nDone. Scanned {scanned} products, "
                 f"{'would create' if args.dry_run else 'created'} {total} change event(s)")


if __name__ == "__main__":
    main()
