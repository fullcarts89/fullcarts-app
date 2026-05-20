#!/usr/bin/env python3
"""
Promote admin-matched claims into the product catalog.

A claim is "admin-matched" when an admin clicked Approve in /admin/claims
(which sets status='matched') but no published_change has been built for it
yet (matched_entity_id IS NULL).

Flow: claims (matched, no entity) -> product_entities -> pack_variants ->
      variant_observations -> change_candidates -> published_changes

The status stays 'matched' the whole time — this script only fills in the
matched_entity_id / matched_variant_id columns and creates the downstream
event rows. Claims folded into an existing event flip to status='merged'
(migration 060 split that bucket out from the evidence-wall 'evidence' status).

Usage:
    python -m pipeline promote_claims [--limit N] [--dry-run]
"""
import os
import sys
import argparse
import hashlib
from datetime import datetime, timezone, date, timedelta
from typing import Any, Dict, List, Optional, Tuple

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# (entity_id, size_before, size_after) is the canonical dedup key for an
# event. A product shrinks 200g → 180g once. If a new claim with the same
# entity and same sizes arrives later (whether minutes or years), it's
# evidence for the same event, not a new one. We do NOT use a date window:
#   - Tight windows (e.g. 30 days) missed cases where GDELT re-indexed the
#     same wire story years later as a second wave, producing apparent
#     "new" events with identical headlines + sizes
#   - A genuine re-shrinkage of the exact same magnitude is theoretically
#     possible but extremely rare (would require a full restoration first)
#     and we'd rather collapse the rare case than under-report syndication
EVENT_DEDUP_WINDOW_DAYS = None  # retained for legacy callers; None = no window


def get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_matched_claims_to_promote(sb, limit: int = 0) -> List[Dict[str, Any]]:
    """Fetch matched claims that don't yet have a published_change.

    `matched_entity_id IS NULL` is the marker for "admin clicked Approve
    but the daily promote run hasn't built the event yet."
    """
    q = (sb.table("claims")
         .select("*")
         .eq("status", "matched")
         .is_("matched_entity_id", "null")
         .order("extracted_at", desc=False))
    if limit > 0:
        q = q.limit(limit)
    resp = q.execute()
    return resp.data or []


# Backwards-compat alias for any caller still importing the old name.
fetch_approved_claims = fetch_matched_claims_to_promote


def normalize_brand(brand: Optional[str]) -> str:
    if not brand:
        return "Unknown"
    return brand.strip().title()


def normalize_name(name: Optional[str]) -> str:
    if not name:
        return "Unknown Product"
    return name.strip()


def entity_key(brand: str, name: str) -> str:
    """Deterministic key for deduplication."""
    raw = (brand.lower().strip() + "|" + name.lower().strip())
    return hashlib.md5(raw.encode()).hexdigest()[:16]


def calc_delta_pct(old: Optional[float], new: Optional[float]) -> Optional[float]:
    if old and new and old > 0:
        return round(((new - old) / old) * 100, 2)
    return None


# Reject AI extraction errors like "1L -> 900L" or "1kg -> 1000kg" before they
# land in published_changes. Mirrors the CHECK constraint added by migration
# 061. Threshold rationale lives in that migration file.
SIZE_RATIO_MIN = 0.05
SIZE_RATIO_MAX = 5.0


def sane_size_ratio(old_size: Optional[float], new_size: Optional[float]) -> bool:
    """Return True if (old_size, new_size) clears the sanity bounds.

    Both-null is fine (skimpflation claims carry no numeric size change).
    Either-side null is also fine — no ratio to evaluate. A zero or negative
    old_size is rejected as suspect (legitimate products never start at zero).
    """
    if old_size is None or new_size is None:
        return True
    try:
        if old_size <= 0:
            return False
        ratio = float(new_size) / float(old_size)
    except (TypeError, ValueError, ZeroDivisionError):
        return False
    return SIZE_RATIO_MIN <= ratio <= SIZE_RATIO_MAX


