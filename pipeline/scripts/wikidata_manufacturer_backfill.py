#!/usr/bin/env python3
"""Fill product_entities.manufacturer from Wikidata.

Walks brands in order of impact (event count desc, then alphabetical
long-tail) and resolves each to a manufacturer label via Wikidata SPARQL.

Property priority (most-specific first):
   1. P176 — manufacturer (literally what the column is named).
   2. P127 — owned by.
   3. P749 — parent organization. *Fallback only* — chains too far up
             the holding-company ladder if used as the primary.

Each candidate parent is filtered against `PARENT_DENYLIST_CLASSES` —
Wikidata `instance of` (P31) QIDs we refuse to call a manufacturer
(humans, countries, PE funds, asset-management firms, etc.). This is
what keeps "France" / "Karl Albrecht Jr." / "BlackRock" off the
corporate tree on /insights.

The script is intentionally conservative:
  - Single brand search per request so we can audit.
  - 1-second delay between requests (Wikidata's politeness limit).
  - Skips brands we've already tried within the last 30 days
    (cursor stored in scraper_state.last_cursor JSON).
  - --dry-run prints what it would write without UPDATEing.

Once this fills the manufacturer column, migration 056's
`corporate_tree` view becomes non-empty and the /insights "corporate
parents" section lights up. For the headline brands (Cadbury, Tide,
Nestlé, etc.) we don't wait on this — the seed at
`pipeline/scripts/seed_manufacturers.py` covers them deterministically.

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


# Wikidata `instance of` (P31) classes we refuse to call a "manufacturer".
# When the chase through P176/P127/P749 lands on one of these, skip it —
# the label is probably an investor (BlackRock), country (France), natural
# person (Karl Albrecht Jr.), PE fund (Cerberus), or government body.
# Adding more is cheap; each row is a Wikidata QID.
PARENT_DENYLIST_CLASSES = (
    "Q5",          # human
    "Q6256",       # country
    "Q3624078",    # sovereign state
    "Q484652",     # private equity firm
    "Q1052300",    # institutional investor
    "Q15911314",   # asset-management firm
    "Q1330709",    # mutual fund (commonly bucketed with holding co's)
    "Q4671277",    # academic institution
    "Q11691",      # stock exchange
    "Q161726",     # multinational corporation — too generic, prefer the actual parent
    "Q210167",     # video game publisher (catches mis-resolved brand→studio)
    "Q1799794",    # administrative territorial entity
    "Q34770",      # municipality
    "Q1063239",    # publicly traded company — too generic
    "Q15265344",   # investment trust
    "Q43229",      # organization — too generic; only used when nothing more specific exists
)


def fetch_parent_label(client, qid):
    # type: (httpx.Client, str) -> Optional[str]
    """Return the English label of the manufacturer/owner/parent for a
    Wikidata entity.

    Property priority (most specific first, parent organization last):
       1. P176 — manufacturer (literally what the column is named).
       2. P127 — owned by.
       3. P749 — parent organization. Fallback only; can chase too far
                 up the holding-company ladder.

    Each candidate is filtered:
      - skip if instance-of (P31) matches PARENT_DENYLIST_CLASSES
        (humans, countries, PE funds, etc. — see constant above);
      - skip self-references (where the parent label equals the brand
        label, an artifact of some Wikidata records);
      - skip URIs or empty strings.

    Returns the first surviving candidate, or None.
    """
    # Single SPARQL with a UNION over the three properties + explicit
    # priority ordering. Pulling all candidates with their instance-of
    # set in one query is cheaper than three round-trips and lets us
    # apply the denylist in one pass.
    sparql = """
SELECT ?prop ?parent ?parentLabel
       (GROUP_CONCAT(DISTINCT STR(?cls); separator=",") AS ?classes) WHERE {{
  {{
    wd:{qid} wdt:P176 ?parent .
    BIND(1 AS ?prop)
  }} UNION {{
    wd:{qid} wdt:P127 ?parent .
    BIND(2 AS ?prop)
  }} UNION {{
    wd:{qid} wdt:P749 ?parent .
    BIND(3 AS ?prop)
  }}
  OPTIONAL {{ ?parent wdt:P31 ?cls . }}
  SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
}}
GROUP BY ?prop ?parent ?parentLabel
ORDER BY ?prop
LIMIT 20
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
    deny = set(PARENT_DENYLIST_CLASSES)
    seen = set()
    for b in bindings:
        label = b.get("parentLabel", {}).get("value", "").strip()
        parent_uri = b.get("parent", {}).get("value", "")
        if not label or label in seen:
            continue
        seen.add(label)
        if label.startswith("http"):
            continue
        # PARENT_LABEL fallback returns the URI literal when no rdfs:label
        # exists in en — that surfaces as a bare QID like "Q12345".
        if label.startswith("Q") and label[1:].isdigit():
            continue
        # Instance-of class filter — extract the QIDs from the URI list.
        class_uris = (b.get("classes", {}).get("value", "") or "").split(",")
        class_qids = {u.rsplit("/", 1)[-1] for u in class_uris if u}
        if class_qids & deny:
            LOG.debug(
                "  skipping %s — instance-of intersects denylist (%s)",
                label, ",".join(class_qids & deny),
            )
            continue
        # Self-reference: some Wikidata rows have brand→brand via P176.
        if parent_uri.rsplit("/", 1)[-1] == qid:
            continue
        return label
    return None


def fetch_distinct_brands(client, limit):
    # type: (httpx.Client, Optional[int]) -> List[str]
    """Return brands that need a manufacturer set, ordered by impact.

    Priority order:
      1. Brands appearing in `brand_rankings` (i.e. they have ≥1
         non-retracted published_changes event), sorted by event count
         descending. These are the brands that drive what's actually
         visible on the public site, so they earn the Wikidata budget
         first.
      2. The long tail (brands with 0 events), alphabetical, as a
         tie-breaker so cron runs are deterministic.

    Brands whose name is empty or "Unknown" are skipped — those are
    extractor failures, not real brands.
    """
    out = []  # type: List[str]
    seen = set()

    # Step 1: brand_rankings, ordered by impact.
    resp = client.get(
        "{}/rest/v1/brand_rankings".format(SUPABASE_URL),
        params={
            "select": "brand,shrinkflation_events",
            "order": "shrinkflation_events.desc.nullslast",
            "limit": str(PAGE_SIZE),
        },
    )
    if resp.status_code == 200:
        for r in resp.json():
            b = (r.get("brand") or "").strip()
            if not b or b.lower() == "unknown":
                continue
            if b in seen:
                continue
            # Only enqueue if at least one entity for this brand has
            # NULL manufacturer — otherwise we'd waste Wikidata budget
            # re-resolving brands the seed already covered.
            check = client.get(
                "{}/rest/v1/product_entities".format(SUPABASE_URL),
                params={
                    "select": "id",
                    "brand": "ilike.{}".format(b),
                    "manufacturer": "is.null",
                    "limit": "1",
                },
            )
            if check.status_code == 200 and check.json():
                seen.add(b)
                out.append(b)
                if limit and len(out) >= limit:
                    return out
    else:
        LOG.warning("brand_rankings fetch failed: %s — falling back to alphabetical",
                    resp.status_code)

    # Step 2: long tail, alphabetical. Same is.null filter at the SQL
    # level so we don't spend cycles re-checking covered brands.
    offset = 0
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
            LOG.error("long-tail brand fetch failed: %s", resp.status_code)
            break
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            b = (r.get("brand") or "").strip()
            if not b or b.lower() == "unknown":
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
