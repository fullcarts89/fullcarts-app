#!/usr/bin/env python3
"""Promote nutrition-based skimpflation findings into published_changes.

For every UPC that:
  1. Has nutrition data in *at least two* USDA releases
  2. Shows a meaningful skimpflation signal (aggregate score ≥ threshold)
  3. Maps to a row in our pack_variants table

we create a published_changes row with change_type='skimpflation', so the
finding shows up alongside size-based shrinkflation events on the
public site (per item 2.4 of the Phase 2 plan).

Idempotent: skips UPCs that already have a non-retracted skimpflation
row for the same entity. Re-running won't double-publish.

Schema dependency: migration 055 must be applied first (relaxes the
NOT NULL on size_* + adds skimp_score / nutrient_deltas columns).

Usage:
    python -m pipeline.scripts.promote_skimpflation
    python -m pipeline.scripts.promote_skimpflation --dry-run
    python -m pipeline.scripts.promote_skimpflation --min-score 8
"""
import argparse
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import httpx

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

LOG = logging.getLogger("promote_skimpflation")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Same nutrient model as nutrition_skimpflation.py — kept in sync.
DROP_SIGNALS = ["protein_g", "fiber_g", "calcium_mg"]
RISE_SIGNALS = ["sugars_g", "sodium_mg", "saturated_fat_g"]
ALL_NUTRIENTS = [
    "calories_kcal", "protein_g", "total_fat_g", "saturated_fat_g",
    "carbs_g", "fiber_g", "sugars_g", "calcium_mg", "sodium_mg",
    "cholesterol_mg",
]
NUTRIENT_UNITS = {
    "calories_kcal": "kcal",
    "protein_g": "g",
    "total_fat_g": "g",
    "saturated_fat_g": "g",
    "carbs_g": "g",
    "fiber_g": "g",
    "sugars_g": "g",
    "calcium_mg": "mg",
    "sodium_mg": "mg",
    "cholesterol_mg": "mg",
}
NUTRIENT_LABELS = {
    "calories_kcal": "Calories",
    "protein_g": "Protein",
    "total_fat_g": "Total fat",
    "saturated_fat_g": "Saturated fat",
    "carbs_g": "Carbohydrates",
    "fiber_g": "Fiber",
    "sugars_g": "Sugar",
    "calcium_mg": "Calcium",
    "sodium_mg": "Sodium",
    "cholesterol_mg": "Cholesterol",
}

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


def detect_releases(client):
    # type: (httpx.Client) -> List[str]
    """Return USDA release_dates that have nutrition data, oldest first."""
    resp = client.get("/rest/v1/usda_product_history", params={
        "select": "release_date",
        "protein_g": "not.is.null",
        "order": "release_date.asc",
        "limit": "1",
    })
    # Cheap version: enumerate distinct release_dates via a separate call.
    resp = client.post(
        "/rest/v1/rpc/usda_releases_with_nutrition",
        json={},
    )
    if resp.status_code == 200:
        return [r["release_date"] for r in resp.json()]

    # Fall back to manually fetching distinct dates with a paginated
    # select(distinct). PostgREST doesn't support DISTINCT directly, so
    # we use an ordered select with limit and dedup in Python.
    seen = []
    offset = 0
    while True:
        r = client.get("/rest/v1/usda_product_history", params={
            "select": "release_date",
            "protein_g": "not.is.null",
            "order": "release_date.asc",
            "limit": str(PAGE_SIZE),
            "offset": str(offset),
        })
        if r.status_code != 200:
            break
        rows = r.json()
        if not rows:
            break
        for row in rows:
            d = row.get("release_date")
            if d and d not in seen:
                seen.append(d)
        offset += PAGE_SIZE
        if offset > 100_000:  # paranoia
            break
    return sorted(seen)


def fetch_release(client, release_date):
    # type: (httpx.Client, str) -> Dict[str, Dict[str, Any]]
    """Fetch all UPCs with nutrition data for one release."""
    fields = ",".join(["gtin_upc", "brand_name", "description"] + ALL_NUTRIENTS)
    result = {}  # type: Dict[str, Dict[str, Any]]
    offset = 0
    while True:
        resp = client.get("/rest/v1/usda_product_history", params={
            "select": fields,
            "release_date": "eq.{}".format(release_date),
            "protein_g": "not.is.null",
            "order": "gtin_upc.asc",
            "limit": str(PAGE_SIZE),
            "offset": str(offset),
        })
        if resp.status_code != 200:
            LOG.error("Fetch failed for %s at offset %d: %s",
                      release_date, offset, resp.status_code)
            break
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            upc = r.get("gtin_upc", "")
            if upc:
                result[upc] = r
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return result


