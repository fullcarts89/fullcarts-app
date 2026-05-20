#!/usr/bin/env python3
"""Auto-triage the data_quality_flags queue.

The backfill (PR #93) populated 1,119 historical flags. Hand-resolving
all of them would take hours. This script auto-actions the high-
confidence subset and leaves judgment calls for human review, marking
each handled flag resolved with `resolved_by='auto_triage_v1'` and a
short note explaining what was done.

Decision rules (deliberately conservative — anything ambiguous is left):

  fuzzy_brand_collision     → merge_entities(source, target)
                              Same logic as /admin/duplicates batch.
                              Idempotent: skips if either side already
                              retracted.
  sku_mashup severity=high  → set_entity_retracted(entity_id, true)
                              Spread > 10× = different SKUs collapsed
                              into one entity. Retract; admin can split
                              and restore manually later. Claims stay
                              matched (linked but hidden).
  size_outlier severity=high → retract the event + reset backing claims
                              to pending. Ratios outside [0.1, 5.0] are
                              unit errors; the underlying claims need to
                              be re-reviewed by admin.
  short_brand, no events    → set_entity_retracted(entity_id, true)
                              "Poor" / "Unknown" entities with zero
                              attached events are AI extraction garbage.

Left for human review:
  short_brand WITH events   — entity has real claim data behind a wrong
                              brand string; rename vs retract is judgment.
  sku_mashup severity=med   — 3-10× spread can be legit pack-size variants.
  size_outlier severity=med — Quality Street 137ct→67ct is real shrinkage
                              with 23 sources and falls in this band.
  mixed_units (all)         — picking the canonical unit needs source
                              inspection.
  stuck_approved_claim      — never auto-acted; needs admin to look at
                              why promote_claims can't resolve.

All actions are reversible per-row via /admin/entities. Resolved flags
remain in the queue (under the Resolved tab) so the audit trail stays
intact.

Usage:
    python -m pipeline.scripts.auto_triage_quality_flags --dry-run
    python -m pipeline.scripts.auto_triage_quality_flags
"""
import argparse
import logging
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("auto_triage_quality_flags")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000
ACTOR = "auto_triage_v1"


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


