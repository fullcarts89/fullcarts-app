#!/usr/bin/env python3
"""Auto-approve high-confidence pending claims and promote them.

Approves pending claims that have:
  - Overall confidence >= threshold (default 80%)
  - Both old_size and new_size present
  - Brand is not null

Then runs promote_claims logic on the newly approved claims.

Usage:
    python -m pipeline.scripts.auto_approve_claims
    python -m pipeline.scripts.auto_approve_claims --threshold 75 --dry-run
    python -m pipeline.scripts.auto_approve_claims --approve-only  # skip promotion
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List

LOG = logging.getLogger("auto_approve_claims")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 500
DEFAULT_CONFIDENCE_THRESHOLD = 80


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_eligible_claims(sb, threshold: float) -> List[Dict[str, Any]]:
    """Fetch pending claims that meet auto-approval criteria.

    `confidence` is a JSONB column with sub-keys {overall, brand, size_change,
    product_name} on a 0-1 scale. We filter on `overall` >= threshold.
    """
    eligible = []  # type: List[Dict[str, Any]]
    offset = 0

    while True:
        resp = (
            sb.table("claims")
            .select("*")
            .eq("status", "pending")
            .not_.is_("old_size", "null")
            .not_.is_("new_size", "null")
            .not_.is_("brand", "null")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        for claim in batch:
            scores = claim.get("confidence") or {}
            if not isinstance(scores, dict):
                continue
            overall = scores.get("overall")
            if overall is not None and float(overall) >= threshold:
                eligible.append(claim)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return eligible


def main():
    parser = argparse.ArgumentParser(description="Auto-approve high-confidence claims")
    parser.add_argument("--threshold", type=float, default=DEFAULT_CONFIDENCE_THRESHOLD,
                        help="Min overall confidence; values > 1 are treated as percentages")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--approve-only", action="store_true",
                        help="Only approve, don't promote")
    parser.add_argument("--limit", type=int, default=0,
                        help="Max claims to approve (0=all)")
    args = parser.parse_args()

    # Normalize threshold: accept 0-100 percentage or 0-1 fraction.
    threshold = args.threshold / 100.0 if args.threshold > 1 else args.threshold

    sb = _get_client()

    # Show current pending stats
    pending_resp = (
        sb.table("claims")
        .select("id", count="exact")
        .eq("status", "pending")
        .execute()
    )
    LOG.info("Total pending claims: %d", pending_resp.count or 0)

    LOG.info("Fetching eligible claims (overall confidence >= %.2f)...", threshold)
    eligible = _fetch_eligible_claims(sb, threshold)

    if args.limit > 0:
        eligible = eligible[:args.limit]

    LOG.info("Found %d eligible claims for auto-approval", len(eligible))

    if not eligible:
        LOG.info("No claims meet the criteria. Try lowering --threshold.")
        return

    # Show breakdown by source
    by_source = {}  # type: Dict[str, int]
    for c in eligible:
        src = c.get("source_type", "unknown")
        by_source[src] = by_source.get(src, 0) + 1
    LOG.info("By source: %s", by_source)

    # Show sample
    for c in eligible[:5]:
        scores = c.get("confidence") or {}
        if not isinstance(scores, dict):
            scores = {}
        LOG.info(
            "  [%.0f%%] %s / %s: %s → %s %s",
            float(scores.get("overall", 0)) * 100,
            c.get("brand", "?"),
            c.get("product_name", "?"),
            c.get("old_size", "?"),
            c.get("new_size", "?"),
            c.get("old_size_unit", ""),
        )

    if args.dry_run:
        LOG.info("DRY RUN — would approve %d claims", len(eligible))
        return

    # Approve claims in batches
    approved = 0
    batch_size = 50
    ids = [c["id"] for c in eligible]

    for i in range(0, len(ids), batch_size):
        batch = ids[i:i + batch_size]
        resp = (
            sb.table("claims")
            .update({"status": "approved"})
            .in_("id", batch)
            .execute()
        )
        approved += len(resp.data or [])

    LOG.info("Approved %d claims", approved)

    if args.approve_only:
        LOG.info("--approve-only set, skipping promotion. Run promote_claims next.")
        return

    # Run promotion on newly approved claims
    LOG.info("Promoting newly approved claims...")
    from pipeline.scripts.promote_claims import (
        fetch_approved_claims,
        promote_claims,
    )
    claims_to_promote = fetch_approved_claims(sb)
    LOG.info("Found %d approved claims to promote", len(claims_to_promote))

    if claims_to_promote:
        stats = promote_claims(sb, claims_to_promote)
        LOG.info("Promotion results:")
        for k, v in stats.items():
            LOG.info("  %s: %d", k, v)


if __name__ == "__main__":
    main()
