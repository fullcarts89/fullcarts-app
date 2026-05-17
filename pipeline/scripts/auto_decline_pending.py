#!/usr/bin/env python3
"""Auto-decline pending claims that don't meet quality bar.

Rules:
- News/GDELT claims with no brand or no size/price change -> discarded
- Reddit claims with no image in raw_payload -> discarded
- Open Food Facts claims with no before AND after size -> discarded
  (OFF rows are catalog metadata, not user-reported shrinkflation; they only
   become real claims if extraction wrote both old_size AND new_size.)

Designed to be idempotent and safe to run on a daily cron. Writes a markdown
summary to GITHUB_STEP_SUMMARY (and stdout) so each run leaves an audit trail.

Usage:
    python -m pipeline.scripts.auto_decline_pending [--dry-run]
"""
import argparse
import os
from typing import Any, Dict, List, Optional, Set, Tuple

from pipeline.lib.image_archiver import extract_image_url
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("auto_decline_pending")

PAGE_SIZE = 1000


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Auto-decline low-quality pending claims"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be declined without updating",
    )
    args = parser.parse_args()

    client = get_client()

    # Fetch all pending claims with their raw_items
    pending_claims = _fetch_pending_claims_with_raw(client)
    log.info("Found %d pending claims to evaluate", len(pending_claims))

    to_decline = []  # type: List[str]
    # reason_counts buckets the rule that caused each decline. Surfaces in
    # the summary so the founder can see what kinds of junk got cleared.
    reason_counts = {}  # type: Dict[str, int]

    def _flag(claim_id, reason):
        # type: (str, str) -> None
        to_decline.append(claim_id)
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

    for claim in pending_claims:
        raw = claim.get("raw_items") or {}
        source_type = raw.get("source_type", "")
        payload = raw.get("raw_payload", {})

        if source_type in ("news", "gdelt"):
            brand = claim.get("brand")
            if not brand:
                _flag(claim["id"], "{}: no brand".format(source_type))
                continue
            has_size = claim.get("old_size") is not None and claim.get("new_size") is not None
            has_price = claim.get("old_price") is not None and claim.get("new_price") is not None
            if not has_size and not has_price:
                _flag(claim["id"], "{}: no size or price change".format(source_type))
                continue

        if source_type == "reddit":
            image_url = extract_image_url(payload)
            if not image_url:
                _flag(claim["id"], "reddit: no image")
                continue

        if source_type == "openfoodfacts":
            # OFF entries are catalog records, not user-reported shrinkflation.
            # They only become real claims if extraction wrote both old AND new
            # sizes (i.e. the entry actually documents a size change). Without
            # both, the row is just product metadata — discard.
            if claim.get("old_size") is None or claim.get("new_size") is None:
                _flag(claim["id"], "openfoodfacts: missing before/after size")
                continue

        if source_type == "kroger_change":
            # v1 analyzer fired on any adjacent-week size delta ≥2%, which
            # produced almost-pure noise from Kroger's API toggling between
            # two size representations for the same SKU (14oz ↔ 8oz week to
            # week). v2 adds oscillation and unit-stability guards; until a
            # claim is stamped with v2+ extractor_version we treat it as junk.
            ev = claim.get("extractor_version") or ""
            if ev == "kroger-change-v1" or ev.startswith("kroger-change-v0"):
                _flag(claim["id"], "kroger_change: legacy v1 analyzer (noise)")
                continue

    log.info("Will decline %d of %d pending claims", len(to_decline), len(pending_claims))
    for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
        log.info("  %d × %s", count, reason)

    if args.dry_run:
        log.info("[DRY RUN] No changes made")
        _write_summary(reason_counts, len(pending_claims), mode="dry-run")
        return

    # Batch update in chunks
    batch_size = 100
    declined = 0
    for i in range(0, len(to_decline), batch_size):
        batch = to_decline[i:i + batch_size]
        try:
            client.table("claims").update(
                {"status": "discarded"}
            ).in_("id", batch).execute()
            declined += len(batch)
            log.info("Declined %d/%d", declined, len(to_decline))
        except Exception as exc:
            log.error("Failed to decline batch at offset %d: %s", i, str(exc)[:200])

    log.info("Done: declined %d claims", declined)
    _write_summary(reason_counts, len(pending_claims), mode="live", declined=declined)


def _write_summary(reason_counts, evaluated, mode, declined=None):
    # type: (Dict[str, int], int, str, Optional[int]) -> None
    """Write a markdown audit trail to GITHUB_STEP_SUMMARY (and stdout).

    Mirrors the auto_approve_claims summary format so daily workflow runs
    leave a consistent record of both sides of the decision (decline + approve).
    """
    lines = []  # type: List[str]
    label = "declined" if mode == "live" else "would decline"
    total_flagged = sum(reason_counts.values())

    lines.append("### Auto-Decline Pending Claims — {}".format(label))
    lines.append("")
    lines.append("- **Claims evaluated**: {}".format(evaluated))
    if mode == "live" and declined is not None:
        lines.append("- **Declined**: {}".format(declined))
    else:
        lines.append("- **Would decline**: {}".format(total_flagged))

    lines.append("")
    if not reason_counts:
        lines.append("_Nothing flagged for decline. Queue is clean by these rules._")
    else:
        lines.append("| Rule | Claims |")
        lines.append("|---|---:|")
        for reason, count in sorted(reason_counts.items(), key=lambda kv: -kv[1]):
            lines.append("| {} | {} |".format(reason.replace("|", "\\|"), count))

    summary_md = "\n".join(lines)

    gh_summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if gh_summary_path:
        try:
            with open(gh_summary_path, "a", encoding="utf-8") as fh:
                fh.write(summary_md + "\n\n")
        except OSError as exc:
            log.warning("Could not write to GITHUB_STEP_SUMMARY: %s", exc)

    log.info("\n%s", summary_md)


def _fetch_pending_claims_with_raw(client):
    # type: (Any) -> List[Dict[str, Any]]
    """Fetch all pending claims joined with raw_items source info."""
    all_claims = []  # type: List[Dict[str, Any]]
    offset = 0

    while True:
        resp = (
            client.table("claims")
            .select(
                "id,brand,product_name,extractor_version,"
                "old_size,new_size,old_price,new_price,"
                "raw_items(source_type,raw_payload)"
            )
            .eq("status", "pending")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        if not resp.data:
            break

        all_claims.extend(resp.data)

        if len(resp.data) < PAGE_SIZE:
            break
        offset += PAGE_SIZE

    return all_claims


if __name__ == "__main__":
    main()