def analyze(early, late, min_score, noise_floor_pct):
    # type: (Dict[str, Dict], Dict[str, Dict], float, float) -> List[Dict[str, Any]]
    """Compute per-UPC nutrient deltas + aggregate skimp score.

    Mirrors `web/src/app/products/[id]/lib.ts:computeSkimpData` so the
    pipeline and the live page agree on what counts as skimpflation.
    """
    common = set(early.keys()) & set(late.keys())
    LOG.info("Common UPCs across releases: %d", len(common))
    out = []  # type: List[Dict[str, Any]]
    for upc in common:
        e = early[upc]
        l = late[upc]
        deltas = []  # type: List[Dict[str, Any]]
        score = 0.0
        for col in ALL_NUTRIENTS:
            ev = e.get(col)
            lv = l.get(col)
            if ev is None or lv is None:
                continue
            try:
                evf = float(ev)
                lvf = float(lv)
            except (ValueError, TypeError):
                continue
            if evf == 0:
                continue
            pct = ((lvf - evf) / evf) * 100
            if abs(pct) < noise_floor_pct:
                continue
            bad = "up" if col in RISE_SIGNALS else "down" if col in DROP_SIGNALS else None
            deltas.append({
                "nutrient": col,
                "label": NUTRIENT_LABELS.get(col, col),
                "unit": NUTRIENT_UNITS.get(col, ""),
                "before": round(evf, 2),
                "after": round(lvf, 2),
                "delta_pct": round(pct, 1),
                "bad_direction": bad,
            })
            if bad == "down" and pct < 0:
                score += abs(pct)
            elif bad == "up" and pct > 0:
                score += pct
        if deltas and score >= min_score:
            out.append({
                "upc": upc,
                "brand": (e.get("brand_name") or "").strip(),
                "description": (e.get("description") or "").strip(),
                "skimp_score": round(score, 1),
                "deltas": deltas,
            })
    out.sort(key=lambda x: -x["skimp_score"])
    return out


def norm_upc(raw):
    # type: (Optional[str]) -> str
    if not raw:
        return ""
    digits = "".join(ch for ch in raw if ch.isdigit())
    return digits


def upc_variants(raw):
    # type: (Optional[str]) -> List[str]
    """All plausible UPC representations for matching against pack_variants."""
    d = norm_upc(raw)
    if not d or len(d) < 8:
        return []
    out = [d]
    if len(d) == 13 and d.startswith("0"):
        out.append(d[1:])
    if len(d) == 12:
        out.append("0" + d)
    return out


def fetch_pack_variants(client, upcs):
    # type: (httpx.Client, List[str]) -> Dict[str, Tuple[str, str]]
    """Return {upc: (variant_id, entity_id)} for any of the given UPCs."""
    if not upcs:
        return {}
    # Chunk into batches of ~200 to keep the URL length safe.
    out = {}
    for i in range(0, len(upcs), 200):
        chunk = upcs[i:i + 200]
        in_clause = "in.({})".format(",".join('"{}"'.format(u) for u in chunk))
        resp = client.get("/rest/v1/pack_variants", params={
            "select": "id,upc,entity_id",
            "upc": in_clause,
            "limit": "1000",
        })
        if resp.status_code != 200:
            LOG.warning("pack_variants lookup failed: %s", resp.status_code)
            continue
        for r in resp.json():
            upc = r.get("upc") or ""
            if upc:
                out[upc] = (r["id"], r["entity_id"])
    return out


def existing_skimp_entities(client):
    # type: (httpx.Client) -> set
    """Set of entity_ids that already have a non-retracted skimpflation row."""
    out = set()
    offset = 0
    while True:
        resp = client.get("/rest/v1/published_changes", params={
            "select": "entity_id",
            "change_type": "eq.skimpflation",
            "is_retracted": "eq.false",
            "limit": str(PAGE_SIZE),
            "offset": str(offset),
        })
        if resp.status_code != 200:
            break
        rows = resp.json()
        if not rows:
            break
        for r in rows:
            if r.get("entity_id"):
                out.add(r["entity_id"])
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def fetch_entity_brands(client, entity_ids):
    # type: (httpx.Client, List[str]) -> Dict[str, Tuple[str, str]]
    """Return {entity_id: (brand, canonical_name)} for the given IDs."""
    if not entity_ids:
        return {}
    out = {}
    for i in range(0, len(entity_ids), 200):
        chunk = entity_ids[i:i + 200]
        in_clause = "in.({})".format(",".join('"{}"'.format(e) for e in chunk))
        resp = client.get("/rest/v1/product_entities", params={
            "select": "id,brand,canonical_name",
            "id": in_clause,
            "limit": "1000",
        })
        if resp.status_code != 200:
            continue
        for r in resp.json():
            out[r["id"]] = (r.get("brand") or "", r.get("canonical_name") or "")
    return out


def severity_of(score):
    # type: (float) -> str
    if score >= 25:
        return "major"
    if score >= 12:
        return "moderate"
    return "minor"


