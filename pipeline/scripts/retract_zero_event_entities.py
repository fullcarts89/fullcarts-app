#!/usr/bin/env python3
"""One-shot cleanup: retract every active product_entity that has no
non-retracted published_changes row behind it.

Enforces the rule that every public-facing entity on FullCarts must trace
back to at least one live event. Pre-sweep diagnostic: ~20,872 active
entities, only ~2,306 have a live event behind them — so ~18,566 orphans
render as empty product pages today.

Idempotent: can be re-run safely. set_entity_retracted is a no-op on
already-retracted rows, and raise_flag swallows duplicate-key errors from
the partial unique index on (flag_kind, target_id).

Per-action audit row goes to data_quality_flags with:
  flag_kind   = "zero_event_entity_swept"
  severity    = "low"
  detected_by = "retract_zero_event_entities"
  entity_id   = the swept entity
  detail      = {"events_affected": N, "reason": "no live event"}

Usage:
    python3 -m pipeline.scripts.retract_zero_event_entities --dry-run
    python3 -m pipeline.scripts.retract_zero_event_entities --limit 100
    python3 -m pipeline.scripts.retract_zero_event_entities         # full run
"""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter
from typing import Any, Dict, List, Optional

from pipeline.lib import data_quality_flags

PAGE = 1000
FLAG_KIND = "zero_event_entity_swept"
DETECTED_BY = "retract_zero_event_entities"
BRAND_SUMMARY_LIMIT = 20


def find_orphaned_entities(sb):
    # type: (Any) -> List[str]
    """Return entity_ids of active entities with no live event behind them.

    Live event = a `published_changes` row with the same entity_id and
    is_retracted=false. The set difference is computed in memory because
    PostgREST has no native set-difference operator, and both tables fit
    well within memory (active ~21k rows, live events ~3k rows).
    """
    # 1. Page through all active entity ids.
    active_ids = []  # type: List[str]
    offset = 0
    while True:
        resp = (
            sb.table("product_entities")
            .select("id")
            .eq("is_retracted", False)
            .order("id")
            .range(offset, offset + PAGE - 1)
            .execute()
        )
        rows = resp.data or []
        active_ids.extend(r["id"] for r in rows)
        if len(rows) < PAGE:
            break
        offset += PAGE

    # 2. Page through entity_ids that have at least one live event.
    with_event = set()  # type: set
    offset = 0
    while True:
        resp = (
            sb.table("published_changes")
            .select("entity_id")
            .eq("is_retracted", False)
            .not_.is_("entity_id", "null")
            .range(offset, offset + PAGE - 1)
            .execute()
        )
        rows = resp.data or []
        for r in rows:
            eid = r.get("entity_id")
            if eid is not None:
                with_event.add(eid)
        if len(rows) < PAGE:
            break
        offset += PAGE

    # 3. Set diff = orphans.
    return [eid for eid in active_ids if eid not in with_event]


def load_brand_by_id(sb, entity_ids):
    # type: (Any, List[str]) -> Dict[str, str]
    """Fetch the brand for each entity id. Used only for the markdown
    summary. Paginated via `.in_()` in batches of PAGE rows because
    PostgREST chokes on huge `in.()` filters.
    """
    # PostgREST GETs with .in_() encode the values in the query string;
    # 1000 UUIDs (~36KB) breaks Cloudflare/PostgREST URL-length limits.
    # 200 keeps the URL well under 8KB. Total run time for 18k entities
    # stays fast because each batch round-trips in <100ms.
    BRAND_LOAD_BATCH = 200
    out = {}  # type: Dict[str, str]
    if not entity_ids:
        return out
    for i in range(0, len(entity_ids), BRAND_LOAD_BATCH):
        batch = entity_ids[i:i + BRAND_LOAD_BATCH]
        resp = (
            sb.table("product_entities")
            .select("id,brand")
            .in_("id", batch)
            .execute()
        )
        for r in (resp.data or []):
            out[r["id"]] = r.get("brand") or ""
    return out


def retract_one(sb, entity_id):
    # type: (Any, str) -> Optional[int]
    """Retract one entity via set_entity_retracted RPC.

    Returns events_affected from the RPC response (None if the response
    is empty). The RPC cascades the retraction to the entity's attached
    published_changes rows and flips associated matched claims back to
    status='pending' per migration 062.
    """
    resp = sb.rpc(
        "set_entity_retracted",
        {"p_entity_id": entity_id, "p_retracted": True},
    ).execute()
    rows = resp.data or []
    if not rows:
        return None
    first = rows[0]
    if isinstance(first, dict):
        return first.get("events_affected")
    # Some RPCs return a scalar (e.g. 0) — treat that as the count directly.
    return first


