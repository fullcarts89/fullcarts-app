#!/usr/bin/env python3
"""Resolve approved claims that are stuck because of an orphaned matched_entity_id.

`fetch_approved_claims` in promote_claims.py filters on
`matched_entity_id IS NULL`, so any claim whose entity was set by some other
path (admin UI, older promote_claims code) but whose status wasn't advanced
gets passed over on every daily run. This script handles them:

  - If a published_changes row already exists for the
    (entity_id, size_before, size_after) tuple this claim describes:
      add the claim to that event's evidence_summary (if not already there),
      bump evidence_count, and set claim status='evidence'.

  - Otherwise: clear matched_entity_id so the regular promote_claims run
    picks the claim up on its next pass and produces a published_change for
    it (entity will be reused because brand+name still resolve to the same
    row).

  - Claims missing sizes (old_size IS NULL AND new_size IS NULL) are demoted
    straight to 'unmatched' — without sizes they can't produce or join an
    event.

Idempotent: re-running after a successful pass is a no-op (no more approved
claims will have matched_entity_id set).

Usage:
    python -m pipeline.scripts.cleanup_stuck_approved [--dry-run]
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("cleanup_stuck_approved")
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
    resp = (sb.table("claims")
            .select("id,brand,product_name,old_size,new_size,old_size_unit,new_size_unit,"
                    "matched_entity_id,matched_variant_id,observed_date,change_description")
            .eq("status", "approved")
            .not_.is_("matched_entity_id", "null")
            .execute())
    return resp.data or []


def _find_existing_event(sb, entity_id: str, old_size, new_size) -> Optional[Dict[str, Any]]:
    if old_size is None or new_size is None:
        return None
    resp = (sb.table("published_changes")
            .select("id, evidence_count, evidence_summary, variant_id, is_retracted")
            .eq("entity_id", entity_id)
            .eq("size_before", old_size)
            .eq("size_after", new_size)
            .eq("is_retracted", False)
            .order("observed_date")
            .limit(1)
            .execute())
    return resp.data[0] if resp.data else None


def _claim_already_in_summary(summary: Any, claim_id: str) -> bool:
    if not isinstance(summary, list):
        return False
    for entry in summary:
        if isinstance(entry, dict) and str(entry.get("claim_id")) == str(claim_id):
            return True
    return False


def cleanup(sb, dry_run: bool = False) -> Dict[str, int]:
    stats = {
        "scanned": 0,
        "folded_into_event": 0,        # 30 of 34 in current data
        "already_in_evidence": 0,      # idempotent re-run case
        "entity_cleared_for_retry": 0, # 4 of 34: no matching event exists yet
        "unmatched_no_size": 0,        # missing sizes — can't fold or promote
        "errors": 0,
    }

    claims = _fetch_stuck_with_entity(sb)
    LOG.info("Found %d approved claims with matched_entity_id set", len(claims))

    for c in claims:
        stats["scanned"] += 1
        try:
            old_size = c.get("old_size")
            new_size = c.get("new_size")

            # No sizes: demote to unmatched, can't recover.
            if old_size is None or new_size is None:
                if dry_run:
                    LOG.info("[DRY] claim %s (no sizes): would set status='unmatched'", c["id"])
                else:
                    (sb.table("claims")
                     .update({"status": "unmatched"})
                     .eq("id", c["id"])
                     .execute())
                stats["unmatched_no_size"] += 1
                continue

            event = _find_existing_event(sb, c["matched_entity_id"], old_size, new_size)

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
                             "status='evidence'", c["id"], event["id"])
                else:
                    update_payload = {"status": "evidence"}
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
                update_payload = {"status": "evidence"}
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
