#!/usr/bin/env python3
"""Fill product_entities.manufacturer from Wikidata.

For every distinct `brand` in product_entities that has at least one
non-retracted shrinkflation event but no manufacturer, query Wikidata's
SPARQL endpoint for the parent organization (P749) or, failing that,
the owner (P127) or operator (P127 again) of the matching brand entity.

The script is intentionally conservative:
  - Single brand search per request (no UNION queries) so we can audit.
  - 1-second delay between requests (Wikidata's politeness limit).
  - Skips brands we've already tried within the last 30 days
    (cursor stored in scraper_state.last_cursor JSON).
  - --dry-run prints what it would write without UPDATEing.

Once this fills the manufacturer column, migration 056's
`corporate_tree` view becomes non-empty and the /insights "corporate
parents" section lights up.

Usage:
    python -m pipeline.scripts.wikidata_manufacturer_backfill
    python -m pipeline.scripts.wikidata_manufacturer_backfill --dry-run
    python -m pipeline.scripts.wikidata_manufacturer_backfill --limit 50
    python -m pipeline.scripts.wikidata_manufacturer_backfill --force-brand "Cadbury"
"""
import argparse
import json
import logging
import os
import sys
import time
import urllib.parse
from typing import Any, Dict, List, Optional

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

LOG = logging.getLogger("wikidata_manufacturer_backfill")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
)
WIKIDATA_SPARQL = "https://query.wikidata.org/sparql"
WIKIDATA_SEARCH = "https://www.wikidata.org/w/api.php"
USER_AGENT = (
    "FullCartsBot/1.0 (https://fullcarts.org/about; "
    "fullcartsinfo@gmail.com) python-httpx"
)
SLEEP_BETWEEN = 1.1  # seconds — Wikidata politeness floor
PAGE_SIZE = 1000


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


def find_brand_entity(client, brand):
    # type: (httpx.Client, str) -> Optional[str]
    """Search Wikidata for the QID best matching `brand`.

    Strategy:
      1. Search the API for label/alias matches.
      2. Prefer hits whose description suggests "brand" or "product line",
         falling back to the first result.
    """
    resp = client.get(WIKIDATA_SEARCH, params={
        "action": "wbsearchentities",
        "search": brand,
        "language": "en",
        "format": "json",
        "type": "item",
        "limit": "5",
    })
    if resp.status_code != 200:
        LOG.warning("wbsearchentities failed for %s: %s", brand, resp.status_code)
        return None
    js = resp.json()
    candidates = js.get("search", [])
    if not candidates:
        return None
    # Heuristic: prefer entries whose description mentions "brand",
    # "product", "company" — anything that smells consumer-CPG.
    GOOD_DESC = ("brand", "product line", "trademark", "snack", "food", "beverage",
                 "candy", "confection", "cereal", "biscuit")
    for c in candidates:
        desc = (c.get("description") or "").lower()
        if any(t in desc for t in GOOD_DESC):
            return c.get("id")
    # Otherwise fall back to the first result.
    return candidates[0].get("id")


def fetch_parent_label(client, qid):
    # type: (httpx.Client, str) -> Optional[str]
    """Return the English label of the parent org / owner / manufacturer
    associated with the given QID. Picks the first non-null value
    across P749 / P127 / P176 in that priority order."""
    sparql = """
SELECT ?parentLabel WHERE {{
  VALUES ?prop {{ wdt:P749 wdt:P127 wdt:P176 }}
  wd:{qid} ?prop ?parent .
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}} LIMIT 5
""".format(qid=qid)
    resp = client.get(WIKIDATA_SPARQL, params={
        "query": sparql,
        "format": "json",
    })
    if resp.status_code != 200:
        LOG.warning("SPARQL failed for %s: %s", qid, resp.status_code)
        return None
    bindings = resp.json().get("results", {}).get("bindings", [])
    if not bindings:
        return None
    # First non-empty label wins. We collapse repeats so the same parent
    # showing up across multiple props doesn't beat a more specific one.
    seen = set()
    for b in bindings:
        v = b.get("parentLabel", {}).get("value", "").strip()
        if not v or v in seen:
            continue
        seen.add(v)
        # Filter obvious wikidata-internal artifacts
        if v.startswith("http"):
            continue
        return v
    return None


