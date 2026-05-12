#!/usr/bin/env python3
"""Activate pack_variants that have real UPCs for weekly monitoring.

Sets is_active=true on pack_variants with real (non-synthetic) UPCs so that
the off_daily and kroger_weekly scrapers pick them up.

Usage:
    python -m pipeline.scripts.activate_variants
    python -m pipeline.scripts.activate_variants --dry-run
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List

LOG = logging.getLogger("activate_variants")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000

SYNTHETIC_PREFIXES = ("CLAIM-", "REDDIT-", "TEMP-", "UNKNOWN")


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def main():
    parser = argparse.ArgumentParser(description="Activate pack_variants for monitoring")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sb = _get_client()

    # Check current state
    all_resp = sb.table("pack_variants").select("id", count="exact").execute()
    active_resp = (
        sb.table("pack_variants")
        .select("id", count="exact")
        .eq("is_active", True)
        .execute()
    )
    total = all_resp.count or 0
    already_active = active_resp.count or 0
    LOG.info("pack_variants: %d total, %d already active", total, already_active)

    # Fetch inactive variants with UPCs
    inactive = []  # type: List[Dict[str, Any]]
    offset = 0
    while True:
        resp = (
            sb.table("pack_variants")
            .select("id, upc, variant_name, entity_id")
            .neq("is_active", True)
            .not_.is_("upc", "null")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        inactive.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    LOG.info("Found %d inactive variants with UPCs", len(inactive))

    # Filter out synthetic UPCs
    to_activate = []
    skipped = 0
    for v in inactive:
        upc = v.get("upc", "")
        if any(upc.startswith(prefix) for prefix in SYNTHETIC_PREFIXES):
            skipped += 1
            continue
        to_activate.append(v)

    LOG.info(
        "Eligible for activation: %d (skipped %d synthetic UPCs)",
        len(to_activate), skipped,
    )

    if not to_activate:
        LOG.info("Nothing to activate.")
        return

    if args.dry_run:
        LOG.info("DRY RUN — would activate %d variants", len(to_activate))
        for v in to_activate[:10]:
            LOG.info("  %s | %s", v.get("upc", "?"), v.get("variant_name", "?"))
        if len(to_activate) > 10:
            LOG.info("  ... and %d more", len(to_activate) - 10)
        return

    # Batch activate
    activated = 0
    batch_size = 50
    ids = [v["id"] for v in to_activate]

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        resp = (
            sb.table("pack_variants")
            .update({"is_active": True})
            .in_("id", batch)
            .execute()
        )
        activated += len(resp.data or [])

    LOG.info("Activated %d pack_variants for monitoring", activated)

    # Verify
    new_active = (
        sb.table("pack_variants")
        .select("id", count="exact")
        .eq("is_active", True)
        .execute()
    )
    LOG.info("Total active variants now: %d", new_active.count or 0)


if __name__ == "__main__":
    main()
