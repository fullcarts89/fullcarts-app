#!/usr/bin/env python3
"""Backfill: collapse duplicate published_changes into single events.

A product shrinks 200g → 180g exactly once. Multiple published_changes rows
for the same (entity, size_before, size_after) tuple are by definition
documenting the same event — whether they came from a wire-story syndicated
across 40 regional papers in one week (Newsquest UK), or from a "best of"
republication years later that GDELT re-indexed.

Dedup key: (entity_id, size_before, size_after). No date window by default
because date dispersion across re-publishings of the same wire story can
span years, and same-product/same-magnitude re-shrinkages are vanishingly
rare. Use --window-days N if you want a narrower window for some reason.

For each cluster of >=2 published_changes matching the key:
  - Keep the EARLIEST as canonical
  - Merge all evidence_summary arrays into the canonical
  - Sum evidence_count
  - Delete the duplicate rows

Designed to be safe to re-run. Skips singletons.

Usage:
    python -m pipeline.scripts.dedup_events --dry-run
    python -m pipeline.scripts.dedup_events --brand Cadbury  # single brand
    python -m pipeline.scripts.dedup_events --window-days 30  # opt back into a window
    python -m pipeline.scripts.dedup_events                  # all brands, live
"""
import argparse
import logging
import os
import sys
from collections import defaultdict
from datetime import date, timedelta
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("dedup_events")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000
# Effectively no window — 100 years. Use --window-days N to override.
# Rationale: (entity, size_before, size_after) uniquely identifies an event;
# date constraints under-merge syndication that GDELT re-indexes over years.
DEFAULT_WINDOW_DAYS = 36500


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _parse_date(value):
    # type: (Any) -> Optional[date]
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None


def _fetch_all_published_changes(sb, brand=None):
    # type: (Any, Optional[str]) -> List[Dict[str, Any]]
    """Fetch rows tolerant of the evidence_count column being absent (we run
    this BEFORE migration 050 lands during the initial dry-run; after the
    migration evidence_count is included for completeness)."""
    base_cols = ("id, entity_id, brand, product_name, size_before, "
                 "size_after, size_unit, observed_date, published_at, "
                 "evidence_summary, is_retracted")
    rows = []  # type: List[Dict[str, Any]]
    # Detect whether evidence_count exists once, up front.
    try:
        sb.table("published_changes").select("evidence_count").limit(1).execute()
        cols = base_cols + ", evidence_count"
    except Exception:
        cols = base_cols
    offset = 0
    while True:
        q = (sb.table("published_changes")
             .select(cols)
             .eq("is_retracted", False)
             .order("entity_id")
             .order("observed_date")
             .order("published_at")
             .range(offset, offset + PAGE_SIZE - 1))
        if brand:
            q = q.eq("brand", brand)
        resp = q.execute()
        batch = resp.data or []
        rows.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return rows


def _cluster_duplicates(
    rows,        # type: List[Dict[str, Any]]
    window_days,  # type: int
):
    # type: (...) -> List[List[Dict[str, Any]]]
    """Group rows that represent the same event.

    Same entity_id + same size_before + same size_after + observed_date
    within `window_days` of an earlier row in the group.

    rows MUST be sorted by (entity_id, observed_date, published_at ASC) so
    the canonical (earliest) row anchors each cluster.
    """
    clusters = []  # type: List[List[Dict[str, Any]]]
    # Group by (entity_id, size_before, size_after) first; then walk by date.
    by_key = defaultdict(list)  # type: Dict[Tuple[str, Any, Any], List[Dict[str, Any]]]
    for r in rows:
        if r.get("size_before") is None or r.get("size_after") is None:
            continue
        key = (r["entity_id"], r["size_before"], r["size_after"])
        by_key[key].append(r)

    for key, items in by_key.items():
        if len(items) < 2:
            continue
        # Items are already in observed_date asc order from the SQL ORDER BY.
        # Walk and cluster.
        current = [items[0]]
        for r in items[1:]:
            anchor_date = _parse_date(current[0]["observed_date"])
            this_date = _parse_date(r["observed_date"])
            if (anchor_date and this_date
                    and abs((this_date - anchor_date).days) <= window_days):
                current.append(r)
            else:
                if len(current) >= 2:
                    clusters.append(current)
                current = [r]
        if len(current) >= 2:
            clusters.append(current)
    return clusters


