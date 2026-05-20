#!/usr/bin/env python3
"""Bulk revert: for every open data_quality_flag, hide the offending row
and send its backing claims to admin Pending for re-review.

Companion to auto_triage_quality_flags.py. That script ran the
high-confidence subset of flags through their per-kind actions (merge,
retract_entity, retract_event) and left 278 flags marked 'leave' for
manual review. This script handles those remaining flags in bulk when
admin doesn't have time to triage each one by hand.

Per-flag action rules:

  entity_id flag → set_entity_retracted(true) + reset all the entity's
                   claims to status='pending', clearing matched_*_id.
                   Used for: mixed_units, sku_mashup (any severity),
                   short_brand with events.

  event_id flag  → set published_changes.is_retracted=true + reset all
                   backing claims (originator + fold-ins) to pending.
                   Same logic as the public-page "↩ Send to pending"
                   button and the auto_triage retract_event branch.
                   Used for: size_outlier (any severity).

  claim_id flag  → set the claim itself to status='pending', clearing
                   matched_*_id. Used for stuck_approved_claim flags.

Each flag is marked resolved with `resolution_note='user-directed bulk
revert v1: sent to pending for re-review'` and `resolved_by=
'revert_remaining_v1'`.

Reversibility: every action is reversible via the corresponding admin
surface (entity retract, event retract, claim status change). Audit
trails are intact across entity_merge_log / claim_status_log /
data_quality_flags itself.

Usage:
    python -m pipeline.scripts.revert_remaining_flags_to_pending --dry-run
    python -m pipeline.scripts.revert_remaining_flags_to_pending
"""
import argparse
import logging
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