def find_existing_event(
    sb,
    entity_id: str,
    size_before: float,
    size_after: float,
    observed_date_str: Optional[str] = None,  # kept for backwards-compat; unused
    window_days: Optional[int] = EVENT_DEDUP_WINDOW_DAYS,
) -> Optional[Dict[str, Any]]:
    """Look for an already-published_changes row that documents the same event.

    Dedup key: (entity_id, size_before, size_after). A product can only shrink
    from 200g to 180g once — any future report with that same (entity, before,
    after) tuple is referring to the same event, regardless of when it was
    reported. Returns the earliest matching row.

    `observed_date_str` and `window_days` are retained as parameters for
    backwards-compatibility with callers passing them through, but they no
    longer constrain the query.
    """
    resp = (sb.table("published_changes")
            .select("id, evidence_count, evidence_summary, observed_date")
            .eq("entity_id", entity_id)
            .eq("size_before", size_before)
            .eq("size_after", size_after)
            .eq("is_retracted", False)
            .order("observed_date")
            .limit(1)
            .execute())

    return resp.data[0] if resp.data else None


def classify_change(delta_pct: Optional[float]) -> Tuple[str, str, bool]:
    """Returns (change_type, severity, is_shrinkflation)."""
    if delta_pct is None:
        return ("shrinkflation", "moderate", True)
    if delta_pct < -20:
        return ("shrinkflation", "major", True)
    elif delta_pct < -5:
        return ("shrinkflation", "moderate", True)
    elif delta_pct < 0:
        return ("shrinkflation", "minor", True)
    elif delta_pct > 5:
        return ("upsizing", "moderate", False)
    elif delta_pct > 0:
        return ("restoration", "minor", False)
    else:
        return ("shrinkflation", "minor", True)


