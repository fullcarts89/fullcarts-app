#!/usr/bin/env python3
"""Read-only audit of the historic auto-approve cohort.

The auto_approve_claims.py cron lived from PR #61 (May 15) to PR #70
(May 17). Most claims it approved had to clear hard filters — image
required, CPG-unit allowlist, sub-score floors at 0.85 / 0.85 / 0.80 —
but the user may want a post-hoc sweep to catch any low-quality events
that slipped through. This script:

  1. Reconstructs the historic filter exactly (logic copied verbatim
     from the deleted auto_approve_claims.py at commit 6e561ec^).
  2. Walks every claim through the filter. The result is the
     "would-have-been-approved cohort" — a superset of what actually
     got approved during the May 15-17 window plus anything that
     would clear it today.
  3. For each cohort claim, joins to its downstream published_change
     via matched_entity_id + (old_size, new_size) and emits a CSV row.

The CSV is the workflow artefact: open in a spreadsheet, sort by
evidence_count ASC + size_delta_pct DESC, scan for anything that looks
like AI hallucination, then use the /admin/entities retract button or
the /admin/claims send-back-to-pending flow on the public site to
clean it up. No mutations from this script.

Usage:
    python -m pipeline.scripts.audit_auto_approved             # prints to stdout
    python -m pipeline.scripts.audit_auto_approved -o audit.csv
    python -m pipeline.scripts.audit_auto_approved --threshold 90  # default

Threshold note: the production cron used --threshold 90 (per the
pipeline_promote.yml workflow). The auto_approve_claims.py default
was 80; the workflow always overrode it. Default here is 90 to
match what actually ran.
"""
import argparse
import csv
import logging
import os
import sys
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("audit_auto_approved")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 500
DEFAULT_THRESHOLD = 90.0

# Verbatim from the deleted auto_approve_claims.py (commit 6e561ec^).
_ALLOWED_UNITS = frozenset({
    "g", "kg", "mg", "oz", "lb",
    "ml", "l", "fl oz",
    "ct", "count", "pack",
})
_MIN_BRAND_SCORE = 0.85
_MIN_SIZE_CHANGE_SCORE = 0.85
_MIN_PRODUCT_NAME_SCORE = 0.80


