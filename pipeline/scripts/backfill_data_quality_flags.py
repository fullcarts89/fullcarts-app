#!/usr/bin/env python3
"""One-shot backfill of data_quality_flags from historical data.

The forward detectors that ship in promote_claims.py and
cleanup_stuck_matched.py only fire when new claims flow through the
pipeline. The structural gap is everything that landed in the catalog
BEFORE those detectors existed — the "Poor" entities, the M&M's case
variants, the 1L→900L upsize events, etc.

This script reads every non-retracted entity, event, and active claim,
runs each one through the same predicates the forward detectors use,
and calls raise_flag() for each match. The partial unique index from
migration 063 makes the inserts idempotent: re-running this script
against a populated queue is a safe no-op for already-open flags.

Six detector kinds covered:

  short_brand            entity has placeholder/short brand
  fuzzy_brand_collision  entity collides with another on (brand, slug)
  size_outlier           event has size ratio outside [0.5, 2.0]
  sku_mashup             entity has events with size_before spread > 3x
  mixed_units            entity has events with > 1 size_unit
  stuck_approved_claim   claim has been in 'matched' with NULL entity
                         link for > 7 days

Designed to be safe to run repeatedly (idempotent). Read-only against
entities/events/claims; only writes to data_quality_flags.

Usage:
    python -m pipeline.scripts.backfill_data_quality_flags
    python -m pipeline.scripts.backfill_data_quality_flags --dry-run
    python -m pipeline.scripts.backfill_data_quality_flags --only short_brand sku_mashup
"""
import argparse
import logging
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from pipeline.lib.data_quality_flags import raise_flag

LOG = logging.getLogger("backfill_data_quality_flags")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000

# Predicates duplicated here intentionally rather than imported. The
# forward detectors live in pipeline scripts that pull large dependencies
# (supabase client init, etc.) and aren't safe to import in a unit-test
# context. Tests on the detectors and this backfill stay independently
# verifiable.

# from promote_claims._SUSPECT_BRAND_PLACEHOLDERS:
_SUSPECT_BRAND_PLACEHOLDERS = frozenset(
    {"Unknown", "Various", "Poor", "N/A", "Generic", "Misc"}
)
_SUSPECT_NAME_PLACEHOLDERS = frozenset({"Unknown Product", "Product", "Item"})

# Size-ratio bounds for the size_outlier detector. Matches the profiler
# script (pipeline/scripts/profile_matched_claims.py). Note these are
# TIGHTER than migration 061's [0.05, 5.0] CHECK constraint — the
# constraint blocks structurally impossible writes; this band flags
# plausible-but-suspicious ones.
SIZE_OUTLIER_MIN = 0.5
SIZE_OUTLIER_MAX = 2.0

# SKU-mashup spread thresholds.
WIDE_SPREAD = 3.0
EXTREME_SPREAD = 10.0

# stuck_approved_claim threshold.
STUCK_CLAIM_DAYS = 7

ALL_KINDS = (
    "short_brand",
    "fuzzy_brand_collision",
    "size_outlier",
    "sku_mashup",
    "mixed_units",
    "stuck_approved_claim",
)


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _paginate(builder):
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        # Each call to .range() returns a fresh builder slice; the previous
        # one had a bug where supabase-py accumulates range params on the
        # same builder. We construct a new builder per page from a factory.
        page_builder = builder()
        resp = page_builder.range(offset, offset + PAGE_SIZE - 1).execute()
        batch = resp.data or []
        out.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def slugify(name: str) -> str:
    """Match the lib.ts slugify in /admin/duplicates so the two surfaces
    agree on what constitutes a duplicate."""
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower().strip())


def is_suspect_brand(brand: Optional[str]) -> bool:
    """Mirror of pipeline.scripts.promote_claims.is_suspect_brand."""
    if not brand or len(brand.strip()) < 2:
        return True
    return brand in _SUSPECT_BRAND_PLACEHOLDERS


# ────────────────────────────── detectors ──────────────────────────────