LOG = logging.getLogger("revert_remaining_flags")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000
ACTOR = "revert_remaining_v1"


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _paginate_open_flags(sb) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        resp = (
            sb.table("data_quality_flags")
            .select("id, claim_id, entity_id, event_id, flag_kind, severity, detail")
            .is_("resolved_at", None)
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        out.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


# ────────────────────────────── action runners ──────────────────────────────


def _revert_entity(sb, entity_id: str) -> Dict[str, int]:
    """Retract the entity (cascades to events) and send all its claims
    to pending."""
    # Skip the RPC if already retracted to avoid duplicate audit-log rows.
    cur = (sb.table("product_entities")
           .select("is_retracted")
           .eq("id", entity_id)
           .limit(1)
           .execute())
    if not cur.data:
        raise ValueError(f"entity {entity_id} not found")
    already_retracted = bool(cur.data[0].get("is_retracted"))

    if not already_retracted:
        sb.rpc(
            "set_entity_retracted",
            {"p_entity_id": entity_id, "p_retracted": True},
        ).execute()

    # Reset every claim attached to this entity. PostgREST returns the
    # updated rows by default (Prefer: return=representation), so
    # resp.data length gives us the affected count without a separate
    # SELECT call. We don't bother filtering already-pending rows — the
    # update is a no-op write on those.
    upd = (sb.table("claims")
           .update({
               "status": "pending",
               "matched_entity_id": None,
               "matched_variant_id": None,
           })
           .eq("matched_entity_id", entity_id)
           .execute())
    claims_reset = len(upd.data or [])
    return {"already_retracted": int(already_retracted), "claims_reset": claims_reset}


def _revert_event(sb, event_id: str) -> Dict[str, int]:
    """Retract the event and send backing claims to pending. Mirrors
    web/src/app/api/admin/retract-event/route.ts."""
    ev = (sb.table("published_changes")
          .select("id, candidate_id, evidence_summary, is_retracted")
          .eq("id", event_id)
          .limit(1)
          .execute())
    if not ev.data:
        raise ValueError(f"event {event_id} not found")
    event = ev.data[0]
    if event.get("is_retracted"):
        return {"already_retracted": 1, "claims_reset": 0}

    # Collect backing claim ids.
    claim_ids: List[str] = []
    if event.get("candidate_id"):
        cand = (sb.table("change_candidates")
                .select("supporting_claims")
                .eq("id", event["candidate_id"])
                .limit(1)
                .execute())
        if cand.data:
            claim_ids.extend(str(c) for c in (cand.data[0].get("supporting_claims") or []))
    for entry in event.get("evidence_summary") or []:
        if isinstance(entry, dict) and entry.get("claim_id"):
            claim_ids.append(str(entry["claim_id"]))
    claim_ids = list(set(claim_ids))

    (sb.table("published_changes")
     .update({
         "is_retracted": True,
         "retracted_at": datetime.now(timezone.utc).isoformat(),
         "retraction_reason": f"reverted by {ACTOR}: bulk send-to-pending of remaining quality flags",
     })
     .eq("id", event_id)
     .execute())

    claims_reset = 0
    if claim_ids:
        upd = (sb.table("claims")
               .update({
                   "status": "pending",
                   "matched_entity_id": None,
                   "matched_variant_id": None,
               })
               .in_("id", claim_ids)
               .execute())
        claims_reset = len(upd.data or [])

    return {"already_retracted": 0, "claims_reset": claims_reset}


def _revert_claim(sb, claim_id: str) -> Dict[str, int]:
    """Flip the claim itself back to pending."""
    upd = (sb.table("claims")
           .update({
               "status": "pending",
               "matched_entity_id": None,
               "matched_variant_id": None,
           })
           .eq("id", claim_id)
           .execute())
    return {"claims_reset": len(upd.data or [])}


def _resolve_flag(sb, flag_id: str) -> None:
    (sb.table("data_quality_flags")
     .update({
         "resolved_at": datetime.now(timezone.utc).isoformat(),
         "resolved_by": ACTOR,
         "resolution_note": "user-directed bulk revert v1: sent to pending for re-review",
     })
     .eq("id", flag_id)
     .is_("resolved_at", None)
     .execute())


# ────────────────────────────── main ──────────────────────────────


def run(sb, dry_run: bool) -> Dict[str, Any]:
    flags = _paginate_open_flags(sb)
    LOG.info("Loaded %d open flags", len(flags))

    # Bucket by target type for the dry-run preview.
    buckets: Counter = Counter()
    per_kind: Dict[str, Counter] = defaultdict(Counter)
    for f in flags:
        if f.get("entity_id"):
            buckets["entity"] += 1
            per_kind[f["flag_kind"]]["entity"] += 1
        elif f.get("event_id"):
            buckets["event"] += 1
            per_kind[f["flag_kind"]]["event"] += 1
        elif f.get("claim_id"):
            buckets["claim"] += 1
            per_kind[f["flag_kind"]]["claim"] += 1
        else:
            buckets["unknown"] += 1
    LOG.info("Action breakdown:")
    for action, count in sorted(buckets.items(), key=lambda kv: -kv[1]):
        LOG.info("  %-22s %d", action, count)
    LOG.info("Per-kind breakdown:")
    for kind in sorted(per_kind.keys()):
        targets = per_kind[kind]
        LOG.info("  %s", kind)
        for tgt, count in sorted(targets.items(), key=lambda kv: -kv[1]):
            LOG.info("    %-20s %d", tgt, count)

    if dry_run:
        LOG.info("Dry-run only. Re-run without --dry-run to apply.")
        return {"buckets": dict(buckets), "per_kind": {k: dict(v) for k, v in per_kind.items()}}

    LOG.info("Applying reverts…")
    applied: Counter = Counter()
    totals: Counter = Counter()
    errors: List[Dict[str, str]] = []
    for f in flags:
        try:
            if f.get("entity_id"):
                result = _revert_entity(sb, f["entity_id"])
                _resolve_flag(sb, f["id"])
                applied["entity_reverted"] += 1
                totals["claims_reset"] += result.get("claims_reset", 0)
            elif f.get("event_id"):
                result = _revert_event(sb, f["event_id"])
                _resolve_flag(sb, f["id"])
                applied["event_reverted"] += 1
                totals["claims_reset"] += result.get("claims_reset", 0)
            elif f.get("claim_id"):
                result = _revert_claim(sb, f["claim_id"])
                _resolve_flag(sb, f["id"])
                applied["claim_reverted"] += 1
                totals["claims_reset"] += result.get("claims_reset", 0)
            else:
                applied["unknown"] += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"flag_id": f["id"], "error": str(exc)})
            applied["error"] += 1
            LOG.error("Failed on flag %s: %s", f["id"], exc)

    LOG.info("Done. Applied:")
    for k, v in sorted(applied.items(), key=lambda kv: -kv[1]):
        LOG.info("  %-22s %d", k, v)
    LOG.info("Totals:")
    for k, v in sorted(totals.items(), key=lambda kv: -kv[1]):
        LOG.info("  %-22s %d", k, v)
    if errors:
        LOG.info("First 5 errors:")
        for e in errors[:5]:
            LOG.info("  %s", e)

    return {
        "buckets": dict(buckets),
        "per_kind": {k: dict(v) for k, v in per_kind.items()},
        "applied": dict(applied),
        "totals": dict(totals),
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Bucket + count remaining flags without writing anything.",
    )
    args = parser.parse_args()

    sb = _get_client()
    LOG.info("Mode: %s", "DRY-RUN (no writes)" if args.dry_run else "APPLY")
    run(sb, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
