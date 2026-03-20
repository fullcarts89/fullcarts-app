#!/usr/bin/env python3
"""promote_claims.py — Promote approved claims to product_entities + published_changes.

Data flow (per claim):
  claims (status='approved')
    → find-or-create product_entity (brand + canonical_name)
    → find-or-create pack_variant (entity_id + variant_name)
    → create variant_observation BEFORE (old_size)
    → create variant_observation AFTER  (new_size)
    → create change_candidate
    → create published_change
    → update claim: matched_entity_id + status='matched'

Usage:
    python3 pipeline/scripts/promote_claims.py [--dry-run] [--limit N]
"""

import os
import sys
import argparse
import logging
import math
from typing import Optional, Dict, List, Any
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)
))))

from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.lib.logging_setup import get_logger

log = get_logger("promote_claims")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _compute_delta_pct(old_size: float, new_size: float) -> float:
    """Signed percentage change from old to new."""
    return (new_size - old_size) / old_size * 100.0


def _classify_change(delta_pct: float):
    """Return (change_type, severity, is_shrinkflation)."""
    if delta_pct < 0:
        change_type = "shrinkflation"
        is_shrink = True
    else:
        change_type = "upsizing"
        is_shrink = False

    abs_delta = abs(delta_pct)
    if abs_delta < 5:
        severity = "minor"
    elif abs_delta < 15:
        severity = "moderate"
    else:
        severity = "major"

    return change_type, severity, is_shrink


def _confidence_score(claim: Dict[str, Any]) -> float:
    """Extract overall confidence score (0-1) from claim.confidence JSONB."""
    conf = claim.get("confidence") or {}
    if isinstance(conf, dict):
        try:
            return float(conf.get("overall", 0.5))
        except (TypeError, ValueError):
            return 0.5
    return 0.5


# ---------------------------------------------------------------------------
# Find-or-create helpers
# ---------------------------------------------------------------------------

def _find_or_create_entity(
    sb,
    brand: str,
    canonical_name: str,
    category: Optional[str],
    dry_run: bool,
    stats: Dict[str, int],
) -> Optional[str]:
    """Return product_entity UUID, creating if needed."""
    brand_lc = brand.strip().lower()
    name_lc = canonical_name.strip().lower()

    # Search by lower(brand) + lower(canonical_name)
    resp = (
        sb.table("product_entities")
        .select("id")
        .ilike("brand", brand.strip())
        .ilike("canonical_name", canonical_name.strip())
        .limit(1)
        .execute()
    )
    if resp.data:
        stats["entity_matched"] += 1
        return resp.data[0]["id"]

    if dry_run:
        stats["entity_created"] += 1
        return "dry-run-entity-id"

    row = {
        "brand": brand.strip(),
        "canonical_name": canonical_name.strip(),
        "category": category,
    }
    ins = sb.table("product_entities").insert(row).execute()
    if ins.data:
        stats["entity_created"] += 1
        return ins.data[0]["id"]

    log.error("Failed to create product_entity for %s / %s", brand, canonical_name)
    return None


def _find_or_create_variant(
    sb,
    entity_id: str,
    variant_name: str,
    size_unit: Optional[str],
    upc: Optional[str],
    dry_run: bool,
    stats: Dict[str, int],
) -> Optional[str]:
    """Return pack_variant UUID, creating if needed."""
    if dry_run and entity_id == "dry-run-entity-id":
        stats["variant_created"] += 1
        return "dry-run-variant-id"

    q = (
        sb.table("pack_variants")
        .select("id")
        .eq("entity_id", entity_id)
        .ilike("variant_name", variant_name.strip())
        .limit(1)
    )
    resp = q.execute()
    if resp.data:
        stats["variant_matched"] += 1
        return resp.data[0]["id"]

    if dry_run:
        stats["variant_created"] += 1
        return "dry-run-variant-id"

    row = {
        "entity_id": entity_id,
        "variant_name": variant_name.strip(),
        "size_unit": size_unit,
        "upc": upc,
        "is_active": True,
    }
    ins = sb.table("pack_variants").insert(row).execute()
    if ins.data:
        stats["variant_created"] += 1
        return ins.data[0]["id"]

    log.error("Failed to create pack_variant for entity %s / %s", entity_id, variant_name)
    return None


