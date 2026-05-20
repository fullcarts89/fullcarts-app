#!/usr/bin/env python3
"""Resolve legacy approved claims (and matched claims with a partial entity link).

Two stuck shapes get handled here:

  1. Legacy status='approved' rows. The pre-refactor flow had an 'approved'
     bucket between admin-clicks-OK and the daily promote run. That bucket
     is gone — admin clicks now write status='matched' directly. Any leftover
     approved rows get migrated to 'matched' with matched_entity_id cleared
     so promote_claims will pick them up on its next pass.

  2. status='matched' rows with matched_entity_id already set but no
     published_change row covering (entity_id, old_size, new_size). The
     entity got linked by some older path but the event was never built.
     If a published_change for that tuple now exists (e.g. created by a
     different claim): add this claim to its evidence_summary and flip the
     status to 'merged'. Otherwise: clear matched_entity_id so the
     regular promote run picks them up. (Pre-migration-060 this script
     wrote 'evidence' for fold-ins; 060 carved out the dedicated 'merged'
     status to keep the evidence-wall bucket clean.)

  3. Claims missing sizes are demoted to 'unmatched' (can't build an event).

Idempotent: re-running on a healthy queue is a no-op.

Usage:
    python -m pipeline.scripts.cleanup_stuck_matched [--dry-run]
"""
import argparse
import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pipeline.lib.data_quality_flags import raise_flag

LOG = logging.getLogger("cleanup_stuck_matched")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_stuck_with_entity(sb) -> List[Dict[str, Any]]:
    """Approved claims that have a matched_entity_id but status hasn't moved on."""
    # status='matched' with a matched_entity_id set — but the promote run
    # skips these (its fetch filters on matched_entity_id IS NULL). They
    # need either a fold-into-event or an entity-clear-and-retry.
    resp = (sb.table("claims")
            .select("id,brand,product_name,old_size,new_size,old_size_unit,new_size_unit,"
                    "matched_entity_id,matched_variant_id,observed_date,change_description")
            .eq("status", "matched")
            .not_.is_("matched_entity_id", "null")
            .execute())
    return resp.data or []


def _migrate_legacy_approved(sb, dry_run: bool = False) -> int:
    """Flip any straggler status='approved' rows to 'matched' with entity
    cleared, so the regular promote run handles them. Returns count migrated.
    """
    resp = (sb.table("claims")
            .select("id")
            .eq("status", "approved")
            .execute()).data or []
    if not resp:
        return 0
    if dry_run:
        return len(resp)
    ids = [r["id"] for r in resp]
    # Batch in chunks of 100 to keep the URL short.
    migrated = 0
    for i in range(0, len(ids), 100):
        batch = ids[i:i + 100]
        (sb.table("claims")
         .update({
             "status": "matched",
             "matched_entity_id": None,
             "matched_variant_id": None,
         })
         .in_("id", batch)
         .execute())
        migrated += len(batch)
    return migrated


def _find_existing_event(sb, entity_id: str, old_size, new_size) -> Optional[Dict[str, Any]]:
    if old_size is None or new_size is None:
        return None
    resp = (sb.table("published_changes")
            .select("id, candidate_id, evidence_count, evidence_summary, "
                    "variant_id, is_retracted")
            .eq("entity_id", entity_id)
            .eq("size_before", old_size)
            .eq("size_after", new_size)
            .eq("is_retracted", False)
            .order("observed_date")
            .limit(1)
            .execute())
    return resp.data[0] if resp.data else None


def _is_event_originator(sb, candidate_id: Optional[str], claim_id: str) -> bool:
    """A claim is the originator of an event when its id is listed in the
    event's change_candidate.supporting_claims[] array. promote_claims.py
    writes the originator there at candidate-create time; folded-in claims
    go into published_changes.evidence_summary, never into supporting_claims.
    So this is a clean "is this the claim that built this event?" check.

    The pre-fix cleanup folded originators back into their own event as
    evidence on every daily run — the matched bucket drained to ~zero. This
    guard keeps a legitimate originator in 'matched' where it belongs.
    """
    if not candidate_id:
        return False
    resp = (sb.table("change_candidates")
            .select("supporting_claims")
            .eq("id", candidate_id)
            .limit(1)
            .execute())
    if not resp.data:
        return False
    supporting = resp.data[0].get("supporting_claims") or []
    return str(claim_id) in [str(s) for s in supporting]