def main():
    parser = argparse.ArgumentParser(
        description="Promote nutrition-based skimpflation into published_changes",
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Compute everything, don't insert.")
    parser.add_argument("--min-score", type=float, default=5.0,
                        help="Minimum aggregate skimp score (default 5).")
    parser.add_argument("--noise-floor", type=float, default=2.0,
                        help="Per-nutrient %% delta to count (default 2%%).")
    parser.add_argument("--early", type=str, default=None,
                        help="USDA release_date to use as 'before'.")
    parser.add_argument("--late", type=str, default=None,
                        help="USDA release_date to use as 'after'.")
    args = parser.parse_args()

    key = read_key()
    url = os.environ.get(
        "SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co"
    )
    if not key:
        LOG.error("No SUPABASE_KEY found")
        sys.exit(1)

    client = httpx.Client(
        base_url=url,
        headers={
            "apikey": key,
            "Authorization": "Bearer {}".format(key),
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        },
        timeout=60.0,
    )

    LOG.info("Detecting USDA releases with nutrition data...")
    releases = detect_releases(client)
    if len(releases) < 2:
        # Quarterly USDA ingestion is what populates this; in a fresh DB or
        # before the second release lands, the cross-release diff has
        # nothing to compare. Soft-skip so the daily cron stays green.
        LOG.warning(
            "Skipping: need ≥2 USDA releases with nutrition data, have %d.",
            len(releases),
        )
        client.close()
        return
    LOG.info("Releases with nutrition data: %s", releases)

    early_rel = args.early or releases[0]
    late_rel = args.late or releases[-1]
    LOG.info("Comparing %s → %s", early_rel, late_rel)

    t0 = time.time()
    early = fetch_release(client, early_rel)
    LOG.info("  %s: %d products in %.1fs", early_rel, len(early), time.time() - t0)

    t0 = time.time()
    late = fetch_release(client, late_rel)
    LOG.info("  %s: %d products in %.1fs", late_rel, len(late), time.time() - t0)

    findings = analyze(early, late, args.min_score, args.noise_floor)
    LOG.info("UPCs with skimpflation signal ≥ %s: %d",
             args.min_score, len(findings))
    if not findings:
        client.close()
        return

    # Build UPC variants for pack_variants lookup
    upc_index = {}  # type: Dict[str, Dict[str, Any]]
    all_variants = []  # type: List[str]
    for f in findings:
        for v in upc_variants(f["upc"]):
            upc_index[v] = f
            all_variants.append(v)
    # Dedup while preserving order
    seen = set()
    ordered = []
    for u in all_variants:
        if u not in seen:
            seen.add(u)
            ordered.append(u)

    LOG.info("Looking up %d UPC variants in pack_variants...", len(ordered))
    matches = fetch_pack_variants(client, ordered)
    LOG.info("  matched %d UPCs to existing variants", len(matches))

    if not matches:
        LOG.info("No skimpflation findings map to known pack_variants — done.")
        client.close()
        return

    LOG.info("Checking which entities already have a skimpflation row...")
    already = existing_skimp_entities(client)
    LOG.info("  %d entities already have one", len(already))

    LOG.info("Resolving entity names...")
    entity_ids = list({eid for (_, eid) in matches.values()})
    entity_info = fetch_entity_brands(client, entity_ids)

    # Each finding maps via its UPC variants to one (variant_id, entity_id).
    # Multiple variants can share the same entity; we only publish once per
    # entity (first-match wins, sorted by skimp_score desc).
    inserts = []  # type: List[Dict[str, Any]]
    handled_entities = set(already)
    for f in findings:
        eid_for_this = None
        vid_for_this = None
        for v in upc_variants(f["upc"]):
            m = matches.get(v)
            if m:
                vid_for_this, eid_for_this = m
                break
        if not eid_for_this:
            continue
        if eid_for_this in handled_entities:
            continue
        handled_entities.add(eid_for_this)

        brand, canonical_name = entity_info.get(
            eid_for_this, (f["brand"], f["description"])
        )
        inserts.append({
            "variant_id": vid_for_this,
            "entity_id": eid_for_this,
            "brand": brand or f["brand"] or "Unknown",
            "product_name": canonical_name or f["description"] or "Unknown product",
            "change_type": "skimpflation",
            "severity": severity_of(f["skimp_score"]),
            "observed_date": late_rel,
            "skimp_score": f["skimp_score"],
            "nutrient_deltas": f["deltas"],
            "evidence_summary": [{
                "source_type": "usda",
                "release_before": early_rel,
                "release_after": late_rel,
                "gtin_upc": f["upc"],
                "score": f["skimp_score"],
            }],
            "evidence_count": 1,
        })

    LOG.info("Will %s %d new skimpflation events.",
             "PRINT" if args.dry_run else "insert", len(inserts))

    if args.dry_run:
        for ins in inserts[:10]:
            LOG.info("  %s — %s · score %.1f",
                     ins["brand"], ins["product_name"], ins["skimp_score"])
        if len(inserts) > 10:
            LOG.info("  ... and %d more", len(inserts) - 10)
        client.close()
        return

    # Batch insert in chunks of 100 to keep request bodies small.
    inserted_total = 0
    for i in range(0, len(inserts), 100):
        chunk = inserts[i:i + 100]
        resp = client.post("/rest/v1/published_changes", json=chunk)
        if resp.status_code >= 300:
            LOG.error("Insert failed (%s): %s", resp.status_code, resp.text[:500])
            break
        inserted_total += len(chunk)
    LOG.info("Inserted %d skimpflation events into published_changes.", inserted_total)

    client.close()


if __name__ == "__main__":
    main()