def _create_observation(
    sb,
    variant_id: str,
    observed_date: str,
    size: float,
    size_unit: Optional[str],
    raw_item_id: str,
    source_ref: Optional[str],
    dry_run: bool,
) -> Optional[str]:
    """Insert a variant_observation and return its UUID.

    On duplicate key (same variant/date/source_type/retailer), fetch and
    return the existing row's ID rather than failing.
    """
    if dry_run:
        return "dry-run-obs-id"

    row = {
        "variant_id": variant_id,
        "observed_date": observed_date,
        "source_type": "reddit",  # claims originate from reddit/news
        "source_ref": source_ref,
        "size": size,
        "size_unit": size_unit,
        "raw_item_id": raw_item_id,
    }
    try:
        ins = sb.table("variant_observations").insert(row).execute()
        if ins.data:
            return ins.data[0]["id"]
    except Exception as exc:
        # Handle duplicate key — fetch existing row
        if "23505" in str(exc) or "duplicate key" in str(exc).lower():
            existing = (
                sb.table("variant_observations")
                .select("id")
                .eq("variant_id", variant_id)
                .eq("observed_date", observed_date)
                .eq("source_type", "reddit")
                .is_("retailer", "null")
                .limit(1)
                .execute()
            )
            if existing.data:
                return existing.data[0]["id"]
        raise
    return None


def _create_candidate(
    sb,
    variant_id: str,
    obs_before_id: str,
    obs_after_id: str,
    size_before: float,
    size_after: float,
    delta_pct: float,
    change_type: str,
    severity: str,
    is_shrinkflation: bool,
    claim_id: str,
    dry_run: bool,
) -> Optional[str]:
    """Insert a change_candidate and return its UUID.

    On duplicate (obs_before, obs_after) pair, return existing candidate.
    """
    if dry_run:
        return "dry-run-candidate-id"

    row = {
        "variant_id": variant_id,
        "observation_before": obs_before_id,
        "observation_after": obs_after_id,
        "size_before": size_before,
        "size_after": size_after,
        "size_delta_pct": round(delta_pct, 4),
        "change_type": change_type,
        "severity": severity,
        "is_shrinkflation": is_shrinkflation,
        "status": "approved",
        "supporting_claims": [claim_id],
        "evidence_count": 1,
    }
    try:
        ins = sb.table("change_candidates").insert(row).execute()
        if ins.data:
            return ins.data[0]["id"]
    except Exception as exc:
        if "23505" in str(exc) or "duplicate key" in str(exc).lower():
            existing = (
                sb.table("change_candidates")
                .select("id")
                .eq("observation_before", obs_before_id)
                .eq("observation_after", obs_after_id)
                .limit(1)
                .execute()
            )
            if existing.data:
                return existing.data[0]["id"]
        raise
    return None


def _create_published_change(
    sb,
    candidate_id: str,
    variant_id: str,
    entity_id: str,
    claim: Dict[str, Any],
    size_before: float,
    size_after: float,
    size_unit: str,
    delta_pct: float,
    change_type: str,
    severity: str,
    observed_date: str,
    dry_run: bool,
) -> Optional[str]:
    """Insert a published_change and return its UUID."""
    if dry_run:
        return "dry-run-published-id"

    evidence = [
        {
            "type": "claim",
            "claim_id": claim["id"],
            "raw_item_id": claim.get("raw_item_id"),
            "source_url": None,
            "confidence": _confidence_score(claim),
            "change_description": claim.get("change_description"),
        }
    ]

    row = {
        "candidate_id": candidate_id,
        "variant_id": variant_id,
        "entity_id": entity_id,
        "brand": (claim.get("brand") or "").strip(),
        "product_name": (claim.get("product_name") or "").strip(),
        "size_before": size_before,
        "size_after": size_after,
        "size_unit": size_unit,
        "size_delta_pct": round(delta_pct, 4),
        "change_type": change_type,
        "severity": severity,
        "observed_date": observed_date,
        "evidence_summary": evidence,
    }
    try:
        ins = sb.table("published_changes").insert(row).execute()
        if ins.data:
            return ins.data[0]["id"]
    except Exception as exc:
        if "23505" in str(exc) or "duplicate key" in str(exc).lower():
            existing = (
                sb.table("published_changes")
                .select("id")
                .eq("candidate_id", candidate_id)
                .limit(1)
                .execute()
            )
            if existing.data:
                return existing.data[0]["id"]
        raise
    return None