def promote_claims(sb, claims: List[Dict], dry_run: bool = False) -> Dict[str, int]:
    """Promote a list of approved claims into the product catalog."""
    stats = {
        "claims_processed": 0,
        "entities_created": 0,
        "entities_reused": 0,
        "variants_created": 0,
        "observations_created": 0,
        "candidates_created": 0,
        "published": 0,
        "evidence_added_to_existing": 0,  # syndicated claims merged into an existing event
        "skipped_no_size": 0,
        "discarded_no_size": 0,  # no-size claims demoted out of the promote queue
        "discarded_size_sanity": 0,  # AI unit-parse errors (1L -> 900L etc.); mirrors migration 061
        "errors": 0,
    }

    # Cache for entity dedup
    entity_cache = {}  # type: Dict[str, str]  # entity_key -> entity_id

    # Preload raw_items.source_date so we can fall back to the originating
    # post/article date instead of date.today() when the AI extractor
    # didn't pick an observed_date. Falling back to today distorts the
    # /insights monthly chart by piling every dateless claim into the
    # current month. Costs one batched query for the whole run.
    raw_item_dates = {}  # type: Dict[str, str]
    raw_item_ids = list({
        c["raw_item_id"] for c in claims
        if c.get("raw_item_id") and not c.get("observed_date")
    })
    # PostgREST's `in.()` filter has a URL length limit; chunk to be safe.
    for i in range(0, len(raw_item_ids), 500):
        chunk = raw_item_ids[i : i + 500]
        try:
            resp = (sb.table("raw_items")
                    .select("id, source_date")
                    .in_("id", chunk)
                    .execute())
            for row in (resp.data or []):
                sd = row.get("source_date")
                if sd:
                    raw_item_dates[row["id"]] = sd[:10]
        except Exception:
            # Don't fail the whole promote run if the preload errors —
            # we'll just fall back to date.today() for those claims.
            pass

    for i, claim in enumerate(claims):
        try:
            brand = normalize_brand(claim.get("brand"))
            name = normalize_name(claim.get("product_name"))
            old_size = claim.get("old_size")
            new_size = claim.get("new_size")
            old_unit = claim.get("old_size_unit", "oz")
            new_unit = claim.get("new_size_unit", old_unit or "oz")
            size_unit = new_unit or old_unit or "oz"

            # Skip claims without any size data. Without a before/after size we
            # can't produce a published_change row — but if we leave the claim
            # in 'matched' it sits in the promote queue forever, getting
            # re-fetched on every daily run. Demote to 'discarded' so it drops
            # out cleanly.
            if not old_size and not new_size:
                stats["skipped_no_size"] += 1
                if not dry_run:
                    (sb.table("claims")
                     .update({"status": "discarded"})
                     .eq("id", claim["id"])
                     .execute())
                    stats["discarded_no_size"] += 1
                continue

            # Reject AI unit-parse errors before they hit published_changes.
            # Mirrors the CHECK constraint installed by migration 061. The
            # constraint would block the insert anyway, but failing here
            # keeps the cron green and writes a counter so the daily summary
            # surfaces the problem instead of swallowing a 500-class error.
            if not sane_size_ratio(old_size, new_size):
                print(f"  [SKIP] claim {claim['id']} ({brand}/{name}): "
                      f"size ratio {old_size}->{new_size} outside sanity "
                      f"bounds [{SIZE_RATIO_MIN}, {SIZE_RATIO_MAX}]; "
                      f"discarding (suspected unit-parse error)")
                stats["discarded_size_sanity"] += 1
                if not dry_run:
                    (sb.table("claims")
                     .update({"status": "discarded"})
                     .eq("id", claim["id"])
                     .execute())
                continue

            ekey = entity_key(brand, name)

            if dry_run:
                stats["claims_processed"] += 1
                if ekey not in entity_cache:
                    entity_cache[ekey] = "dry-run"
                    stats["entities_created"] += 1
                else:
                    stats["entities_reused"] += 1
                if i < 5:
                    print(f"  [DRY] {brand} / {name}: {old_size}{old_unit} -> {new_size}{new_unit}")
                continue

            # 1. Find or create product_entity
            if ekey in entity_cache:
                entity_id = entity_cache[ekey]
                stats["entities_reused"] += 1
            else:
                # Try to find existing
                existing = (sb.table("product_entities")
                           .select("id")
                           .eq("brand", brand)
                           .eq("canonical_name", name)
                           .limit(1)
                           .execute())

                if existing.data:
                    entity_id = existing.data[0]["id"]
                    stats["entities_reused"] += 1
                else:
                    resp = (sb.table("product_entities")
                           .insert({
                               "canonical_name": name,
                               "brand": brand,
                               "category": claim.get("category"),
                           })
                           .execute())
                    entity_id = resp.data[0]["id"]
                    stats["entities_created"] += 1

                entity_cache[ekey] = entity_id

            # 2. Find or create pack_variant
            upc = claim.get("upc")
            variant_name = f"{name} ({new_size or old_size}{size_unit})"
            variant_id = None

            # Check for existing variant by UPC first (UNIQUE constraint)
            if upc:
                existing_var = (sb.table("pack_variants")
                               .select("id")
                               .eq("upc", upc)
                               .limit(1)
                               .execute())
                if existing_var.data:
                    variant_id = existing_var.data[0]["id"]

            if variant_id is None:
                variant_resp = (sb.table("pack_variants")
                              .insert({
                                  "entity_id": entity_id,
                                  "variant_name": variant_name[:200],
                                  "current_size": new_size or old_size,
                                  "size_unit": size_unit,
                                  "upc": upc,
                              })
                              .execute())
                variant_id = variant_resp.data[0]["id"]
                stats["variants_created"] += 1

            # 3. Create variant_observations (before and after)
            # Fallback order: AI-extracted observed_date → originating
            # raw_item's source_date → today. The middle step keeps the
            # /insights timeline honest — without it, every dateless
            # claim collapses onto today() and the chart shows a
            # spurious spike in the current month.
            obs_date = claim.get("observed_date")
            if not obs_date:
                rid = claim.get("raw_item_id")
                if rid and rid in raw_item_dates:
                    obs_date = raw_item_dates[rid]
            if not obs_date:
                obs_date = date.today().isoformat()
            obs_before_id = None
            obs_after_id = None

            if old_size:
                resp = (sb.table("variant_observations")
                       .insert({
                           "variant_id": variant_id,
                           "observed_date": obs_date,
                           "source_type": "claim_before",
                           "source_ref": str(claim["id"]),
                           "size": old_size,
                           "size_unit": old_unit or size_unit,
                           "price": claim.get("old_price"),
                           "retailer": claim.get("retailer"),
                           "raw_item_id": claim.get("raw_item_id"),
                       })
                       .execute())
                obs_before_id = resp.data[0]["id"]
                stats["observations_created"] += 1

            if new_size:
                resp = (sb.table("variant_observations")
                       .insert({
                           "variant_id": variant_id,
                           "observed_date": obs_date,
                           "source_type": "claim_after",
                           "source_ref": str(claim["id"]),
                           "size": new_size,
                           "size_unit": new_unit or size_unit,
                           "price": claim.get("new_price"),
                           "retailer": claim.get("retailer"),
                           "raw_item_id": claim.get("raw_item_id"),
                       })
                       .execute())
                obs_after_id = resp.data[0]["id"]
                stats["observations_created"] += 1

            # 4. Create change_candidate (if we have both before and after)
            candidate_id = None
            delta_pct = calc_delta_pct(old_size, new_size)
            change_type, severity, is_shrinkflation = classify_change(delta_pct)
            folded_into_existing = False

            if obs_before_id and obs_after_id and old_size and new_size:
                # Check whether this same event is already documented by a
                # prior published_change (within EVENT_DEDUP_WINDOW_DAYS).
                # If so, treat this claim as additional corroborating evidence
                # rather than a separate event. Solves the news-syndication
                # explosion where one wire story becomes dozens of rows.
                existing_event = find_existing_event(
                    sb, entity_id, old_size, new_size, obs_date,
                )

                new_evidence_entry = {
                    "source": "claim",
                    "claim_id": str(claim["id"]),
                    "description": claim.get("change_description", ""),
                }

                if existing_event:
                    # Append evidence to existing event; no new candidate /
                    # published_change row.
                    existing_summary = existing_event.get("evidence_summary") or []
                    if not isinstance(existing_summary, list):
                        existing_summary = []
                    updated_summary = existing_summary + [new_evidence_entry]
                    new_count = (existing_event.get("evidence_count") or 1) + 1
                    (sb.table("published_changes")
                     .update({
                         "evidence_summary": updated_summary,
                         "evidence_count": new_count,
                     })
                     .eq("id", existing_event["id"])
                     .execute())
                    stats["evidence_added_to_existing"] += 1
                    folded_into_existing = True
                else:
                    # First time we see this event — create candidate + published_change.
                    resp = (sb.table("change_candidates")
                           .insert({
                               "variant_id": variant_id,
                               "observation_before": obs_before_id,
                               "observation_after": obs_after_id,
                               "size_before": old_size,
                               "size_after": new_size,
                               "size_delta_pct": delta_pct or 0,
                               "price_before": claim.get("old_price"),
                               "price_after": claim.get("new_price"),
                               "change_type": change_type,
                               "severity": severity,
                               "is_shrinkflation": is_shrinkflation,
                               "status": "approved",
                               "supporting_claims": [str(claim["id"])],
                               "evidence_count": 1,
                           })
                           .execute())
                    candidate_id = resp.data[0]["id"]
                    stats["candidates_created"] += 1

                    (sb.table("published_changes")
                     .insert({
                         "candidate_id": candidate_id,
                         "variant_id": variant_id,
                         "entity_id": entity_id,
                         "brand": brand,
                         "product_name": name,
                         "size_before": old_size,
                         "size_after": new_size,
                         "size_unit": size_unit,
                         "size_delta_pct": delta_pct or 0,
                         "change_type": change_type,
                         "severity": severity,
                         "observed_date": obs_date,
                         "evidence_summary": [new_evidence_entry],
                         "evidence_count": 1,
                     })
                     .execute())
                    stats["published"] += 1

            # 6. Fill in the entity/variant link. Status is already 'matched'
            # (the admin's Approve click set it). If we folded this claim into
            # an existing event instead of publishing a new one, flip status
            # to 'merged' so the admin queue distinguishes the two. Note:
            # 'merged' was carved out of 'evidence' by migration 060; pre-060
            # rows are backfilled in the same migration.
            new_status = "merged" if folded_into_existing else "matched"
            (sb.table("claims")
             .update({
                 "matched_entity_id": entity_id,
                 "matched_variant_id": variant_id,
                 "status": new_status,
             })
             .eq("id", claim["id"])
             .execute())

            stats["claims_processed"] += 1

            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(claims)} claims...")

        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 10:
                print(f"  ERROR on claim {claim.get('id', '?')}: {e}", file=sys.stderr)
            if stats["errors"] == 10:
                print("  (suppressing further error messages)", file=sys.stderr)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Promote admin-matched claims into the product catalog")
    parser.add_argument("--limit", type=int, default=0, help="Max claims to process (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()

    sb = get_client()

    print("Fetching matched claims to promote...")
    claims = fetch_matched_claims_to_promote(sb, limit=args.limit)
    print(f"Found {len(claims)} matched claims awaiting promotion")

    if not claims:
        print("Nothing to promote.")
        return

    mode = "DRY RUN" if args.dry_run else "LIVE"
    print(f"\nPromoting claims ({mode})...")

    stats = promote_claims(sb, claims, dry_run=args.dry_run)

    print(f"\n{'='*50}")
    print(f"PROMOTION RESULTS ({mode})")
    print(f"{'='*50}")
    for key, val in stats.items():
        print(f"  {key}: {val}")


if __name__ == "__main__":
    main()
