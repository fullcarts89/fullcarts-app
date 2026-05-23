#!/usr/bin/env python3
"""Retract published_changes events that still have no image on any source
after the rescue pass, and move their backing claims into the discarded
bucket.

Companion to rescue_no_image_events.py. Run rescue first; whatever survives
the rescue (no image recovered) gets retracted here.

Retraction policy:
  * published_changes.is_retracted   = true
  * published_changes.retracted_at   = now()
  * published_changes.retraction_reason = 'no_image_sweep_2026_05_22'
  * claims.status                    = 'discarded'   (audit log captures the flip)
  * claims.matched_entity_id/variant — left intact (preserves the AI's link to
    the entity for forensic review; the discarded status hides the row from
    public surfaces anyway)

Backing claims are the union of:
  * change_candidates.supporting_claims[]  (the originator claim)
  * published_changes.evidence_summary[]    (the fold-ins)
  ...mirroring web/src/app/api/admin/retract-event/route.ts. The published_-
  changes.evidence_count counter is left at its current value — the rows
  are gone from the public surface either way.

Usage:
    # Dry-run (prints the count + sample 10)
    python -m pipeline.scripts.retract_no_image_events --dry-run

    # Live
    python -m pipeline.scripts.retract_no_image_events

    # Custom reason label
    python -m pipeline.scripts.retract_no_image_events --reason no_image_sweep_v2
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Set

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("retract_no_image_events")

DEFAULT_REASON = "no_image_sweep_2026_05_22"


def fetch_no_image_event_ids() -> List[Dict[str, Any]]:
    sb = get_client()
    PAGE = 1000
    out = []
    offset = 0
    while True:
        resp = (sb.table("event_evidence_summary")
                  .select("event_id, brand, product_name, sources")
                  .range(offset, offset + PAGE - 1).execute())
        rows = resp.data or []
        out.extend(rows)
        if len(rows) < PAGE:
            break
        offset += PAGE

    candidates = []
    for ev in out:
        srcs = ev.get("sources") or []
        if not srcs:
            continue
        any_image = any((s.get("claim_image_path") or s.get("image"))
                        for s in srcs)
        if any_image:
            continue
        candidates.append(ev)
    return candidates


def gather_backing_claim_ids(sb, event_ids: List[str]
                             ) -> Dict[str, Set[str]]:
    """For each event_id, return the set of claim_ids that back it."""
    claim_ids_by_event: Dict[str, Set[str]] = {eid: set() for eid in event_ids}

    # 1. Pull evidence_summary in batches
    for i in range(0, len(event_ids), 80):
        chunk = event_ids[i : i + 80]
        resp = (sb.table("published_changes")
                  .select("id, candidate_id, evidence_summary")
                  .in_("id", chunk).execute())
        for row in resp.data or []:
            eid = row["id"]
            # From evidence_summary
            for entry in row.get("evidence_summary") or []:
                cid = (entry or {}).get("claim_id")
                if isinstance(cid, str):
                    claim_ids_by_event[eid].add(cid)
            # Stash candidate_id for the next lookup
            row["_cid"] = row.get("candidate_id")

        # 2. For events with candidate_ids, also pull supporting_claims
        cand_ids = [r["candidate_id"] for r in (resp.data or [])
                    if r.get("candidate_id")]
        if cand_ids:
            cresp = (sb.table("change_candidates")
                       .select("id, supporting_claims")
                       .in_("id", cand_ids).execute())
            cand_to_claims = {r["id"]: r.get("supporting_claims") or []
                              for r in (cresp.data or [])}
            for row in resp.data or []:
                cid = row.get("candidate_id")
                if not cid:
                    continue
                for sc in cand_to_claims.get(cid, []):
                    if isinstance(sc, str):
                        claim_ids_by_event[row["id"]].add(sc)
    return claim_ids_by_event


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Print what would happen; no writes.")
    p.add_argument("--reason", default=DEFAULT_REASON,
                   help="Value to write to published_changes.retraction_reason")
    args = p.parse_args()

    sb = get_client()
    log.info("Loading residual no-image events...")
    events = fetch_no_image_event_ids()
    log.info("%d events qualify for retraction.", len(events))
    if not events:
        log.info("Nothing to do.")
        return 0

    event_ids = [e["event_id"] for e in events]
    log.info("Gathering backing claim_ids (originator + fold-ins)...")
    claims_by_event = gather_backing_claim_ids(sb, event_ids)

    total_claims = sum(len(s) for s in claims_by_event.values())
    log.info("Total backing claims: %d (events with zero backing claims: %d)",
             total_claims,
             sum(1 for v in claims_by_event.values() if not v))

    # Show sample
    log.info("Sample (first 10):")
    for ev in events[:10]:
        eid = ev["event_id"]
        log.info("    %s — %s / %s — %d backing claim(s)",
                 eid[:8], ev.get("brand"), ev.get("product_name"),
                 len(claims_by_event[eid]))

    if args.dry_run:
        log.info("Dry run — no writes.")
        return 0

    now = datetime.now(timezone.utc).isoformat()
    stats = {"events_retracted": 0, "claims_discarded": 0, "errors": 0}

    # Retract events in batches
    for i in range(0, len(event_ids), 80):
        chunk = event_ids[i : i + 80]
        try:
            resp = (sb.table("published_changes")
                      .update({
                          "is_retracted": True,
                          "retracted_at": now,
                          "retraction_reason": args.reason,
                      })
                      .in_("id", chunk).execute())
            stats["events_retracted"] += len(resp.data or chunk)
        except Exception as exc:
            log.error("Event retract batch failed: %s", str(exc)[:200])
            stats["errors"] += 1

    # Flip claims to discarded in batches
    all_claim_ids = list({cid for cids in claims_by_event.values()
                          for cid in cids})
    for i in range(0, len(all_claim_ids), 80):
        chunk = all_claim_ids[i : i + 80]
        try:
            resp = (sb.table("claims")
                      .update({"status": "discarded"})
                      .in_("id", chunk).execute())
            stats["claims_discarded"] += len(resp.data or chunk)
        except Exception as exc:
            log.error("Claim discard batch failed: %s", str(exc)[:200])
            stats["errors"] += 1

    log.info("=" * 60)
    log.info("Done.")
    for k, v in stats.items():
        log.info("    %-25s %d", k, v)
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
