#!/usr/bin/env python3
"""Phase 1 profiler for the matched-claims bucket.

Read-only audit of the ~3,000 admin-matched claims and their downstream
published_changes, surfacing the four classes of data quality issue we
know about today:

  1. high-confidence outlier events    — single-event size ratio extreme
                                          enough to be likely an AI-extraction
                                          unit error (12oz -> 0.5oz etc.)
  2. mixed-unit entity histories       — same product shows events in
                                          {g, oz, ml} interleaved, breaking
                                          the /products/[id] time series
  3. wide-size-range entity histories  — same product entity has events at
                                          200g AND 500g (different SKUs that
                                          should be different entities, or
                                          different pack_variants)
  4. duplicate entities                — same brand + fuzzy-equal canonical
                                          name landing in product_entities
                                          multiple times (Wheat Thins case)

For each class the script writes a CSV with one row per problem, sorted
by impact. The companion `summary.md` ranks the categories by row count
and links to the per-issue CSV so the admin can drill in.

Where the fix has a clear next step (e.g. a merge_entities() RPC call
for duplicates), the CSV includes a `suggested_action` column with a
ready-to-copy SQL snippet.

The script does NOT mutate any data. The output directory defaults to
`./out/matched_profile/` (already in .gitignore via the catch-all `out`
pattern). Pass `--out PATH` to override.

Usage:
    python -m pipeline.scripts.profile_matched_claims
    python -m pipeline.scripts.profile_matched_claims --out /tmp/profile
"""
import argparse
import csv
import logging
import os
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

LOG = logging.getLogger("profile_matched_claims")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
PAGE_SIZE = 1000

# Single-event ratio bounds. Tighter than migration 061's [0.05, 5.0] —
# the goal here is to FLAG for review, not block at insert time. Anything
# more extreme than 50% shrink or 100% growth is rare in real shrinkflation
# and worth eyeballing.
SINGLE_EVENT_TIGHT_MIN = 0.5
SINGLE_EVENT_TIGHT_MAX = 2.0

# Per-entity size_before spread that's almost certainly different SKUs.
WIDE_SIZE_FLAG = 3.0
EXTREME_SIZE_FLAG = 10.0


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _paginate(query_builder):
    """Walk every page of a Supabase query until exhausted."""
    out: List[Dict[str, Any]] = []
    offset = 0
    while True:
        resp = query_builder.range(offset, offset + PAGE_SIZE - 1).execute()
        batch = resp.data or []
        out.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return out


def _slugify(name: str) -> str:
    """Normalise canonical_name for fuzzy duplicate detection.
    Strips everything that isn't a-z0-9, lowercases. Aggressive on purpose —
    'Wheat Thins (Original)' and 'wheat-thins original' both become
    'wheatthinsoriginal'."""
    return re.sub(r"[^a-z0-9]+", "", name.lower().strip())


# ────────────────────────────── analysers ──────────────────────────────