def _claim_already_in_summary(summary: Any, claim_id: str) -> bool:
    if not isinstance(summary, list):
        return False
    for entry in summary:
        if isinstance(entry, dict) and str(entry.get("claim_id")) == str(claim_id):
            return True
    return False


def _flag_stuck_unresolved(sb, dry_run: bool, stats: Dict[str, int]) -> None:
    """Detector: claims in `status='matched'` AND `matched_entity_id IS NULL`
    AND extracted_at > 7 days ago.

    These are claims promote_claims has had repeated daily chances to resolve
    and still can't (entity-matching failed, brand string is too weird, etc.).
    They'll sit forever otherwise. Flag for admin review via the
    data_quality_flags quarantine queue (migration 063).
    """
    threshold = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    resp = (sb.table("claims")
            .select("id, brand, product_name, extracted_at")
            .eq("status", "matched")
            .is_("matched_entity_id", "null")
            .lt("extracted_at", threshold)
            .limit(1000)
            .execute())
    rows = resp.data or []
    for r in rows:
        if dry_run:
            LOG.info("[DRY] would flag stuck claim %s (%s / %s, extracted %s)",
                     r["id"], r.get("brand"), r.get("product_name"), r.get("extracted_at"))
            stats["stuck_unresolved_flagged"] += 1
            continue
        try:
            new_id = raise_flag(
                sb,
                flag_kind="stuck_approved_claim",
                severity="med",
                detected_by="cleanup_stuck_matched",
                claim_id=r["id"],
                detail={
                    "brand": r.get("brand"),
                    "product_name": r.get("product_name"),
                    "extracted_at": r.get("extracted_at"),
                },
            )
            if new_id:
                stats["stuck_unresolved_flagged"] += 1
        except Exception as exc:  # noqa: BLE001
            stats["errors"] += 1
            LOG.error("raise_flag failed for claim %s: %s", r["id"], exc)