# ---------------------------------------------------------------------------
# Core promotion logic
# ---------------------------------------------------------------------------

def promote_claim(
    sb,
    claim: Dict[str, Any],
    dry_run: bool,
    stats: Dict[str, int],
) -> bool:
    """Promote a single approved claim. Returns True on success."""
    claim_id = claim["id"]
    brand = (claim.get("brand") or "").strip()
    product_name = (claim.get("product_name") or "").strip()

    # Skip claims without enough info to create a meaningful entity
    if not brand or not product_name:
        log.debug("Claim %s: skipping — missing brand or product_name", claim_id)
        stats["skipped_no_name"] += 1
        return False

    old_size = claim.get("old_size")
    new_size = claim.get("new_size")

    if old_size is None or new_size is None:
        log.debug("Claim %s: skipping — missing old_size or new_size", claim_id)
        stats["skipped_no_sizes"] += 1
        return False

    try:
        old_size = float(old_size)
        new_size = float(new_size)
    except (TypeError, ValueError):
        log.warning("Claim %s: invalid size values: %s / %s", claim_id, old_size, new_size)
        stats["skipped_no_sizes"] += 1
        return False

    if old_size <= 0:
        log.debug("Claim %s: skipping — old_size <= 0", claim_id)
        stats["skipped_no_sizes"] += 1
        return False

    # Prefer old_size_unit; fall back to new_size_unit
    size_unit = (claim.get("old_size_unit") or claim.get("new_size_unit") or "").strip() or None

    delta_pct = _compute_delta_pct(old_size, new_size)
    change_type, severity, is_shrinkflation = _classify_change(delta_pct)

    # Observed date — use claim's date or today
    observed_date = claim.get("observed_date")
    if not observed_date:
        observed_date = date.today().isoformat()
    else:
        # Ensure it's a string date
        if isinstance(observed_date, (datetime, date)):
            observed_date = observed_date.isoformat()

    category = claim.get("category")
    upc = claim.get("upc")
    raw_item_id = claim.get("raw_item_id")

    # 1. Find-or-create product_entity
    entity_id = _find_or_create_entity(
        sb, brand, product_name, category, dry_run, stats
    )
    if not entity_id:
        stats["errors"] += 1
        return False

    # 2. Find-or-create pack_variant
    variant_id = _find_or_create_variant(
        sb, entity_id, product_name, size_unit, upc, dry_run, stats
    )
    if not variant_id:
        stats["errors"] += 1
        return False

    # 3. Create BEFORE observation (old_size) — use observed_date - 1 day
    #    so it doesn't conflict with the AFTER observation's unique key.
    before_date = (date.fromisoformat(observed_date) - timedelta(days=1)).isoformat()
    obs_before_id = _create_observation(
        sb, variant_id, before_date, old_size, size_unit,
        raw_item_id, claim_id, dry_run
    )
    if not obs_before_id:
        stats["errors"] += 1
        log.error("Claim %s: failed to create BEFORE observation", claim_id)
        return False

    # 4. Create AFTER observation (new_size)
    obs_after_id = _create_observation(
        sb, variant_id, observed_date, new_size, size_unit,
        raw_item_id, claim_id, dry_run
    )
    if not obs_after_id:
        stats["errors"] += 1
        log.error("Claim %s: failed to create AFTER observation", claim_id)
        return False

    # 5. Create change_candidate
    candidate_id = _create_candidate(
        sb, variant_id, obs_before_id, obs_after_id,
        old_size, new_size, delta_pct,
        change_type, severity, is_shrinkflation,
        claim_id, dry_run
    )
    if not candidate_id:
        stats["errors"] += 1
        log.error("Claim %s: failed to create change_candidate", claim_id)
        return False

    # 6. Create published_change
    published_id = _create_published_change(
        sb, candidate_id, variant_id, entity_id, claim,
        old_size, new_size, size_unit or "",
        delta_pct, change_type, severity, observed_date, dry_run
    )
    if not published_id:
        stats["errors"] += 1
        log.error("Claim %s: failed to create published_change", claim_id)
        return False

    # 7. Update claim: matched_entity_id + status='matched'
    if not dry_run:
        sb.table("claims").update({
            "matched_entity_id": entity_id,
            "status": "matched",
        }).eq("id", claim_id).execute()

    stats["published"] += 1
    log.info(
        "Claim %s → %s %s  %.1f%s→%.1f%s  (%s, %s)%s",
        claim_id[:8], brand, product_name,
        old_size, size_unit or "", new_size, size_unit or "",
        change_type, severity,
        " [DRY RUN]" if dry_run else "",
    )
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Promote approved claims to product_entities + published_changes"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would be promoted without writing to DB"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max number of claims to process (0 = all)"
    )
    parser.add_argument(
        "--batch-size", type=int, default=1000,
        help="Fetch page size (default 1000)"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Enable DEBUG logging"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    sb = get_client()

    stats = {
        "fetched": 0,
        "skipped_no_name": 0,
        "skipped_no_sizes": 0,
        "entity_created": 0,
        "entity_matched": 0,
        "variant_created": 0,
        "variant_matched": 0,
        "published": 0,
        "errors": 0,
    }

    if args.dry_run:
        log.info("=== DRY RUN MODE — no changes will be written ===")

    # Paginate through approved claims
    offset = 0
    batch_size = args.batch_size
    total_processed = 0

    while True:
        if args.limit > 0:
            fetch_n = min(batch_size, args.limit - total_processed)
            if fetch_n <= 0:
                break
        else:
            fetch_n = batch_size

        resp = (
            sb.table("claims")
            .select("*")
            .eq("status", "approved")
            .order("extracted_at")
            .range(offset, offset + fetch_n - 1)
            .execute()
        )

        batch = resp.data or []
        if not batch:
            break

        stats["fetched"] += len(batch)
        log.info("Processing batch of %d claims (offset=%d)…", len(batch), offset)

        for claim in batch:
            # Recycle HTTP/2 connection every 400 claims to avoid stream limit
            if total_processed > 0 and total_processed % 400 == 0:
                reset_client()
                sb = get_client()
                log.info("Recycled Supabase connection at %d claims", total_processed)
            promote_claim(sb, claim, args.dry_run, stats)
            total_processed += 1
            if args.limit > 0 and total_processed >= args.limit:
                break

        if len(batch) < fetch_n:
            break  # last page

        offset += fetch_n

        if args.limit > 0 and total_processed >= args.limit:
            break

    # Summary
    print("\n" + "=" * 60)
    print("PROMOTE CLAIMS SUMMARY")
    if args.dry_run:
        print("  *** DRY RUN — nothing was written ***")
    print("=" * 60)
    print(f"  Fetched (approved claims):  {stats['fetched']}")
    print(f"  Skipped (no name):          {stats['skipped_no_name']}")
    print(f"  Skipped (no sizes):         {stats['skipped_no_sizes']}")
    print(f"  Entities created:           {stats['entity_created']}")
    print(f"  Entities matched (reused):  {stats['entity_matched']}")
    print(f"  Variants created:           {stats['variant_created']}")
    print(f"  Variants matched (reused):  {stats['variant_matched']}")
    print(f"  Published changes:          {stats['published']}")
    print(f"  Errors:                     {stats['errors']}")
    print("=" * 60)


if __name__ == "__main__":
    main()
