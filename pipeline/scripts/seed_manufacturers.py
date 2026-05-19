#!/usr/bin/env python3
"""Seed product_entities.manufacturer from a hand-curated YAML.

Reads pipeline/data/brand_manufacturers.yml and idempotently applies each
mapping via PostgREST. Brand matching is case-insensitive; an optional
`category` filter on a row narrows it to entities whose category column
contains the given substring (also case-insensitive). This lets us
disambiguate cross-category brand collisions like "Dove" (Unilever
personal care vs Mars chocolate).

The script never overwrites a non-NULL manufacturer unless --force is
passed. That way it's safe to re-run after a Wikidata backfill cron has
filled some values: the seed only fills gaps.

Why this script exists: the Wikidata backfill is slow (~200 brands/wk),
walks alphabetically, and occasionally returns noise like "BlackRock" or
"France" for brands whose ownership chain on Wikidata threads through
holding companies and governments. The /insights corporate-tree section
needs deterministic, correct mappings for the top brands by event count
right now — this seed handles those; the Wikidata backfill covers the
long tail.

Usage:
    python -m pipeline.scripts.seed_manufacturers --dry-run
    python -m pipeline.scripts.seed_manufacturers
    python -m pipeline.scripts.seed_manufacturers --force        # overwrite existing
    python -m pipeline.scripts.seed_manufacturers --yaml path/to/other.yml
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

import httpx

try:
    import yaml  # type: ignore
except ImportError:
    print(
        "PyYAML is required. Install with: pip install pyyaml",
        file=sys.stderr,
    )
    sys.exit(2)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

LOG = logging.getLogger("seed_manufacturers")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

DEFAULT_YAML = os.path.join(
    os.path.dirname(__file__), "..", "data", "brand_manufacturers.yml"
)
SUPABASE_URL = os.getenv(
    "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
)
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


def load_mappings(path):
    # type: (str) -> List[Dict[str, str]]
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    rows = data.get("mappings") or []
    out = []  # type: List[Dict[str, str]]
    for i, r in enumerate(rows):
        brand = (r.get("brand") or "").strip()
        manuf = (r.get("manufacturer") or "").strip()
        if not brand or not manuf:
            LOG.warning("row %d: missing brand or manufacturer; skipping", i)
            continue
        cat = (r.get("category") or "").strip() or None
        out.append({"brand": brand, "manufacturer": manuf, "category": cat})
    return out


def fetch_matches(client, brand, category, force):
    # type: (httpx.Client, str, Optional[str], bool) -> List[Dict[str, Any]]
    """Return product_entities rows that match this row's filter.

    Without --force, we skip entities whose manufacturer is already set.
    PostgREST's `or`/`is.null` query for "null OR same value" is verbose
    so we just filter on `is.null` here and let the caller handle the
    --force path by re-fetching without the null filter.
    """
    params = {
        "select": "id,brand,category,manufacturer",
        # Case-insensitive equality. Use the wildcard-free pattern so
        # "Dove " or " Dove" doesn't match unintentionally.
        "brand": "ilike.{}".format(brand.replace(",", "")),
        "limit": str(PAGE_SIZE),
    }
    if category:
        # Category column is free-text from the extractor; substring is
        # safer than exact match. Wrap in % for ilike.
        params["category"] = "ilike.*{}*".format(category)
    if not force:
        params["manufacturer"] = "is.null"

    resp = client.get(
        "{}/rest/v1/product_entities".format(SUPABASE_URL),
        params=params,
    )
    if resp.status_code != 200:
        LOG.error(
            "fetch failed for brand=%r category=%r: %s",
            brand,
            category,
            resp.status_code,
        )
        return []
    return resp.json()


def apply_update(client, ids, manufacturer, dry_run):
    # type: (httpx.Client, List[str], str, bool) -> int
    """PATCH product_entities for the given ids, batched to keep URLs
    under PostgREST's 8KB query-string limit (each UUID is ~40 chars)."""
    if not ids:
        return 0
    if dry_run:
        return len(ids)
    BATCH = 100
    updated = 0
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i + BATCH]
        in_clause = "in.({})".format(",".join('"{}"'.format(x) for x in chunk))
        resp = client.patch(
            "{}/rest/v1/product_entities".format(SUPABASE_URL),
            params={"id": in_clause},
            json={"manufacturer": manufacturer},
            headers={"Prefer": "return=minimal"},
        )
        if resp.status_code >= 300:
            LOG.error(
                "PATCH failed (%s) on batch %d-%d: %s",
                resp.status_code, i, i + len(chunk), resp.text[:300],
            )
            continue
        updated += len(chunk)
    return updated


def main():
    parser = argparse.ArgumentParser(
        description="Seed product_entities.manufacturer from a YAML mapping.",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show counts but don't write to the DB.")
    parser.add_argument("--force", action="store_true",
                        help="Overwrite manufacturer even when already set.")
    parser.add_argument("--yaml", type=str, default=DEFAULT_YAML,
                        help="Path to the mappings YAML.")
    args = parser.parse_args()

    key = read_key()
    if not key:
        LOG.error("No SUPABASE_KEY in env or web/.env.local")
        sys.exit(1)

    mappings = load_mappings(args.yaml)
    if not mappings:
        LOG.error("No mappings loaded from %s", args.yaml)
        sys.exit(1)
    LOG.info("Loaded %d mappings from %s", len(mappings), args.yaml)

    # Sort so category-scoped rows apply BEFORE bare-brand rows. That
    # way the more-specific filter wins when both could match an entity
    # (we re-fetch with is.null between rows so this only matters when
    # --force is set, but it's the right order regardless).
    mappings.sort(key=lambda r: 0 if r.get("category") else 1)

    client = httpx.Client(
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
            "Content-Type": "application/json",
        },
        timeout=60.0,
    )

    total_seen = 0
    total_updated = 0
    by_manuf = {}  # type: Dict[str, int]
    misses = []  # type: List[Tuple[str, Optional[str]]]

    for row in mappings:
        brand = row["brand"]
        manuf = row["manufacturer"]
        cat = row.get("category")
        rows = fetch_matches(client, brand, cat, args.force)
        total_seen += len(rows)
        # Skip rows already set to this same manufacturer (idempotent).
        ids = [
            r["id"]
            for r in rows
            if (r.get("manufacturer") or "") != manuf
        ]
        n = apply_update(client, ids, manuf, args.dry_run)
        total_updated += n
        by_manuf[manuf] = by_manuf.get(manuf, 0) + n
        if not rows:
            misses.append((brand, cat))
        else:
            tag = " [{}]".format(cat) if cat else ""
            LOG.info(
                "  %s%s → %s : matched %d, updated %d",
                brand, tag, manuf, len(rows), n,
            )

    LOG.info("")
    LOG.info("=" * 60)
    LOG.info(
        "Total: matched %d entities, %s %d",
        total_seen,
        "would update" if args.dry_run else "updated",
        total_updated,
    )
    LOG.info("By manufacturer:")
    for m, count in sorted(by_manuf.items(), key=lambda x: -x[1]):
        if count == 0:
            continue
        LOG.info("  %-32s %d", m, count)
    if misses:
        LOG.info("")
        LOG.info("Brands with no entities in DB (long-tail mappings):")
        for b, c in misses[:30]:
            tag = " [{}]".format(c) if c else ""
            LOG.info("  - %s%s", b, tag)
        if len(misses) > 30:
            LOG.info("  ... and %d more", len(misses) - 30)

    client.close()


if __name__ == "__main__":
    main()
