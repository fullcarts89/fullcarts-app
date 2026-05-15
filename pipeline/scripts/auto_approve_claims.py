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
from typing import Any, Dict, List, Optional, Tuple

LOG = logging.getLogger("auto_approve_claims")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 500
DEFAULT_CONFIDENCE_THRESHOLD = 80

# Hard filters layered on top of the overall confidence threshold. A claim
# that fails ANY of these stays in `pending` for manual review even if its
# overall confidence beats the bar.

# Standard CPG packaging units. Anything outside this set (e.g. "in" for
# Little Caesars pizza diameter, "ft" for paper-towel rolls) is restaurant /
# dimensional / oddball — we route those to manual review since shrinkflation
# auto-approval should stay CPG-focused. Matching is case-insensitive and
# tolerant of whitespace, but the canonical unit string must exactly match.
_ALLOWED_UNITS = frozenset({
    # mass
    "g", "kg", "mg", "oz", "lb",
    # volume
    "ml", "l", "fl oz",
    # count
    "ct", "count", "pack",
})

# Minimum sub-score requirements (each on 0-1 scale).
_MIN_BRAND_SCORE = 0.85
_MIN_SIZE_CHANGE_SCORE = 0.85
_MIN_PRODUCT_NAME_SCORE = 0.80


def _passes_hard_filters(claim: Dict[str, Any]) -> Optional[str]:
    """Return None if the claim passes all hard filters, else a reason string.

    Used both for filtering and for surfacing why borderline claims were
    skipped (visible in the dry-run / job-summary output).
    """
    # 1. Image required — every legit shrinkflation claim has visual evidence
    #    archived to Supabase Storage (claim-images bucket).
    if not claim.get("image_storage_path"):
        return "no image"

    # 2. Standard CPG units only.
    unit = (claim.get("old_size_unit") or "").strip().lower()
    if unit not in _ALLOWED_UNITS:
        return "unit {!r} not in CPG allowlist".format(claim.get("old_size_unit"))

    # 3. Sub-score floors.
    scores = claim.get("confidence") or {}
    if not isinstance(scores, dict):
        return "missing sub-scores"
    brand_s = scores.get("brand")
    size_s = scores.get("size_change")
    name_s = scores.get("product_name")
    if brand_s is None or float(brand_s) < _MIN_BRAND_SCORE:
        return "brand sub-score {} < {}".format(brand_s, _MIN_BRAND_SCORE)
    if size_s is None or float(size_s) < _MIN_SIZE_CHANGE_SCORE:
        return "size_change sub-score {} < {}".format(size_s, _MIN_SIZE_CHANGE_SCORE)
    if name_s is None or float(name_s) < _MIN_PRODUCT_NAME_SCORE:
        return "product_name sub-score {} < {}".format(name_s, _MIN_PRODUCT_NAME_SCORE)

    return None


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_eligible_claims(
    sb,
    threshold: float,
) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict[str, Any], str]]]:
    """Fetch pending claims and split them into auto-approvable vs near-misses.

    `confidence` is a JSONB column with sub-keys {overall, brand, size_change,
    product_name} on a 0-1 scale. We filter on `overall` >= threshold, then
    apply hard filters (`_passes_hard_filters`).

    Returns:
        (eligible, near_misses) — eligible passes everything;
        near_misses passed the overall threshold but failed a hard filter
        (so they get surfaced in the summary as "would have approved if X").
    """
    eligible = []  # type: List[Dict[str, Any]]
    near_misses = []  # type: List[Tuple[Dict[str, Any], str]]
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
            if overall is None or float(overall) < threshold:
                continue
            reason = _passes_hard_filters(claim)
            if reason is None:
                eligible.append(claim)
            else:
                near_misses.append((claim, reason))
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return eligible, near_misses


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
    eligible, near_misses = _fetch_eligible_claims(sb, threshold)

    if args.limit > 0:
        eligible = eligible[:args.limit]

    LOG.info(
        "Found %d eligible claims for auto-approval (%d near-misses kept for manual review)",
        len(eligible), len(near_misses),
    )

    if not eligible and not near_misses:
        LOG.info("No claims meet the criteria. Try lowering --threshold.")
        return

    # Show breakdown by source
    by_source = {}  # type: Dict[str, int]
    for c in eligible:
        src = c.get("source_type", "unknown")
        by_source[src] = by_source.get(src, 0) + 1
    if by_source:
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
        _write_summary(eligible, threshold, mode="dry-run", near_misses=near_misses)
        return

    if not eligible:
        # All eligibles got filtered out; only near-misses remain.
        LOG.info("No claims passed the hard filters.")
        _write_summary(eligible, threshold, mode="live", near_misses=near_misses)
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
        _write_summary(eligible, threshold, mode="approve-only", near_misses=near_misses)
        return

    # Run promotion on newly approved claims
    LOG.info("Promoting newly approved claims...")
    from pipeline.scripts.promote_claims import (
        fetch_approved_claims,
        promote_claims,
    )
    claims_to_promote = fetch_approved_claims(sb)
    LOG.info("Found %d approved claims to promote", len(claims_to_promote))

    promotion_stats = {}  # type: Dict[str, int]
    if claims_to_promote:
        promotion_stats = promote_claims(sb, claims_to_promote)
        LOG.info("Promotion results:")
        for k, v in promotion_stats.items():
            LOG.info("  %s: %d", k, v)

    _write_summary(
        eligible, threshold, mode="live",
        promotion_stats=promotion_stats, near_misses=near_misses,
    )