def _passes_hard_filters(claim: Dict[str, Any]) -> Optional[str]:
    """Return None if the claim would have passed all hard filters,
    else a short reason string."""
    if not claim.get("image_storage_path"):
        return "no image"
    unit = (claim.get("old_size_unit") or "").strip().lower()
    if unit not in _ALLOWED_UNITS:
        return "unit {!r} not in CPG allowlist".format(claim.get("old_size_unit"))
    scores = claim.get("confidence") or {}
    if not isinstance(scores, dict):
        return "missing sub-scores"
    for key, floor in (
        ("brand", _MIN_BRAND_SCORE),
        ("size_change", _MIN_SIZE_CHANGE_SCORE),
        ("product_name", _MIN_PRODUCT_NAME_SCORE),
    ):
        val = scores.get(key)
        if val is None or float(val) < floor:
            return "{} sub-score {} < {}".format(key, val, floor)
    return None


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_candidate_claims(sb, threshold: float) -> List[Dict[str, Any]]:
    """Pull every claim whose overall confidence clears the threshold.

    Status doesn't matter — we want both the ones currently in matched /
    evidence (the actual cohort) AND any pending ones that would clear
    today's filter. Caller filters further via hard-filter check.
    """
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        resp = (
            sb.table("claims")
            .select(
                "id, brand, product_name, status, confidence, "
                "old_size, old_size_unit, new_size, new_size_unit, "
                "matched_entity_id, matched_variant_id, image_storage_path, "
                "raw_item_id, extracted_at, observed_date"
            )
            .gte("confidence->>overall", str(threshold))
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        out.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def _fetch_raw_item_urls(sb, raw_item_ids: List[str]) -> Dict[str, str]:
    """Batch-fetch source_url for the cohort's raw items so the CSV has
    a clickable link per row."""
    out: Dict[str, str] = {}
    for i in range(0, len(raw_item_ids), 200):
        chunk = raw_item_ids[i : i + 200]
        resp = (
            sb.table("raw_items")
            .select("id, source_url")
            .in_("id", chunk)
            .execute()
        )
        for r in resp.data or []:
            url = r.get("source_url")
            if url:
                out[r["id"]] = url
    return out


def _fetch_events(sb, claims: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """For each cohort claim, look up the published_change that documents
    its (entity_id, size_before, size_after) tuple. Returns
    {claim_id: event_dict} for the matches.

    Claims with no matched_entity_id or no published_change get omitted —
    the caller handles the missing case with defaults in the CSV row.
    """
    out: Dict[str, Dict[str, Any]] = {}
    # Group by entity so we minimize round-trips.
    by_entity: Dict[str, List[Dict[str, Any]]] = {}
    for c in claims:
        eid = c.get("matched_entity_id")
        if eid:
            by_entity.setdefault(eid, []).append(c)
    entity_ids = list(by_entity.keys())
    for i in range(0, len(entity_ids), 100):
        chunk = entity_ids[i : i + 100]
        resp = (
            sb.table("published_changes")
            .select(
                "id, entity_id, size_before, size_after, size_delta_pct, "
                "change_type, severity, evidence_count, is_retracted, "
                "observed_date"
            )
            .in_("entity_id", chunk)
            .execute()
        )
        # Index events by (entity_id, size_before, size_after) so we can
        # join each claim to its event in O(1).
        idx: Dict[tuple, Dict[str, Any]] = {}
        for e in resp.data or []:
            key = (str(e["entity_id"]), float(e["size_before"]), float(e["size_after"]))
            idx[key] = e
        for eid, claim_group in by_entity.items():
            if i <= entity_ids.index(eid) < i + 100:
                for c in claim_group:
                    try:
                        key = (
                            str(c["matched_entity_id"]),
                            float(c["old_size"]) if c.get("old_size") is not None else None,
                            float(c["new_size"]) if c.get("new_size") is not None else None,
                        )
                    except (TypeError, ValueError):
                        continue
                    event = idx.get(key)
                    if event:
                        out[c["id"]] = event
    return out


def audit(sb, threshold: float, output_path: Optional[str]) -> Dict[str, int]:
    LOG.info("Threshold: overall confidence >= %s%%", threshold)
    LOG.info("Hard filters: image required, CPG unit allowlist, sub-scores "
             "(brand >= %s, size_change >= %s, product_name >= %s)",
             _MIN_BRAND_SCORE, _MIN_SIZE_CHANGE_SCORE, _MIN_PRODUCT_NAME_SCORE)

    candidates = _fetch_candidate_claims(sb, threshold)
    LOG.info("Pulled %d claims clearing the overall threshold", len(candidates))

    cohort: List[Dict[str, Any]] = []
    for c in candidates:
        reason = _passes_hard_filters(c)
        if reason is None:
            cohort.append(c)
    LOG.info("After hard filters: %d cohort claims", len(cohort))

    # Bulk-fetch source URLs and downstream events.
    raw_ids = list({c["raw_item_id"] for c in cohort if c.get("raw_item_id")})
    url_map = _fetch_raw_item_urls(sb, raw_ids)
    event_map = _fetch_events(sb, cohort)

    out_fh = open(output_path, "w", newline="") if output_path else sys.stdout
    writer = csv.writer(out_fh)
    writer.writerow([
        "claim_id", "claim_status", "confidence_overall",
        "brand", "product_name",
        "old_size", "old_unit", "new_size", "new_unit",
        "size_delta_pct",
        "event_id", "event_evidence_count", "event_is_retracted",
        "observed_date", "extracted_at", "source_url",
    ])
    rows_written = 0
    for c in cohort:
        ev = event_map.get(c["id"]) or {}
        scores = c.get("confidence") or {}
        overall = scores.get("overall") if isinstance(scores, dict) else None
        writer.writerow([
            c["id"],
            c.get("status") or "",
            overall if overall is not None else "",
            c.get("brand") or "",
            c.get("product_name") or "",
            c.get("old_size") if c.get("old_size") is not None else "",
            c.get("old_size_unit") or "",
            c.get("new_size") if c.get("new_size") is not None else "",
            c.get("new_size_unit") or "",
            ev.get("size_delta_pct") if ev else "",
            ev.get("id") or "",
            ev.get("evidence_count") if ev else "",
            "true" if ev.get("is_retracted") else "false",
            ev.get("observed_date") or c.get("observed_date") or "",
            c.get("extracted_at") or "",
            url_map.get(c.get("raw_item_id", "")) or "",
        ])
        rows_written += 1
    if output_path:
        out_fh.close()
        LOG.info("Wrote %d rows to %s", rows_written, output_path)
    else:
        LOG.info("Wrote %d rows to stdout", rows_written)

    return {
        "candidates_over_threshold": len(candidates),
        "cohort_after_hard_filters": len(cohort),
        "with_published_change": sum(1 for c in cohort if c["id"] in event_map),
        "rows_written": rows_written,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Read-only audit of the historic auto-approve cohort."
    )
    parser.add_argument(
        "--threshold", type=float, default=DEFAULT_THRESHOLD,
        help="Overall confidence threshold in 0-100 (default 90, matches "
             "the value the cron actually ran)",
    )
    parser.add_argument(
        "-o", "--output", type=str, default=None,
        help="CSV output path. Defaults to stdout.",
    )
    args = parser.parse_args()

    sb = _get_client()
    stats = audit(sb, args.threshold, args.output)
    LOG.info("Done. Stats:")
    for k, v in stats.items():
        LOG.info("  %s: %d", k, v)


if __name__ == "__main__":
    main()