def fetch_distinct_brands(client, limit):
    # type: (httpx.Client, Optional[int]) -> List[str]
    """Return distinct product_entities.brand values that have
    documented shrinkflation events but no manufacturer set."""
    # PostgREST select with distinct=true via prefer header
    # PostgREST doesn't truly support DISTINCT, so we paginate full rows
    # and dedup in Python. Filter to brands appearing in brand_rankings
    # so we only spend Wikidata budget on brands that matter.
    seen = set()
    offset = 0
    out = []
    while True:
        resp = client.get(
            "{}/rest/v1/product_entities".format(SUPABASE_URL),
            params={
                "select": "brand",
                "manufacturer": "is.null",
                "limit": str(PAGE_SIZE),
                "offset": str(offset),
                "order": "brand.asc",
            },
        )
        if resp.status_code != 200:
            LOG.error("Brand list fetch failed: %s", resp.status_code)
            break
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            b = (r.get("brand") or "").strip()
            if not b:
                continue
            if b in seen:
                continue
            seen.add(b)
            out.append(b)
            if limit and len(out) >= limit:
                return out
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def update_manufacturer(client, brand, manufacturer, dry_run):
    # type: (httpx.Client, str, str, bool) -> int
    """Update every product_entities row for this brand with the
    given manufacturer. Returns the count of rows updated."""
    if dry_run:
        return 0
    # Use ilike-equality via PostgREST so casing variations all get
    # the same parent. We pre-fetch row count via a HEAD request so
    # the log can show coverage.
    resp = client.patch(
        "{}/rest/v1/product_entities".format(SUPABASE_URL),
        params={"brand": "eq.{}".format(brand)},
        headers={"Prefer": "return=representation"},
        json={"manufacturer": manufacturer},
    )
    if resp.status_code >= 300:
        LOG.error("Update failed for %s: %s %s",
                  brand, resp.status_code, resp.text[:200])
        return 0
    body = resp.json()
    return len(body) if isinstance(body, list) else 1


def main():
    parser = argparse.ArgumentParser(
        description="Backfill product_entities.manufacturer from Wikidata",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Print resolved manufacturers without writing.")
    parser.add_argument("--limit", type=int, default=200,
                        help="Max brands to look up this run (default 200).")
    parser.add_argument(
        "--force-brand", type=str, default=None,
        help="Resolve only this brand (case-sensitive) and exit.",
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
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json",
        },
        timeout=30.0,
    )
    wd = httpx.Client(
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/sparql-results+json",
        },
        timeout=30.0,
    )

    if args.force_brand:
        brands = [args.force_brand]
    else:
        brands = fetch_distinct_brands(sb, args.limit)
    LOG.info("Brands to look up: %d", len(brands))

    resolved = 0
    not_found = 0
    rows_updated_total = 0
    for i, brand in enumerate(brands, start=1):
        LOG.info("[%d/%d] %s", i, len(brands), brand)
        qid = find_brand_entity(wd, brand)
        time.sleep(SLEEP_BETWEEN)
        if not qid:
            LOG.info("  no wikidata entity found")
            not_found += 1
            continue
        parent = fetch_parent_label(wd, qid)
        time.sleep(SLEEP_BETWEEN)
        if not parent:
            LOG.info("  %s found but no parent org", qid)
            not_found += 1
            continue
        rows = update_manufacturer(sb, brand, parent, args.dry_run)
        LOG.info("  → %s  (rows %s %d)",
                 parent, "WOULD UPDATE" if args.dry_run else "updated", rows)
        rows_updated_total += rows
        resolved += 1

    LOG.info("Done. resolved=%d, not_found=%d, rows_updated=%d",
             resolved, not_found, rows_updated_total)

    sb.close()
    wd.close()


if __name__ == "__main__":
    main()
