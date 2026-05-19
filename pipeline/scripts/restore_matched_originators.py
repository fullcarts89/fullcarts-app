#!/usr/bin/env python3
"""One-shot: restore originator claims that cleanup_stuck_matched.py wrongly
flipped from 'matched' to 'evidence'.

Background:
  Between May 17 and May 19, 2026 the daily pipeline_promote cron ran an
  overeager cleanup that, for every claim where status='matched' and
  matched_entity_id was set, asked "does an event exist at this (entity,
  sizes) tuple?" and refiled the claim into that event's evidence_summary
  if so. Every legitimate event-originator matches its own event by that
  test, so the matched bucket drained to ~zero on each daily run.

  The cleanup script has since been patched (originator-skip guard added in
  this same PR). This script reverses the damage already in production.

How we identify "originator claims to restore":
  Every published_change has a candidate_id pointing at change_candidates.
  promote_claims.py writes the originator's claim id into
  change_candidates.supporting_claims on candidate-create. Folded-in claims
  go into published_changes.evidence_summary, NOT into supporting_claims.
  So change_candidates.supporting_claims is a clean "originators only" set
  across every event. For every id in there: if the current status is
  'evidence', flip it back to 'matched'.

  We also strip the originator's entry from the event's evidence_summary if
  the bad cleanup had appended it there, so we don't leave the originator
  duplicated as both supporting_claim AND evidence.

Usage:
    python -m pipeline.scripts.restore_matched_originators            # dry run (default)
    python -m pipeline.scripts.restore_matched_originators --apply    # write changes
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Set

LOG = logging.getLogger("restore_matched_originators")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 500


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_all_candidate_originators(sb) -> List[Dict[str, Any]]:
    """Returns [{candidate_id, event_id, evidence_summary, supporting_claims}]
    for every published_change that has a candidate behind it. Paginated to
    cover all events, not just the first 1000."""
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        resp = (sb.table("published_changes")
                .select("id, candidate_id, evidence_summary, is_retracted")
                .not_.is_("candidate_id", "null")
                .eq("is_retracted", False)
                .range(offset, offset + PAGE_SIZE - 1)
                .execute())
        batch = resp.data or []
        if not batch:
            break
        # Pull supporting_claims for this batch's candidate_ids in chunks.
        cand_ids = [r["candidate_id"] for r in batch]
        cand_map: Dict[str, List[str]] = {}
        for i in range(0, len(cand_ids), 100):
            chunk = cand_ids[i:i + 100]
            cresp = (sb.table("change_candidates")
                     .select("id, supporting_claims")
                     .in_("id", chunk)
                     .execute())
            for c in (cresp.data or []):
                cand_map[c["id"]] = [str(s) for s in (c.get("supporting_claims") or [])]
        for r in batch:
            r["supporting_claims"] = cand_map.get(r["candidate_id"], [])
            out.append(r)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def _fetch_claim_statuses(sb, claim_ids: List[str]) -> Dict[str, str]:
    """Return {claim_id: status} for the given ids, chunked to stay under
    PostgREST URL limits."""
    out: Dict[str, str] = {}
    for i in range(0, len(claim_ids), 100):
        chunk = claim_ids[i:i + 100]
        resp = (sb.table("claims")
                .select("id, status")
                .in_("id", chunk)
                .execute())
        for r in (resp.data or []):
            out[str(r["id"])] = r.get("status") or ""
    return out


def _strip_originator_from_summary(
    summary: Any, originator_ids: Set[str],
) -> Optional[List[Dict[str, Any]]]:
    """Return a new summary with any entry whose claim_id is in originator_ids
    removed. Returns None if no change is needed so the caller can skip the
    UPDATE entirely."""
    if not isinstance(summary, list):
        return None
    changed = False
    kept: List[Dict[str, Any]] = []
    for entry in summary:
        if isinstance(entry, dict) and str(entry.get("claim_id")) in originator_ids:
            changed = True
            continue
        kept.append(entry)
    return kept if changed else None


def restore(sb, apply: bool) -> Dict[str, int]:
    stats = {
        "events_scanned": 0,
        "originators_seen": 0,
        "originators_restored_to_matched": 0,
        "originators_already_matched": 0,
        "originators_in_other_status": 0,
        "events_with_evidence_summary_cleaned": 0,
        "evidence_entries_stripped": 0,
        "errors": 0,
    }

    events = _fetch_all_candidate_originators(sb)
    LOG.info("Scanning %d events with a candidate_id (non-retracted)", len(events))

    # Collect every originator claim id across every event so we batch the
    # status lookup. Most events have exactly one originator.
    all_originator_ids: List[str] = []
    for ev in events:
        all_originator_ids.extend(ev["supporting_claims"])
    unique_ids = list({cid for cid in all_originator_ids if cid})
    LOG.info("Looking up status for %d unique originator claim ids", len(unique_ids))
    status_by_id = _fetch_claim_statuses(sb, unique_ids)

    # Group originators by current status for a single bulk UPDATE on those in
    # 'evidence'. Other statuses get counted but left alone — restore is only
    # meant to undo the matched→evidence flip.
    to_restore: List[str] = []
    for cid in unique_ids:
        st = status_by_id.get(cid, "")
        if st == "evidence":
            to_restore.append(cid)
            stats["originators_restored_to_matched"] += 1
        elif st == "matched":
            stats["originators_already_matched"] += 1
        else:
            stats["originators_in_other_status"] += 1

    if apply and to_restore:
        for i in range(0, len(to_restore), 100):
            chunk = to_restore[i:i + 100]
            (sb.table("claims")
             .update({"status": "matched"})
             .in_("id", chunk)
             .execute())

    # Second pass: scrub originator self-references that the buggy cleanup
    # appended to each event's evidence_summary.
    for ev in events:
        stats["events_scanned"] += 1
        stats["originators_seen"] += len(ev["supporting_claims"])
        originator_set = set(ev["supporting_claims"])
        if not originator_set:
            continue
        cleaned = _strip_originator_from_summary(
            ev.get("evidence_summary"), originator_set,
        )
        if cleaned is None:
            continue
        stats["events_with_evidence_summary_cleaned"] += 1
        stripped = len(ev.get("evidence_summary") or []) - len(cleaned)
        stats["evidence_entries_stripped"] += stripped
        if apply:
            try:
                (sb.table("published_changes")
                 .update({
                     "evidence_summary": cleaned,
                     "evidence_count": max(len(cleaned), 1),
                 })
                 .eq("id", ev["id"])
                 .execute())
            except Exception as exc:  # noqa: BLE001
                stats["errors"] += 1
                LOG.error("Failed cleaning evidence_summary on event %s: %s",
                          ev["id"], exc)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="One-shot restore of originator claims wrongly demoted to 'evidence'.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes. Without this flag the script is a dry-run.",
    )
    args = parser.parse_args()

    sb = _get_client()
    apply = bool(args.apply)
    LOG.info("Mode: %s", "APPLY (will write)" if apply else "DRY-RUN (no writes)")

    stats = restore(sb, apply=apply)

    LOG.info("Done. Stats:")
    for k, v in stats.items():
        LOG.info("  %s: %d", k, v)

    if not apply:
        LOG.info("")
        LOG.info("Dry-run only. Re-run with --apply to commit the restore.")


if __name__ == "__main__":
    main()