def process_orphans(sb, orphans, dry_run):
    # type: (Any, List[str], bool) -> Dict[str, Any]
    """Retract every orphan, raising a flag per success.

    Returns:
      {
        'retracted':     int,   # successful sb.rpc + raise_flag pairs
        'failures':      int,   # raised exceptions (logged, not re-raised)
        'dry_run':       bool,
        'would_retract': int,   # only meaningful in dry-run
      }
    """
    if dry_run:
        return {
            "retracted": 0,
            "failures": 0,
            "dry_run": True,
            "would_retract": len(orphans),
        }

    retracted = 0
    failures = 0
    total = len(orphans)
    for i, eid in enumerate(orphans):
        try:
            events = retract_one(sb, eid)
            data_quality_flags.raise_flag(
                sb,
                flag_kind=FLAG_KIND,
                severity="low",
                detected_by=DETECTED_BY,
                entity_id=eid,
                detail={"events_affected": events, "reason": "no live event"},
            )
            retracted += 1
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(
                "  ! failed {}: {}".format(eid, exc),
                file=sys.stderr,
            )
        if (i + 1) % 500 == 0:
            print("  ...{}/{} done".format(i + 1, total))

    return {
        "retracted": retracted,
        "failures": failures,
        "dry_run": False,
        "would_retract": total,
    }


def render_brand_summary(orphan_ids, brand_by_id, total_swept, failures):
    # type: (List[str], Dict[str, str], int, int) -> str
    """Render a markdown-style summary, suitable for piping into a GitHub
    Actions job summary later. Brand table is capped at the top 20 brands
    by sweep count.
    """
    counts = Counter()  # type: Counter
    for eid in orphan_ids:
        brand = brand_by_id.get(eid) or "Unknown"
        counts[brand] += 1

    top = counts.most_common(BRAND_SUMMARY_LIMIT)
    remaining = len(counts) - len(top)

    lines = []  # type: List[str]
    lines.append("## retract_zero_event_entities summary")
    lines.append("")
    lines.append("- **Total swept:** {}".format(total_swept))
    lines.append("- **Failures:** {}".format(failures))
    lines.append("- **Distinct brands affected:** {}".format(len(counts)))
    lines.append("")
    lines.append("### Top {} brands by sweep count".format(min(BRAND_SUMMARY_LIMIT, len(top))))
    lines.append("")
    lines.append("| Brand | Entities swept |")
    lines.append("|---|---|")
    for brand, count in top:
        # Pipe characters in brand strings would break the table; escape them.
        safe_brand = (brand or "Unknown").replace("|", "\\|")
        lines.append("| {} | {} |".format(safe_brand, count))
    if remaining > 0:
        lines.append("")
        lines.append("_…and {} more brands not shown._".format(remaining))
    return "\n".join(lines)


def main():
    # type: () -> int
    parser = argparse.ArgumentParser(
        description="One-shot cleanup: retract every active entity with no live event",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Report what would be retracted, but skip DB writes",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Process only the first N orphans (test mode)",
    )
    args = parser.parse_args()

    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        print(
            "ERROR: SUPABASE_URL and SUPABASE_KEY must be set",
            file=sys.stderr,
        )
        return 2

    from supabase import create_client
    sb = create_client(url, key)

    print("[retract_zero_event_entities] scanning for orphan entities...")
    orphans = find_orphaned_entities(sb)
    print(
        "[retract_zero_event_entities] {} orphaned active entities found".format(
            len(orphans)
        )
    )

    if args.limit is not None:
        orphans = orphans[: args.limit]
        print(
            "[retract_zero_event_entities] --limit {}: trimmed to {}".format(
                args.limit, len(orphans)
            )
        )

    if not orphans:
        print("[retract_zero_event_entities] nothing to do")
        return 0

    if args.dry_run:
        print("[retract_zero_event_entities] DRY RUN — no writes")
        sample = orphans[:20]
        for eid in sample:
            print("  would retract {}".format(eid))
        if len(orphans) > len(sample):
            print("  ... and {} more".format(len(orphans) - len(sample)))

    result = process_orphans(sb, orphans, dry_run=args.dry_run)

    # Load brands for the markdown summary. In dry-run we still want the
    # brand breakdown so the founder can see which brands the sweep would
    # touch.
    brand_by_id = load_brand_by_id(sb, orphans)
    summary_md = render_brand_summary(
        orphan_ids=orphans,
        brand_by_id=brand_by_id,
        total_swept=result["would_retract"] if args.dry_run else result["retracted"],
        failures=result["failures"],
    )

    print()
    print(summary_md)
    print()

    return 0 if result["failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
