#!/usr/bin/env python3
"""
Promote approved claims into the product catalog.

Flow: claims (approved) -> product_entities -> pack_variants ->
      variant_observations -> change_candidates -> published_changes

Usage:
    python -m pipeline promote_claims [--limit N] [--dry-run]
"""
import os
import sys
import argparse
import hashlib
from datetime import datetime, timezone, date
from typing import Any, Dict, List, Optional, Tuple

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


def get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_approved_claims(sb, limit: int = 0) -> List[Dict[str, Any]]:
    """Fetch approved claims that haven't been promoted yet."""
    q = (sb.table("claims")
         .select("*")
         .eq("status", "approved")
         .is_("matched_entity_id", "null")
         .order("extracted_at", desc=False))
    if limit > 0:
        q = q.limit(limit)
    resp = q.execute()
    return resp.data or []


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
        "skipped_no_size": 0,
        "errors": 0,
    }

    # Cache for entity dedup
    entity_cache = {}  # type: Dict[str, str]  # entity_key -> entity_id

    for i, claim in enumerate(claims):
        try:
            brand = normalize_brand(claim.get("brand"))
            name = normalize_name(claim.get("product_name"))
            old_size = claim.get("old_size")
            new_size = claim.get("new_size")
            old_unit = claim.get("old_size_unit", "oz")
            new_unit = claim.get("new_size_unit", old_unit or "oz")
            size_unit = new_unit or old_unit or "oz"

            # Skip claims without any size data
            if not old_size and not new_size:
                stats["skipped_no_size"] += 1
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

            # 2. Create pack_variant
            variant_name = f"{name} ({new_size or old_size}{size_unit})"
            variant_resp = (sb.table("pack_variants")
                          .insert({
                              "entity_id": entity_id,
                              "variant_name": variant_name[:200],
                              "current_size": new_size or old_size,
                              "size_unit": size_unit,
                              "upc": claim.get("upc"),
                          })
                          .execute())
            variant_id = variant_resp.data[0]["id"]
            stats["variants_created"] += 1

            # 3. Create variant_observations (before and after)
            obs_date = claim.get("observed_date") or date.today().isoformat()
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

            if obs_before_id and obs_after_id and old_size and new_size:
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

                # 5. Create published_change
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
                     "evidence_summary": [{
                         "source": "claim",
                         "claim_id": str(claim["id"]),
                         "description": claim.get("change_description", ""),
                     }],
                 })
                 .execute())
                stats["published"] += 1

            # 6. Update claim's matched_entity_id
            (sb.table("claims")
             .update({
                 "matched_entity_id": entity_id,
                 "matched_variant_id": variant_id,
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
    parser = argparse.ArgumentParser(description="Promote approved claims to product catalog")
    parser.add_argument("--limit", type=int, default=0, help="Max claims to process (0=all)")
    parser.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    args = parser.parse_args()

    sb = get_client()

    print("Fetching approved claims...")
    claims = fetch_approved_claims(sb, limit=args.limit)
    print(f"Found {len(claims)} approved claims to promote")

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