def _merge_cluster(sb, cluster, dry_run=False):
    # type: (Any, List[Dict[str, Any]], bool) -> Dict[str, int]
    """Collapse a cluster of >=2 published_changes into the earliest.

    The earliest by (observed_date asc, published_at asc) is the canonical.
    All other rows' evidence_summary entries are appended to the canonical,
    evidence_count becomes the cluster size, and the duplicates are deleted.
    """
    canonical = cluster[0]
    dupes = cluster[1:]

    # Combine evidence_summary
    combined = list(canonical.get("evidence_summary") or [])
    for d in dupes:
        es = d.get("evidence_summary") or []
        combined.extend(es)

    total_evidence = max(len(combined), sum(int(c.get("evidence_count") or 1)
                                            for c in cluster))

    stats = {"canonical_updated": 0, "dupes_deleted": 0}

    if dry_run:
        return stats

    # Update canonical with merged evidence
    sb.table("published_changes").update({
        "evidence_summary": combined,
        "evidence_count": total_evidence,
    }).eq("id", canonical["id"]).execute()
    stats["canonical_updated"] = 1

    # Delete duplicates in batches
    dupe_ids = [d["id"] for d in dupes]
    batch = 50
    for i in range(0, len(dupe_ids), batch):
        sb.table("published_changes").delete().in_(
            "id", dupe_ids[i:i + batch]
        ).execute()
    stats["dupes_deleted"] = len(dupe_ids)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Deduplicate event-level "
                                                 "syndication in published_changes")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--brand", type=str, default=None,
                        help="Limit to one brand (defaults to all)")
    parser.add_argument("--window-days", type=int, default=DEFAULT_WINDOW_DAYS,
                        help="Cluster rows within this date window "
                             "(default: %(default)s)")
    args = parser.parse_args()

    sb = _get_client()

    LOG.info("Fetching published_changes (brand=%s)...",
             args.brand or "ALL")
    rows = _fetch_all_published_changes(sb, brand=args.brand)
    LOG.info("Fetched %d non-retracted rows", len(rows))

    LOG.info("Clustering with window of %d days...", args.window_days)
    clusters = _cluster_duplicates(rows, args.window_days)

    excess = sum(len(c) - 1 for c in clusters)
    LOG.info("Found %d duplicate clusters covering %d rows "
             "(would remove %d as excess)",
             len(clusters),
             sum(len(c) for c in clusters),
             excess)

    if not clusters:
        LOG.info("Nothing to deduplicate.")
        return

    # By-brand breakdown so the dry-run output is actionable
    by_brand = defaultdict(int)  # type: Dict[str, int]
    for c in clusters:
        by_brand[c[0].get("brand", "?")] += len(c) - 1
    LOG.info("Top brands by removable duplicates:")
    for brand, n in sorted(by_brand.items(), key=lambda kv: -kv[1])[:15]:
        LOG.info("  %-30s  -%d events", brand, n)

    if args.dry_run:
        LOG.info("DRY RUN — no rows modified.")
        # Show a sample cluster
        if clusters:
            big = max(clusters, key=len)
            LOG.info("\nLargest cluster (%d rows):", len(big))
            LOG.info("  brand: %s", big[0].get("brand"))
            LOG.info("  product: %s", big[0].get("product_name"))
            LOG.info("  sizes: %s -> %s %s",
                     big[0].get("size_before"),
                     big[0].get("size_after"),
                     big[0].get("size_unit"))
            LOG.info("  observed dates: %s",
                     sorted({r.get("observed_date", "?") for r in big}))
        return

    # Execute merges
    totals = {"canonical_updated": 0, "dupes_deleted": 0}
    for idx, cluster in enumerate(clusters):
        s = _merge_cluster(sb, cluster, dry_run=False)
        for k, v in s.items():
            totals[k] = totals.get(k, 0) + v
        if (idx + 1) % 100 == 0:
            LOG.info("  Processed %d/%d clusters...", idx + 1, len(clusters))

    LOG.info("\nLIVE RESULTS:")
    for k, v in totals.items():
        LOG.info("  %s: %d", k, v)
    LOG.info("  events collapsed: %d", excess)


if __name__ == "__main__":
    main()