def detect_short_brand(
    sb,
    entities: List[Dict[str, Any]],
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Flag entities with placeholder / single-char brand strings OR
    placeholder canonical_name."""
    for ent in entities:
        brand = ent.get("brand") or ""
        name = ent.get("canonical_name") or ""
        if not (is_suspect_brand(brand) or name in _SUSPECT_NAME_PLACEHOLDERS):
            continue
        stats["short_brand_matched"] += 1
        if dry_run:
            continue
        new_id = raise_flag(
            sb,
            flag_kind="short_brand",
            severity="med",
            detected_by="backfill_v1",
            entity_id=ent["id"],
            detail={"brand": brand, "name": name, "backfill": True},
        )
        if new_id:
            stats["short_brand_inserted"] += 1
        else:
            stats["short_brand_already_open"] += 1


def detect_fuzzy_brand_collision(
    sb,
    entities: List[Dict[str, Any]],
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Flag every non-target entity in a (brand, slug) collision group.
    Target = the entity in the group with the most events (already
    enriched on each row by the caller)."""
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for ent in entities:
        brand = (ent.get("brand") or "").lower().strip()
        slug = slugify(ent.get("canonical_name") or "")
        if not brand or not slug:
            continue
        groups[(brand, slug)].append(ent)

    for (brand, slug), members in groups.items():
        if len(members) < 2:
            continue
        ranked = sorted(
            members,
            key=lambda m: (-(m.get("event_count") or 0), m["id"]),
        )
        target = ranked[0]
        for src in ranked[1:]:
            stats["fuzzy_brand_collision_matched"] += 1
            if dry_run:
                continue
            new_id = raise_flag(
                sb,
                flag_kind="fuzzy_brand_collision",
                severity="med",
                detected_by="backfill_v1",
                entity_id=src["id"],
                detail={
                    "brand": brand,
                    "slug": slug,
                    "group_size": len(members),
                    "source_name": src.get("canonical_name"),
                    "target_id": target["id"],
                    "target_name": target.get("canonical_name"),
                    "target_events": target.get("event_count") or 0,
                    "backfill": True,
                },
            )
            if new_id:
                stats["fuzzy_brand_collision_inserted"] += 1
            else:
                stats["fuzzy_brand_collision_already_open"] += 1


def detect_size_outlier(
    sb,
    events: List[Dict[str, Any]],
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Flag events with size ratio outside [SIZE_OUTLIER_MIN, SIZE_OUTLIER_MAX]."""
    for e in events:
        try:
            sb_v = float(e.get("size_before") or 0)
            sa_v = float(e.get("size_after") or 0)
            if sb_v <= 0 or sa_v <= 0:
                continue
            ratio = sa_v / sb_v
        except (TypeError, ValueError):
            continue
        if SIZE_OUTLIER_MIN <= ratio <= SIZE_OUTLIER_MAX:
            continue
        stats["size_outlier_matched"] += 1
        if dry_run:
            continue
        # Ratio far from 1 = more suspicious; encode that in severity.
        severity = "high" if ratio < 0.1 or ratio > 5.0 else "med"
        new_id = raise_flag(
            sb,
            flag_kind="size_outlier",
            severity=severity,
            detected_by="backfill_v1",
            event_id=e["id"],
            detail={
                "entity_id": e.get("entity_id"),
                "brand": e.get("brand"),
                "product_name": e.get("product_name"),
                "size_before": sb_v,
                "size_after": sa_v,
                "size_unit": e.get("size_unit"),
                "ratio": round(ratio, 4),
                "evidence_count": e.get("evidence_count"),
                "backfill": True,
            },
        )
        if new_id:
            stats["size_outlier_inserted"] += 1
        else:
            stats["size_outlier_already_open"] += 1


def detect_sku_mashup(
    sb,
    events: List[Dict[str, Any]],
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Flag entities with size_before spread > WIDE_SPREAD across their events."""
    per_entity: Dict[str, Dict[str, Any]] = {}
    for e in events:
        eid = e.get("entity_id")
        if not eid:
            continue
        try:
            sb_v = float(e.get("size_before") or 0)
        except (TypeError, ValueError):
            continue
        if sb_v <= 0:
            continue
        slot = per_entity.setdefault(eid, {
            "entity_id": eid,
            "brand": e.get("brand"),
            "product_name": e.get("product_name"),
            "size_unit": e.get("size_unit"),
            "min_size": sb_v,
            "max_size": sb_v,
            "event_count": 0,
        })
        slot["min_size"] = min(slot["min_size"], sb_v)
        slot["max_size"] = max(slot["max_size"], sb_v)
        slot["event_count"] += 1

    for slot in per_entity.values():
        if slot["event_count"] < 2:
            continue
        spread = slot["max_size"] / slot["min_size"]
        if spread < WIDE_SPREAD:
            continue
        stats["sku_mashup_matched"] += 1
        if dry_run:
            continue
        severity = "high" if spread >= EXTREME_SPREAD else "med"
        new_id = raise_flag(
            sb,
            flag_kind="sku_mashup",
            severity=severity,
            detected_by="backfill_v1",
            entity_id=slot["entity_id"],
            detail={
                "brand": slot["brand"],
                "product_name": slot["product_name"],
                "size_unit": slot["size_unit"],
                "min_size": slot["min_size"],
                "max_size": slot["max_size"],
                "spread_ratio": round(spread, 2),
                "event_count": slot["event_count"],
                "backfill": True,
            },
        )
        if new_id:
            stats["sku_mashup_inserted"] += 1
        else:
            stats["sku_mashup_already_open"] += 1


def detect_mixed_units(
    sb,
    events: List[Dict[str, Any]],
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Flag entities with > 1 size_unit across their events."""
    per_entity: Dict[str, Dict[str, Any]] = {}
    for e in events:
        eid = e.get("entity_id")
        unit = (e.get("size_unit") or "").strip().lower()
        if not eid or not unit:
            continue
        slot = per_entity.setdefault(eid, {
            "entity_id": eid,
            "brand": e.get("brand"),
            "product_name": e.get("product_name"),
            "units": defaultdict(int),
            "event_count": 0,
        })
        slot["units"][unit] += 1
        slot["event_count"] += 1

    for slot in per_entity.values():
        units = dict(slot["units"])
        if len(units) <= 1:
            continue
        stats["mixed_units_matched"] += 1
        if dry_run:
            continue
        sorted_units = sorted(units.items(), key=lambda kv: -kv[1])
        majority_unit, _ = sorted_units[0]
        minority = [u for u, _ in sorted_units[1:]]
        new_id = raise_flag(
            sb,
            flag_kind="mixed_units",
            severity="med",
            detected_by="backfill_v1",
            entity_id=slot["entity_id"],
            detail={
                "brand": slot["brand"],
                "product_name": slot["product_name"],
                "event_count": slot["event_count"],
                "majority_unit": majority_unit,
                "minority_units": ", ".join(minority),
                "units_breakdown": ", ".join(
                    f"{u}={n}" for u, n in sorted_units
                ),
                "backfill": True,
            },
        )
        if new_id:
            stats["mixed_units_inserted"] += 1
        else:
            stats["mixed_units_already_open"] += 1


def detect_stuck_claims(
    sb,
    dry_run: bool,
    stats: Dict[str, int],
) -> None:
    """Mirror of the forward detector in cleanup_stuck_matched._flag_stuck_unresolved.
    Pulls every claim with status='matched' AND matched_entity_id NULL AND
    extracted_at < now() - 7 days, flags each."""
    threshold = (datetime.now(timezone.utc) - timedelta(days=STUCK_CLAIM_DAYS)).isoformat()
    resp = (
        sb.table("claims")
        .select("id, brand, product_name, extracted_at")
        .eq("status", "matched")
        .is_("matched_entity_id", "null")
        .lt("extracted_at", threshold)
        .limit(10000)
        .execute()
    )
    rows = resp.data or []
    for r in rows:
        stats["stuck_claim_matched"] += 1
        if dry_run:
            continue
        new_id = raise_flag(
            sb,
            flag_kind="stuck_approved_claim",
            severity="med",
            detected_by="backfill_v1",
            claim_id=r["id"],
            detail={
                "brand": r.get("brand"),
                "product_name": r.get("product_name"),
                "extracted_at": r.get("extracted_at"),
                "backfill": True,
            },
        )
        if new_id:
            stats["stuck_claim_inserted"] += 1
        else:
            stats["stuck_claim_already_open"] += 1


# ────────────────────────────── runner ──────────────────────────────


def run(sb, only: Optional[Set[str]], dry_run: bool) -> Dict[str, int]:
    stats: Dict[str, int] = defaultdict(int)

    def should(kind: str) -> bool:
        return only is None or kind in only

    if should("short_brand") or should("fuzzy_brand_collision"):
        LOG.info("Fetching entities…")
        entities = _paginate(lambda: (
            sb.table("product_entities")
            .select("id, brand, canonical_name, is_retracted")
            .eq("is_retracted", False)
            .order("id")
        ))
        LOG.info("  %d entities", len(entities))

        # Enrich entities with event_count for fuzzy_brand_collision target picking.
        if should("fuzzy_brand_collision"):
            ev_counts = defaultdict(int)
            ev_pages = _paginate(lambda: (
                sb.table("published_changes")
                .select("entity_id")
                .eq("is_retracted", False)
                .not_.is_("entity_id", "null")
                .order("entity_id")
            ))
            for r in ev_pages:
                eid = r.get("entity_id")
                if eid:
                    ev_counts[eid] += 1
            for ent in entities:
                ent["event_count"] = ev_counts.get(ent["id"], 0)

        if should("short_brand"):
            LOG.info("Running detect_short_brand…")
            detect_short_brand(sb, entities, dry_run, stats)
        if should("fuzzy_brand_collision"):
            LOG.info("Running detect_fuzzy_brand_collision…")
            detect_fuzzy_brand_collision(sb, entities, dry_run, stats)

    if should("size_outlier") or should("sku_mashup") or should("mixed_units"):
        LOG.info("Fetching events…")
        events = _paginate(lambda: (
            sb.table("published_changes")
            .select(
                "id, entity_id, brand, product_name, "
                "size_before, size_after, size_unit, evidence_count, is_retracted"
            )
            .eq("is_retracted", False)
            .order("id")
        ))
        LOG.info("  %d events", len(events))

        if should("size_outlier"):
            LOG.info("Running detect_size_outlier…")
            detect_size_outlier(sb, events, dry_run, stats)
        if should("sku_mashup"):
            LOG.info("Running detect_sku_mashup…")
            detect_sku_mashup(sb, events, dry_run, stats)
        if should("mixed_units"):
            LOG.info("Running detect_mixed_units…")
            detect_mixed_units(sb, events, dry_run, stats)

    if should("stuck_approved_claim"):
        LOG.info("Running detect_stuck_claims…")
        detect_stuck_claims(sb, dry_run, stats)

    return dict(stats)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count matches without writing data_quality_flags rows.",
    )
    parser.add_argument(
        "--only",
        nargs="*",
        choices=ALL_KINDS,
        help="Only run these detector kinds. Default: all six.",
    )
    args = parser.parse_args()
    only: Optional[Set[str]] = set(args.only) if args.only else None

    sb = _get_client()
    LOG.info("Mode: %s", "DRY-RUN (no writes)" if args.dry_run else "APPLY")
    LOG.info("Kinds: %s", ", ".join(sorted(only)) if only else "all six")

    stats = run(sb, only=only, dry_run=args.dry_run)

    LOG.info("Done. Stats:")
    # Group by kind for readable output.
    for kind in ALL_KINDS:
        matched = stats.get(f"{kind}_matched", 0)
        inserted = stats.get(f"{kind}_inserted", 0)
        already = stats.get(f"{kind}_already_open", 0)
        if matched == 0 and inserted == 0 and already == 0:
            continue
        LOG.info(
            "  %-25s matched=%d inserted=%d already_open=%d",
            kind, matched, inserted, already,
        )


if __name__ == "__main__":
    main()