def _write_summary(
    eligible,            # type: List[Dict[str, Any]]
    threshold,           # type: float
    mode,                # type: str
    promotion_stats=None,  # type: Optional[Dict[str, int]]
    near_misses=None,    # type: Optional[List[Tuple[Dict[str, Any], str]]]
):
    """Write a markdown summary to GITHUB_STEP_SUMMARY and stdout.

    Captures every claim approved (or that would be approved in dry-run) so
    the daily workflow run leaves a queryable audit trail in GitHub Actions.
    """
    lines = []  # type: List[str]
    label = {
        "live": "approved + promoted",
        "approve-only": "approved (promotion skipped)",
        "dry-run": "would have been approved",
    }.get(mode, mode)

    lines.append("### Auto-Approve Claims — {}".format(label))
    lines.append("")
    lines.append("- **Threshold**: overall confidence >= {:.2f}".format(threshold))
    lines.append("- **Eligible claims**: {}".format(len(eligible)))

    if promotion_stats:
        lines.append("- **Promotion results**:")
        for k, v in promotion_stats.items():
            lines.append("  - `{}`: {}".format(k, v))

    lines.append("")
    if not eligible:
        lines.append("_No claims met the threshold._")
    else:
        lines.append("| Confidence | Brand | Product | Size change | Category |")
        lines.append("|---:|---|---|---|---|")
        # Sort by confidence desc for readability
        sorted_eligible = sorted(
            eligible,
            key=lambda c: -(
                (c.get("confidence") or {}).get("overall") or 0
                if isinstance(c.get("confidence"), dict) else 0
            ),
        )
        for c in sorted_eligible:
            conf = c.get("confidence") or {}
            ov = conf.get("overall") if isinstance(conf, dict) else None
            ov_pct = "{:.0f}%".format(float(ov) * 100) if ov is not None else "?"
            unit = c.get("old_size_unit") or ""
            size_change = "{} → {} {}".format(
                c.get("old_size", "?"),
                c.get("new_size", "?"),
                unit,
            ).strip()
            lines.append("| {} | {} | {} | {} | {} |".format(
                ov_pct,
                (c.get("brand") or "?").replace("|", "\\|"),
                (c.get("product_name") or "?").replace("|", "\\|"),
                size_change,
                c.get("category") or "—",
            ))

    # Surface near-misses (passed overall threshold but failed a hard filter)
    # so the reviewer can quickly spot what was kicked back to manual review.
    if near_misses:
        lines.append("")
        lines.append("#### Near-misses ({}) — sent to manual review".format(len(near_misses)))
        lines.append("")
        lines.append("| Confidence | Brand | Product | Size change | Rejected because |")
        lines.append("|---:|---|---|---|---|")
        for c, reason in sorted(
            near_misses,
            key=lambda x: -(
                (x[0].get("confidence") or {}).get("overall") or 0
                if isinstance(x[0].get("confidence"), dict) else 0
            ),
        ):
            conf = c.get("confidence") or {}
            ov = conf.get("overall") if isinstance(conf, dict) else None
            ov_pct = "{:.0f}%".format(float(ov) * 100) if ov is not None else "?"
            unit = c.get("old_size_unit") or ""
            size_change = "{} → {} {}".format(
                c.get("old_size", "?"),
                c.get("new_size", "?"),
                unit,
            ).strip()
            lines.append("| {} | {} | {} | {} | {} |".format(
                ov_pct,
                (c.get("brand") or "?").replace("|", "\\|"),
                (c.get("product_name") or "?").replace("|", "\\|"),
                size_change,
                reason.replace("|", "\\|"),
            ))

    summary_md = "\n".join(lines)

    # Write to GitHub Actions step summary if available
    gh_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if gh_summary_path:
        try:
            with open(gh_summary_path, "a", encoding="utf-8") as fh:
                fh.write(summary_md + "\n\n")
        except OSError as exc:
            LOG.warning("Could not write to GITHUB_STEP_SUMMARY: %s", exc)

    # Also print to stdout so it's visible in local runs and console logs
    LOG.info("\n%s", summary_md)


if __name__ == "__main__":
    main()
