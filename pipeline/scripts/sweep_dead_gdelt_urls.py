#!/usr/bin/env python3
"""Sweep dead GDELT source URLs out of the pending claim queue.

Many GDELT-sourced claims point to URLs that 404 because the publisher
rotated old article paths (often Hearst Newspapers syndicates). These
are unverifiable evidence sitting in the review queue, so we bulk-
discard them with an audit trail in `data_quality_flags`.

For each pending claim whose backing raw_item is GDELT and has a non-null
source_url:

  - HTTP HEAD (10s timeout, custom User-Agent) the url.
  - 404 / 410 / other 4xx (NOT 401/403/429) / timeout / DNS fail / conn
    refused → mark claim discarded + raise an audit-only flag.
  - 2xx / 3xx / 401 / 403 / 429 / 5xx → leave alone (paywalls, rate-
    limits, transient server errors all count as "URL still exists").

Runs HEAD checks 10-way parallel. Expected pool ~1-2k claims → 3-5 min.

Usage:
    python -m pipeline.scripts.sweep_dead_gdelt_urls --dry-run
    python -m pipeline.scripts.sweep_dead_gdelt_urls --limit 100
    python -m pipeline.scripts.sweep_dead_gdelt_urls
"""
from __future__ import annotations

import argparse
import concurrent.futures
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import requests

from pipeline.lib import data_quality_flags

USER_AGENT = "Mozilla/5.0 (compatible; FullCartsBot/1.0)"
TIMEOUT = 10.0
WORKERS = 10
PAGE = 1000
FLAG_KIND = "dead_gdelt_source_url"
DETECTED_BY = "gdelt_url_health_sweep"

# Verdict constants used by classify_url + process_claims.
DEAD = "dead"
ALIVE = "alive"


def classify_url(url):
    # type: (str) -> Tuple[str, Optional[int], Optional[str]]
    """HEAD-check a URL. Return (verdict, status_or_None, error_or_None).

    Verdict rules (see module docstring for rationale):

      DEAD:   404, 410, any 4xx that is NOT 401/403/429,
              connection errors, DNS failures, timeouts.
      ALIVE:  2xx, 3xx, 401 (paywall), 403 (forbidden),
              429 (rate limited), 5xx (transient server error).
    """
    try:
        resp = requests.head(
            url,
            allow_redirects=True,
            timeout=TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        code = resp.status_code
        if code in (404, 410):
            return (DEAD, code, None)
        # Ambiguous 4xx (not auth / not rate-limit) → treat as dead.
        if 400 <= code < 500 and code not in (401, 403, 429):
            return (DEAD, code, None)
        return (ALIVE, code, None)
    except requests.exceptions.Timeout:
        return (DEAD, None, "timeout")
    except requests.exceptions.ConnectionError as exc:
        return (DEAD, None, "connection: {}".format(exc.__class__.__name__))
    except requests.exceptions.RequestException as exc:
        return (DEAD, None, "request: {}".format(exc.__class__.__name__))


def find_pending_gdelt_claims(sb):
    # type: (Any) -> List[Dict[str, Any]]
    """Return [{'claim_id', 'url'}] for every pending claim whose backing
    raw_item is GDELT and has a non-null source_url.

    Uses PostgREST's `raw_items!inner(...)` so the join is constrained
    to claims that actually have a raw_item; the `eq` on
    `raw_items.source_type` and the not-null on `raw_items.source_url`
    happen server-side via the embedded-filter pattern.
    """
    out = []  # type: List[Dict[str, Any]]
    offset = 0
    while True:
        resp = (
            sb.table("claims")
            .select("id,raw_item_id,raw_items!inner(source_type,source_url)")
            .eq("status", "pending")
            .eq("raw_items.source_type", "gdelt")
            .not_.is_("raw_items.source_url", "null")
            .order("id")
            .range(offset, offset + PAGE - 1)
            .execute()
        )
        batch = resp.data or []
        for row in batch:
            ri = row.get("raw_items") or {}
            url = ri.get("source_url")
            if url:
                out.append({"claim_id": row["id"], "url": url})
        if len(batch) < PAGE:
            break
        offset += PAGE
    return out


def discard_one(sb, claim_id, url, status, error):
    # type: (Any, str, str, Optional[int], Optional[str]) -> None
    """Mark one claim discarded and write an audit-only flag.

    The flag is left open (no resolved_at); founder can bulk-resolve
    from /admin/quality-flags. The partial unique index on
    (flag_kind, target_id) for open rows makes raise_flag idempotent
    across re-runs.
    """
    sb.table("claims").update({"status": "discarded"}).eq("id", claim_id).execute()
    data_quality_flags.raise_flag(
        sb,
        flag_kind=FLAG_KIND,
        severity="low",
        detected_by=DETECTED_BY,
        claim_id=claim_id,
        detail={"http_status": status, "url": url, "error": error},
    )


def process_claims(sb, candidates, dry_run):
    # type: (Any, List[Dict[str, Any]], bool) -> Dict[str, Any]
    """Classify every candidate URL (10-way parallel) and apply the
    discard + flag when dry_run is False.

    Returns a summary dict for the caller to render:
      {
        'alive': int,
        'dead': [{'claim_id', 'url', 'status', 'error'}, ...],
        'discarded': int,   # only meaningful when dry_run=False
        'failures': int,    # discard_one() exceptions
      }
    """
    dead = []  # type: List[Dict[str, Any]]
    alive = 0
    processed = 0
    total = len(candidates)

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(classify_url, c["url"]): c for c in candidates}
        for fut in concurrent.futures.as_completed(futures):
            cand = futures[fut]
            verdict, status, error = fut.result()
            if verdict == DEAD:
                dead.append({
                    "claim_id": cand["claim_id"],
                    "url": cand["url"],
                    "status": status,
                    "error": error,
                })
            else:
                alive += 1
            processed += 1
            if processed % 50 == 0:
                print("  processed {}/{}".format(processed, total))

    summary = {
        "alive": alive,
        "dead": dead,
        "discarded": 0,
        "failures": 0,
    }  # type: Dict[str, Any]

    if dry_run or not dead:
        return summary

    print()
    print("[sweep_dead_gdelt_urls] discarding {} claims...".format(len(dead)))
    for i, d in enumerate(dead):
        try:
            discard_one(sb, d["claim_id"], d["url"], d["status"], d["error"])
            summary["discarded"] += 1
        except Exception as exc:  # noqa: BLE001
            summary["failures"] += 1
            print(
                "  ! failed claim {}: {}".format(d["claim_id"], exc),
                file=sys.stderr,
            )
        if (i + 1) % 100 == 0:
            print("  ...{}/{} discarded".format(i + 1, len(dead)))

    return summary