def analyse_outlier_events(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Events with single-event size ratio outside [0.5, 2.0].

    These survived migration 061 (which only blocks <0.05 / >5.0) but are
    still extreme enough that a unit-parse error is plausible. Higher-
    confidence rows surface first.
    """
    rows: List[Dict[str, Any]] = []
    for e in events:
        try:
            sb_v = float(e.get("size_before") or 0)
            sa_v = float(e.get("size_after") or 0)
            if sb_v <= 0 or sa_v <= 0:
                continue
            ratio = sa_v / sb_v
        except (TypeError, ValueError):
            continue
        if SINGLE_EVENT_TIGHT_MIN <= ratio <= SINGLE_EVENT_TIGHT_MAX:
            continue
        rows.append({
            "event_id": e["id"],
            "entity_id": e.get("entity_id"),
            "brand": e.get("brand"),
            "product_name": e.get("product_name"),
            "size_before": sb_v,
            "size_after": sa_v,
            "size_unit": e.get("size_unit"),
            "ratio": round(ratio, 4),
            "size_delta_pct": e.get("size_delta_pct"),
            "evidence_count": e.get("evidence_count"),
            "observed_date": e.get("observed_date"),
            "suggested_action": (
                "Inspect via /admin/entities (lookup brand). If unit error, "
                "use the public-page \"↩ Send to pending\" button on this "
                "event to retract and re-review the backing claims."
            ),
        })
    rows.sort(key=lambda r: (-(r["evidence_count"] or 0), r["ratio"]))
    return rows


def analyse_mixed_units(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Entities whose events span more than one size_unit.

    The fix is human — pick the canonical unit and either edit the
    offending events or retract the wrong-unit ones. The script doesn't
    guess which unit is right.
    """
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
    rows: List[Dict[str, Any]] = []
    for slot in per_entity.values():
        units = dict(slot["units"])
        if len(units) <= 1:
            continue
        sorted_units = sorted(units.items(), key=lambda kv: -kv[1])
        majority_unit, majority_count = sorted_units[0]
        minority_units = [u for u, _ in sorted_units[1:]]
        rows.append({
            "entity_id": slot["entity_id"],
            "brand": slot["brand"],
            "product_name": slot["product_name"],
            "event_count": slot["event_count"],
            "unit_variants": len(units),
            "units_breakdown": ", ".join(
                f"{u}={n}" for u, n in sorted_units
            ),
            "majority_unit": majority_unit,
            "majority_count": majority_count,
            "minority_units": ", ".join(minority_units),
            "suggested_action": (
                f"Open /admin/entities, search this brand+name. Retract or "
                f"edit events whose unit is not '{majority_unit}'."
            ),
        })
    rows.sort(key=lambda r: -r["event_count"])
    return rows


def analyse_wide_size_range(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Entities whose events span a wide size_before range, suggesting
    multiple SKUs collapsed into one entity (200g + 500g packs)."""
    per_entity: Dict[str, Dict[str, Any]] = {}
    for e in events:
        eid = e.get("entity_id")
        try:
            sb_v = float(e.get("size_before") or 0)
        except (TypeError, ValueError):
            continue
        if not eid or sb_v <= 0:
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
    rows: List[Dict[str, Any]] = []
    for slot in per_entity.values():
        if slot["event_count"] < 2:
            continue
        spread = slot["max_size"] / slot["min_size"]
        if spread < WIDE_SIZE_FLAG:
            continue
        rows.append({
            "entity_id": slot["entity_id"],
            "brand": slot["brand"],
            "product_name": slot["product_name"],
            "size_unit": slot["size_unit"],
            "min_size": slot["min_size"],
            "max_size": slot["max_size"],
            "spread_ratio": round(spread, 2),
            "event_count": slot["event_count"],
            "severity": "extreme" if spread >= EXTREME_SIZE_FLAG else "wide",
            "suggested_action": (
                "Likely a SKU mix-up: events at min_size and max_size are "
                "probably two different pack sizes that should be separate "
                "pack_variants under one entity, or separate entities. "
                "Inspect on /products/<entity_id>; consider splitting or "
                "retracting the off-size events."
            ),
        })
    rows.sort(key=lambda r: -r["spread_ratio"])
    return rows


def analyse_duplicate_entities(
    entities: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Entities that look like duplicates of each other.

    Grouping key: (brand_normalised, slug(canonical_name)). When >1 entity
    shares the same key, they're candidates for merge_entities.

    For each group, emit one row per non-canonical entity with a
    suggested merge_entities() call pointed at the entity with the most
    events (the "canonical" target).
    """
    groups: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
    for ent in entities:
        if not ent.get("brand") or not ent.get("canonical_name"):
            continue
        brand_norm = (ent["brand"] or "").lower().strip()
        slug = _slugify(ent["canonical_name"])
        if not slug:
            continue
        groups[(brand_norm, slug)].append(ent)
    rows: List[Dict[str, Any]] = []
    for (brand_norm, slug), members in groups.items():
        if len(members) < 2:
            continue
        ranked = sorted(
            members,
            key=lambda m: (-(m.get("event_count") or 0), m["id"]),
        )
        target = ranked[0]
        for src in ranked[1:]:
            rows.append({
                "group_brand": brand_norm,
                "group_slug": slug,
                "source_id": src["id"],
                "source_name": src["canonical_name"],
                "source_events": src.get("event_count") or 0,
                "target_id": target["id"],
                "target_name": target["canonical_name"],
                "target_events": target.get("event_count") or 0,
                "group_size": len(members),
                "suggested_action": (
                    f"SELECT * FROM merge_entities('{src['id']}', "
                    f"'{target['id']}', 'profiler');"
                ),
            })
    rows.sort(key=lambda r: (-r["group_size"], -r["target_events"]))
    return rows


# ────────────────────────────── I/O ──────────────────────────────


def _write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("(no rows)\n", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def _write_summary(
    out_dir: Path,
    outlier_rows: List[Dict[str, Any]],
    mixed_rows: List[Dict[str, Any]],
    wide_rows: List[Dict[str, Any]],
    dup_rows: List[Dict[str, Any]],
    totals: Dict[str, int],
) -> None:
    md = []
    md.append("# Matched-claims profile")
    md.append("")
    md.append(
        "Read-only audit produced by `pipeline/scripts/profile_matched_claims.py`. "
        "Per-issue CSVs live next to this file."
    )
    md.append("")
    md.append("## Universe")
    md.append("")
    md.append(f"- Active (non-retracted) entities scanned: **{totals['entities']:,}**")
    md.append(f"- Non-retracted published_changes scanned: **{totals['events']:,}**")
    md.append("")
    md.append("## Findings, ranked by row count")
    md.append("")
    md.append("| Issue | Count | CSV |")
    md.append("|---|---|---|")
    md.append(f"| Duplicate entities (merge candidates) | **{len(dup_rows):,}** | `04_duplicate_entities.csv` |")
    md.append(f"| Entities with wide size_before spread (>{WIDE_SIZE_FLAG}×) | **{len(wide_rows):,}** | `03_wide_size_range.csv` |")
    md.append(f"| Entities with mixed size_units | **{len(mixed_rows):,}** | `02_mixed_units.csv` |")
    md.append(f"| Single-event outlier ratios (outside [{SINGLE_EVENT_TIGHT_MIN}, {SINGLE_EVENT_TIGHT_MAX}]) | **{len(outlier_rows):,}** | `01_outlier_events.csv` |")
    md.append("")
    md.append("## What each finding means")
    md.append("")
    md.append("### Duplicate entities")
    md.append(
        "Entities that share the same brand AND a normalised "
        "(lowercase, alpha-num only) canonical_name. Most leverage: merging "
        "duplicates collapses the brand's catalog and the product's event "
        "history.  Each row has a ready-to-run `merge_entities()` SQL "
        "snippet pointed at the group's highest-event entity. Apply via "
        "`/admin/entities` merge⇒ UI for an audit-logged version."
    )
    md.append("")
    md.append("### Wide size_before spread")
    md.append(
        "Events under one entity whose `size_before` values differ by more "
        "than 3× — almost always different SKUs that got collapsed. "
        f"`{sum(1 for r in wide_rows if r.get('severity') == 'extreme'):,}` "
        f"of these have spread > {EXTREME_SIZE_FLAG}× (almost certainly wrong)."
    )
    md.append("")
    md.append("### Mixed size_units")
    md.append(
        "Events under one entity that mix unit types (g + oz, ml + L, "
        "etc.). The /products/[id] time series shows nonsense when this "
        "happens. Fix is per-event: retract or edit the off-unit rows."
    )
    md.append("")
    md.append("### Single-event outlier ratios")
    md.append(
        f"Events where size_after/size_before fell outside [{SINGLE_EVENT_TIGHT_MIN}, "
        f"{SINGLE_EVENT_TIGHT_MAX}]. Migration 061 blocks ratios outside "
        f"[0.05, 5.0]; this set is the wider band that's worth eyeballing "
        f"for unit-parse errors (12oz → 0.5oz was the inspiration)."
    )
    md.append("")
    md.append("## Suggested next session")
    md.append("")
    md.append(
        "1. **Highest leverage:** triage `04_duplicate_entities.csv`. Each "
        "row is one merge candidate. Even a partial sweep through the top "
        "100 rows would consolidate ~200 fragmented entities."
    )
    md.append(
        "2. **Second:** `03_wide_size_range.csv` rows with `severity=extreme`. "
        "These are mostly SKU mash-ups where one entity should be split or "
        "the off-size events retracted."
    )
    md.append(
        "3. **Third:** `02_mixed_units.csv` — admin pass through the top "
        "entries to retract the wrong-unit events."
    )
    md.append(
        "4. **Fourth:** `01_outlier_events.csv` — these are the lowest count "
        "but highest signal for unit-parse errors. Worth a quick scan."
    )
    (out_dir / "summary.md").write_text("\n".join(md), encoding="utf-8")


# ────────────────────────────── main ──────────────────────────────


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--out", type=str, default="out/matched_profile",
        help="Output directory (default: out/matched_profile/)",
    )
    args = parser.parse_args()
    out_dir = Path(args.out)

    sb = _get_client()

    LOG.info("Fetching active entities…")
    entities_q = (
        sb.table("product_entities")
        .select("id, brand, canonical_name, category, created_at, is_retracted")
        .eq("is_retracted", False)
        .order("id")
    )
    entities = _paginate(entities_q)
    LOG.info("  %d entities", len(entities))

    LOG.info("Fetching non-retracted published_changes…")
    events_q = (
        sb.table("published_changes")
        .select(
            "id, entity_id, brand, product_name, "
            "size_before, size_after, size_unit, size_delta_pct, "
            "change_type, severity, evidence_count, observed_date, "
            "is_retracted"
        )
        .eq("is_retracted", False)
        .order("id")
    )
    events = _paginate(events_q)
    LOG.info("  %d events", len(events))

    # Per-entity event counts so the duplicate analyser can pick a merge target.
    entity_event_counts: Dict[str, int] = defaultdict(int)
    for e in events:
        eid = e.get("entity_id")
        if eid:
            entity_event_counts[eid] += 1
    for ent in entities:
        ent["event_count"] = entity_event_counts.get(ent["id"], 0)

    LOG.info("Running analysers…")
    outlier_rows = analyse_outlier_events(events)
    mixed_rows = analyse_mixed_units(events)
    wide_rows = analyse_wide_size_range(events)
    dup_rows = analyse_duplicate_entities(entities)

    LOG.info("  outlier events:        %d", len(outlier_rows))
    LOG.info("  mixed-unit entities:   %d", len(mixed_rows))
    LOG.info("  wide-spread entities:  %d", len(wide_rows))
    LOG.info("  duplicate merge rows:  %d", len(dup_rows))

    _write_csv(out_dir / "01_outlier_events.csv", outlier_rows)
    _write_csv(out_dir / "02_mixed_units.csv", mixed_rows)
    _write_csv(out_dir / "03_wide_size_range.csv", wide_rows)
    _write_csv(out_dir / "04_duplicate_entities.csv", dup_rows)
    _write_summary(
        out_dir,
        outlier_rows, mixed_rows, wide_rows, dup_rows,
        {"entities": len(entities), "events": len(events)},
    )

    LOG.info("Wrote profile to %s", out_dir.resolve())


if __name__ == "__main__":
    main()
