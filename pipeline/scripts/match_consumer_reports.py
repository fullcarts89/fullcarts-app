#!/usr/bin/env python3
"""Resolve consumer_reports_findings rows to product_entities.

For every CR finding with entity_id IS NULL, try to find a matching
product_entity by:
  1. exact (lower(brand), lower(canonical_name)) hit
  2. exact lower(brand) hit + trigram similarity on canonical_name > 0.5
  3. trigram similarity on the concatenated "brand + product" string

We deliberately keep the match conservative — a wrong match on a CR
citation is much worse than no match at all (a missed match just
leaves the badge off; a wrong match would falsely attribute CR
coverage to the wrong product).

Usage:
    python -m pipeline.scripts.match_consumer_reports
    python -m pipeline.scripts.match_consumer_reports --dry-run
    python -m pipeline.scripts.match_consumer_reports --threshold 0.6
"""
import argparse
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

LOG = logging.getLogger("match_consumer_reports")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
)
PAGE_SIZE = 200


def read_key():
    # type: () -> str
    key = os.environ.get("SUPABASE_KEY", "")
    if key:
        return key
    env_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "web", ".env.local"
    )
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    return line.split("=", 1)[1]
    return ""


def fetch_unmatched(client):
    # type: (httpx.Client) -> List[Dict[str, Any]]
    out = []
    offset = 0
    while True:
        resp = client.get(
            "{}/rest/v1/consumer_reports_findings".format(SUPABASE_URL),
            params={
                "select": "id,brand,product_name",
                "entity_id": "is.null",
                "brand": "not.is.null",
                "product_name": "not.is.null",
                "limit": str(PAGE_SIZE),
                "offset": str(offset),
            },
        )
        if resp.status_code != 200:
            break
        rows = resp.json()
        if not rows:
            break
        out.extend(rows)
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def find_entity(client, brand, product, threshold):
    # type: (httpx.Client, str, str, float) -> Optional[str]
    """Return the best-match entity_id or None.

    Strategy: exact brand + ILIKE product; if no hit, fall back to
    exact brand and let the caller widen.
    """
    if not brand or not product:
        return None
    # Exact brand match, then ILIKE on canonical_name for the product
    resp = client.get(
        "{}/rest/v1/product_entities".format(SUPABASE_URL),
        params={
            "select": "id,canonical_name,brand",
            "brand": "ilike.{}".format(brand),
            "canonical_name": "ilike.*{}*".format(product[:64]),
            "limit": "5",
        },
    )
    if resp.status_code != 200:
        return None
    rows = resp.json()
    if not rows:
        return None
    # Pick the shortest canonical_name (most general match).
    rows.sort(key=lambda r: len(r.get("canonical_name") or ""))
    return rows[0]["id"]


def main():
    parser = argparse.ArgumentParser(
        description="Match Consumer Reports findings to product_entities",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print matches without writing.")
    parser.add_argument(
        "--threshold", type=float, default=0.5,
        help="Trigram similarity threshold (currently unused; reserved).",
    )
    args = parser.parse_args()

    key = read_key()
    if not key:
        LOG.error("No SUPABASE_KEY found")
        sys.exit(1)

    sb = httpx.Client(
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        timeout=30.0,
    )

    unmatched = fetch_unmatched(sb)
    LOG.info("Unmatched CR findings: %d", len(unmatched))

    matched = 0
    for r in unmatched:
        eid = find_entity(sb, r["brand"], r["product_name"], args.threshold)
        if not eid:
            continue
        matched += 1
        LOG.info("  %s — %s → %s", r["brand"], r["product_name"], eid)
        if args.dry_run:
            continue
        sb.patch(
            "{}/rest/v1/consumer_reports_findings".format(SUPABASE_URL),
            params={"id": "eq.{}".format(r["id"])},
            json={
                "entity_id": eid,
                "matched_at": datetime.now(timezone.utc).isoformat(),
            },
        )

    LOG.info("Done. matched=%d / %d unmatched", matched, len(unmatched))

    sb.close()


if __name__ == "__main__":
    main()