def _entity_event_counts(sb) -> Dict[str, int]:
    """Per-entity count of non-retracted published_changes. Needed for
    the short_brand 'has events' check."""
    counts: Dict[str, int] = defaultdict(int)
    offset = 0
    while True:
        resp = (
            sb.table("published_changes")
            .select("entity_id")
            .eq("is_retracted", False)
            .not_.is_("entity_id", "null")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        for r in batch:
            eid = r.get("entity_id")
            if eid:
                counts[eid] += 1
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return dict(counts)


def _entity_retraction_state(sb, entity_ids: List[str]) -> Dict[str, bool]:
    """{entity_id: is_retracted} for a batch of ids. Chunked to fit
    PostgREST's `in.()` URL limit."""
    out: Dict[str, bool] = {}
    for i in range(0, len(entity_ids), 200):
        chunk = entity_ids[i : i + 200]
        resp = (
            sb.table("product_entities")
            .select("id, is_retracted")
            .in_("id", chunk)
            .execute()
        )
        for r in resp.data or []:
            out[r["id"]] = bool(r.get("is_retracted"))
    return out


# ────────────────────────────── decision rules ──────────────────────────────


def decide(
    flag: Dict[str, Any],
    *,
    entity_event_count: int,
    source_retracted: bool,
    target_retracted: bool,
) -> Tuple[str, str]:
    """Return (action, reason) where action is one of:
      'merge'                 — merge_entities(source, target)
      'retract_entity'        — set_entity_retracted(entity_id, true)
      'retract_event'         — set event retracted + reset claims
      'leave'                 — no auto-action; human review
      'skip_already_done'     — the target row is already retracted

    Pure function: tests can drive it without DB.
    """
    kind = flag.get("flag_kind")
    sev = flag.get("severity")

    if kind == "fuzzy_brand_collision":
        if source_retracted or target_retracted:
            return "skip_already_done", "source or target already retracted"
        return "merge", "merge source into target"

    if kind == "sku_mashup":
        if sev == "high":
            return "retract_entity", "size spread > 10× — almost certainly SKU mash-up"
        return "leave", "spread 3-10× may be legit pack-size variants"

    if kind == "size_outlier":
        if sev == "high":
            return "retract_event", "ratio outside [0.1, 5.0] — almost certainly unit-parse error"
        return "leave", "ratio in band that includes legit large shrinks"

    if kind == "short_brand":
        if entity_event_count == 0:
            return "retract_entity", "placeholder brand with zero attached events"
        return "leave", "placeholder brand BUT has events — needs admin rename vs retract decision"

    if kind == "mixed_units":
        return "leave", "picking canonical unit requires source inspection"

    if kind == "stuck_approved_claim":
        return "leave", "needs admin to investigate why promote_claims can't resolve"

    return "leave", f"unknown flag_kind {kind!r}"


# ────────────────────────────── action runners ──────────────────────────────


def _do_merge(sb, flag: Dict[str, Any]) -> Dict[str, int]:
    """Apply merge_entities RPC."""
    detail = flag.get("detail") or {}
    source_id = flag.get("entity_id")
    target_id = detail.get("target_id")
    if not source_id or not target_id:
        raise ValueError("merge requires entity_id + detail.target_id")
    resp = sb.rpc(
        "merge_entities",
        {
            "p_source_id": source_id,
            "p_target_id": target_id,
            "p_merged_by": ACTOR,
        },
    ).execute()
    row = (resp.data or [{}])[0]
    return {
        "claims_moved": row.get("claims_moved", 0),
        "events_moved": row.get("events_moved", 0),
        "variants_moved": row.get("variants_moved", 0),
    }


def _do_retract_entity(sb, flag: Dict[str, Any]) -> Dict[str, int]:
    """Apply set_entity_retracted RPC."""
    entity_id = flag.get("entity_id")
    if not entity_id:
        raise ValueError("retract_entity requires entity_id")
    resp = sb.rpc(
        "set_entity_retracted",
        {"p_entity_id": entity_id, "p_retracted": True},
    ).execute()
    row = (resp.data or [{}])[0]
    return {"events_affected": row.get("events_affected", 0)}


def _do_retract_event(sb, flag: Dict[str, Any]) -> Dict[str, int]:
    """Retract an event AND reset its backing claims to pending.

    Mirrors web/src/app/api/admin/retract-event/route.ts — kept in sync
    by design so /admin actions and auto-triage take the same path.
    """
    event_id = flag.get("event_id")
    if not event_id:
        raise ValueError("retract_event requires event_id")

    # 1. Load the event to find backing claims.
    ev = (
        sb.table("published_changes")
        .select("id, candidate_id, evidence_summary, is_retracted")
        .eq("id", event_id)
        .limit(1)
        .execute()
    )
    if not ev.data:
        raise ValueError(f"event {event_id} not found")
    event = ev.data[0]
    if event.get("is_retracted"):
        return {"already_retracted": 1, "claims_reset": 0}

    # 2. Collect backing claim ids.
    claim_ids: List[str] = []
    if event.get("candidate_id"):
        cand = (
            sb.table("change_candidates")
            .select("supporting_claims")
            .eq("id", event["candidate_id"])
            .limit(1)
            .execute()
        )
        if cand.data:
            claim_ids.extend(
                str(c) for c in (cand.data[0].get("supporting_claims") or [])
            )
    for entry in event.get("evidence_summary") or []:
        if isinstance(entry, dict) and entry.get("claim_id"):
            claim_ids.append(str(entry["claim_id"]))
    claim_ids = list(set(claim_ids))

    # 3. Retract the event.
    (sb.table("published_changes")
     .update({
         "is_retracted": True,
         "retracted_at": datetime.now(timezone.utc).isoformat(),
         "retraction_reason": f"auto-triaged by {ACTOR}: size_outlier severity=high",
     })
     .eq("id", event_id)
     .execute())

    # 4. Reset backing claims to pending.
    if claim_ids:
        (sb.table("claims")
         .update({
             "status": "pending",
             "matched_entity_id": None,
             "matched_variant_id": None,
         })
         .in_("id", claim_ids)
         .execute())

    return {"already_retracted": 0, "claims_reset": len(claim_ids)}


def _resolve_flag(sb, flag_id: str, note: str) -> None:
    (sb.table("data_quality_flags")
     .update({
         "resolved_at": datetime.now(timezone.utc).isoformat(),
         "resolved_by": ACTOR,
         "resolution_note": f"auto-triaged v1: {note}",
     })
     .eq("id", flag_id)
     .is_("resolved_at", None)
     .execute())


# ────────────────────────────── main ──────────────────────────────


def run(sb, dry_run: bool) -> Dict[str, Any]:
    flags = _paginate_open_flags(sb)
    LOG.info("Loaded %d open flags", len(flags))

    # Bulk lookups: per-entity event counts (for short_brand 'has events'),
    # and is_retracted state for every entity referenced by a fuzzy merge.
    LOG.info("Loading per-entity event counts…")
    event_counts = _entity_event_counts(sb)
    LOG.info("  %d entities have events", len(event_counts))

    merge_entity_ids: List[str] = []
    for f in flags:
        if f.get("flag_kind") == "fuzzy_brand_collision":
            if f.get("entity_id"):
                merge_entity_ids.append(f["entity_id"])
            target_id = (f.get("detail") or {}).get("target_id")
            if isinstance(target_id, str):
                merge_entity_ids.append(target_id)
    LOG.info("Loading retraction state for %d merge participants…",
             len(set(merge_entity_ids)))
    retraction_state = _entity_retraction_state(sb, list(set(merge_entity_ids)))

    decisions: List[Tuple[Dict[str, Any], str, str]] = []
    for f in flags:
        source_id = f.get("entity_id") or ""
        target_id = (f.get("detail") or {}).get("target_id") or ""
        action, reason = decide(
            f,
            entity_event_count=event_counts.get(source_id, 0),
            source_retracted=retraction_state.get(source_id, False),
            target_retracted=retraction_state.get(target_id, False) if isinstance(target_id, str) else False,
        )
        decisions.append((f, action, reason))

    breakdown: Counter = Counter()
    for _, action, _ in decisions:
        breakdown[action] += 1
    per_kind: Dict[str, Counter] = defaultdict(Counter)
    for f, action, _ in decisions:
        per_kind[f["flag_kind"]][action] += 1

    LOG.info("Action breakdown:")
    for action, count in sorted(breakdown.items(), key=lambda kv: -kv[1]):
        LOG.info("  %-22s %d", action, count)
    LOG.info("Per-kind breakdown:")
    for kind in sorted(per_kind.keys()):
        counts = per_kind[kind]
        LOG.info("  %s", kind)
        for action, count in sorted(counts.items(), key=lambda kv: -kv[1]):
            LOG.info("    %-20s %d", action, count)

    if dry_run:
        LOG.info("Dry-run only. Re-run without --dry-run to apply.")
        return {"breakdown": dict(breakdown), "per_kind": {k: dict(v) for k, v in per_kind.items()}}

    # APPLY
    LOG.info("Applying actions…")
    applied: Counter = Counter()
    errors: List[Dict[str, str]] = []
    for f, action, reason in decisions:
        if action == "leave":
            applied["leave"] += 1
            continue
        try:
            if action == "merge":
                _do_merge(sb, f)
                _resolve_flag(sb, f["id"], reason)
                applied["merge"] += 1
            elif action == "retract_entity":
                _do_retract_entity(sb, f)
                _resolve_flag(sb, f["id"], reason)
                applied["retract_entity"] += 1
            elif action == "retract_event":
                _do_retract_event(sb, f)
                _resolve_flag(sb, f["id"], reason)
                applied["retract_event"] += 1
            elif action == "skip_already_done":
                _resolve_flag(sb, f["id"], reason)
                applied["skip_already_done"] += 1
        except Exception as exc:  # noqa: BLE001
            errors.append({"flag_id": f["id"], "action": action, "error": str(exc)})
            applied["error"] += 1
            LOG.error("Failed on flag %s (%s): %s", f["id"], action, exc)

    LOG.info("Done. Applied:")
    for k, v in sorted(applied.items(), key=lambda kv: -kv[1]):
        LOG.info("  %-22s %d", k, v)
    if errors:
        LOG.info("First 5 errors:")
        for e in errors[:5]:
            LOG.info("  %s", e)

    return {
        "breakdown": dict(breakdown),
        "per_kind": {k: dict(v) for k, v in per_kind.items()},
        "applied": dict(applied),
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Decide and report without applying any changes.",
    )
    args = parser.parse_args()

    sb = _get_client()
    LOG.info("Mode: %s", "DRY-RUN (no writes)" if args.dry_run else "APPLY")
    run(sb, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