def _print_final_summary(summary, total_checked, dry_run):
    # type: (Dict[str, Any], int, bool) -> None
    dead = summary["dead"]
    print()
    print("=== Summary ===")
    print("total checked:  {}".format(total_checked))
    print("alive:          {}".format(summary["alive"]))
    print("dead:           {}".format(len(dead)))
    if dead:
        print()
        print("Sample of dead URLs:")
        for d in dead[:10]:
            tag = d["status"] if d["status"] is not None else d["error"]
            print("  [{}] {}".format(tag, d["url"]))
        if len(dead) > 10:
            print("  ... and {} more".format(len(dead) - 10))

    if dry_run:
        print()
        print("[sweep_dead_gdelt_urls] DRY RUN - no writes")
        return

    print()
    print("=== Done ===")
    print("discarded: {}".format(summary["discarded"]))
    print("failed:    {}".format(summary["failures"]))


def main():
    # type: () -> int
    parser = argparse.ArgumentParser(
        description="Sweep dead GDELT source URLs out of the pending claim queue",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="HEAD-check URLs and report, but skip DB writes",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Process only the first N pending GDELT claims (test mode)",
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

    print("[sweep_dead_gdelt_urls] loading pending GDELT claims...")
    candidates = find_pending_gdelt_claims(sb)
    print("[sweep_dead_gdelt_urls] {} candidates".format(len(candidates)))
    if args.limit is not None:
        candidates = candidates[: args.limit]
        print(
            "[sweep_dead_gdelt_urls] --limit {}: trimmed to {}".format(
                args.limit, len(candidates)
            )
        )

    if not candidates:
        print("[sweep_dead_gdelt_urls] nothing to do")
        return 0

    summary = process_claims(sb, candidates, dry_run=args.dry_run)
    _print_final_summary(summary, len(candidates), dry_run=args.dry_run)

    return 0 if summary["failures"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