def cleanup(sb, dry_run: bool = False) -> Dict[str, int]:
    stats = {
        "legacy_approved_migrated": 0, # status='approved' stragglers post-refactor
        "scanned": 0,
        "originator_skipped": 0,       # claim is the event's originator — leave matched
        "folded_into_event": 0,
        "already_in_evidence": 0,      # idempotent re-run case
        "entity_cleared_for_retry": 0,
        "discarded_no_size": 0,        # missing sizes — can't fold or promote
        "stuck_unresolved_flagged": 0, # data_quality_flags entries (migration 063)
        "errors": 0,
    }

    legacy = _migrate_legacy_approved(sb, dry_run=dry_run)
    stats["legacy_approved_migrated"] = legacy
    if legacy:
        LOG.info("Migrated %d legacy status='approved' rows to 'matched'", legacy)

    claims = _fetch_stuck_with_entity(sb)
    LOG.info("Found %d matched claims with matched_entity_id set", len(claims))

    for c in claims:
        stats["scanned"] += 1
        try:
            old_size = c.get("old_size")
            new_size = c.get("new_size")

            # No sizes: demote to discarded, can't recover.
            if old_size is None or new_size is None:
                if dry_run:
                    LOG.info("[DRY] claim %s (no sizes): would set status='discarded'", c["id"])
                else:
                    (sb.table("claims")
                     .update({"status": "discarded"})
                     .eq("id", c["id"])
                     .execute())
                stats["discarded_no_size"] += 1
                continue

            event = _find_existing_event(sb, c["matched_entity_id"], old_size, new_size)

            # Originator guard. Before May 2026 this script folded EVERY
            # matched-with-entity claim into the event it found at the
            # claim's (entity, sizes) tuple — including the originator, which
            # of course finds its own event. That drained the matched bucket
            # to ~zero on the very first daily run. Skip when the claim is
            # listed in the event's change_candidates.supporting_claims, since
            # promote_claims only writes the originator there.
            if event is not None and _is_event_originator(
                sb, event.get("candidate_id"), c["id"],
            ):
                if dry_run:
                    LOG.info("[DRY] claim %s is originator of event %s — would skip",
                             c["id"], event["id"])
                stats["originator_skipped"] += 1
                continue

            if event is None:
                # Clear matched_entity_id so the regular promote_claims daily run
                # picks this up and builds the published_change. Brand+name will
                # still resolve to the same entity via the find-or-create lookup.
                if dry_run:
                    LOG.info("[DRY] claim %s (%s/%s, %s→%s): no matching event — would clear "
                             "matched_entity_id for promote_claims retry",
                             c["id"], c.get("brand"), c.get("product_name"), old_size, new_size)
                else:
                    (sb.table("claims")
                     .update({"matched_entity_id": None, "matched_variant_id": None})
                     .eq("id", c["id"])
                     .execute())
                stats["entity_cleared_for_retry"] += 1
                continue

            # Event exists. Fold this claim's evidence in if not already there.
            summary = event.get("evidence_summary") or []
            if _claim_already_in_summary(summary, c["id"]):
                if dry_run:
                    LOG.info("[DRY] claim %s already in event %s evidence — would just set "
                             "status='merged'", c["id"], event["id"])
                else:
                    update_payload = {"status": "merged"}
                    if not c.get("matched_variant_id") and event.get("variant_id"):
                        update_payload["matched_variant_id"] = event["variant_id"]
                    (sb.table("claims")
                     .update(update_payload)
                     .eq("id", c["id"])
                     .execute())
                stats["already_in_evidence"] += 1
                continue

            new_entry = {
                "source": "claim",
                "claim_id": str(c["id"]),
                "description": c.get("change_description", "") or "",
            }
            updated_summary = (summary if isinstance(summary, list) else []) + [new_entry]
            new_count = (event.get("evidence_count") or len(summary) or 0) + 1

            if dry_run:
                LOG.info("[DRY] claim %s (%s/%s, %s→%s): would fold into event %s "
                         "(evidence_count %s → %s)",
                         c["id"], c.get("brand"), c.get("product_name"),
                         old_size, new_size, event["id"],
                         event.get("evidence_count"), new_count)
            else:
                (sb.table("published_changes")
                 .update({
                     "evidence_summary": updated_summary,
                     "evidence_count": new_count,
                 })
                 .eq("id", event["id"])
                 .execute())
                update_payload = {"status": "merged"}
                # Backfill matched_variant_id from the event if claim was missing it.
                if not c.get("matched_variant_id") and event.get("variant_id"):
                    update_payload["matched_variant_id"] = event["variant_id"]
                (sb.table("claims")
                 .update(update_payload)
                 .eq("id", c["id"])
                 .execute())
            stats["folded_into_event"] += 1

        except Exception as exc:  # noqa: BLE001 — surface but keep going
            stats["errors"] += 1
            LOG.error("Failed on claim %s: %s", c.get("id"), exc)

    # Independent detector pass — flag claims that have been waiting on
    # promote_claims for too long. Runs after the cleanup loop so any
    # legacy migrations + entity_cleared retries have had a chance first.
    _flag_stuck_unresolved(sb, dry_run, stats)

    return stats


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    sb = _get_client()
    stats = cleanup(sb, dry_run=args.dry_run)

    mode = "DRY RUN" if args.dry_run else "LIVE"
    LOG.info("\n=== cleanup_stuck_approved (%s) ===", mode)
    for k, v in stats.items():
        LOG.info("  %s: %d", k, v)


if __name__ == "__main__":
    main()
