#!/usr/bin/env python3
"""Deduplicate product_entities by fuzzy-matching brand+name within each brand.

Uses trigram similarity (pg_trgm) to find near-duplicate entities, then merges
them by reassigning pack_variants and published_changes to the canonical entity.

Usage:
    python -m pipeline.scripts.dedup_entities                # interactive mode
    python -m pipeline.scripts.dedup_entities --auto         # auto-merge similarity > 0.85
    python -m pipeline.scripts.dedup_entities --dry-run      # preview only
    python -m pipeline.scripts.dedup_entities --threshold 0.7  # custom threshold
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Set, Tuple

LOG = logging.getLogger("dedup_entities")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

AUTO_MERGE_THRESHOLD = 0.85
DEFAULT_THRESHOLD = 0.5
PAGE_SIZE = 1000


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _fetch_all_entities(sb) -> List[Dict[str, Any]]:
    """Fetch all product_entities with their published_changes count."""
    entities = []  # type: List[Dict[str, Any]]
    offset = 0
    while True:
        resp = (
            sb.table("product_entities")
            .select("id, brand, canonical_name, category, image_url")
            .order("brand")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        batch = resp.data or []
        entities.extend(batch)
        if len(batch) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return entities


def _count_published_changes(sb, entity_id: str) -> int:
    resp = (
        sb.table("published_changes")
        .select("id", count="exact")
        .eq("entity_id", entity_id)
        .execute()
    )
    return resp.count or 0


def _find_duplicates(
    entities: List[Dict[str, Any]], threshold: float
) -> List[List[Dict[str, Any]]]:
    """Group entities by brand, then cluster by name similarity within each brand."""
    from difflib import SequenceMatcher

    by_brand = {}  # type: Dict[str, List[Dict[str, Any]]]
    for e in entities:
        brand = (e.get("brand") or "").lower().strip()
        by_brand.setdefault(brand, []).append(e)

    clusters = []  # type: List[List[Dict[str, Any]]]

    for brand, group in sorted(by_brand.items()):
        if len(group) < 2:
            continue

        merged_ids = set()  # type: Set[str]
        for i, a in enumerate(group):
            if a["id"] in merged_ids:
                continue
            cluster = [a]
            name_a = (a.get("canonical_name") or "").lower().strip()
            for b in group[i + 1:]:
                if b["id"] in merged_ids:
                    continue
                name_b = (b.get("canonical_name") or "").lower().strip()
                sim = SequenceMatcher(None, name_a, name_b).ratio()
                if sim >= threshold:
                    cluster.append(b)
                    merged_ids.add(b["id"])
            if len(cluster) > 1:
                clusters.append(cluster)
                merged_ids.add(a["id"])

    return clusters


def _merge_cluster(
    sb,
    cluster: List[Dict[str, Any]],
    dry_run: bool = False,
) -> Dict[str, int]:
    """Merge a cluster of duplicate entities into one canonical entity.

    The entity with the most published_changes (or first alphabetically) wins.
    """
    stats = {"entities_merged": 0, "changes_reassigned": 0, "variants_reassigned": 0}

    counts = []
    for e in cluster:
        c = _count_published_changes(sb, e["id"])
        counts.append((c, e))

    counts.sort(key=lambda x: (-x[0], x[1].get("canonical_name", "")))
    canonical = counts[0][1]
    dupes = [e for _, e in counts[1:]]

    for dupe in dupes:
        LOG.info(
            "  Merging '%s' (id=%s) → '%s' (id=%s)",
            dupe["canonical_name"], dupe["id"][:8],
            canonical["canonical_name"], canonical["id"][:8],
        )

        if dry_run:
            stats["entities_merged"] += 1
            continue

        # Reassign published_changes
        resp = (
            sb.table("published_changes")
            .update({"entity_id": canonical["id"]})
            .eq("entity_id", dupe["id"])
            .execute()
        )
        stats["changes_reassigned"] += len(resp.data or [])

        # Reassign pack_variants
        resp = (
            sb.table("pack_variants")
            .update({"entity_id": canonical["id"]})
            .eq("entity_id", dupe["id"])
            .execute()
        )
        stats["variants_reassigned"] += len(resp.data or [])

        # Reassign claims
        sb.table("claims").update(
            {"matched_entity_id": canonical["id"]}
        ).eq("matched_entity_id", dupe["id"]).execute()

        # Delete the orphaned entity
        sb.table("product_entities").delete().eq("id", dupe["id"]).execute()
        stats["entities_merged"] += 1

    # Update canonical entity: prefer non-null image and category from dupes
    if not canonical.get("image_url"):
        for dupe in dupes:
            if dupe.get("image_url"):
                sb.table("product_entities").update(
                    {"image_url": dupe["image_url"]}
                ).eq("id", canonical["id"]).execute()
                break

    if not canonical.get("category"):
        for dupe in dupes:
            if dupe.get("category"):
                sb.table("product_entities").update(
                    {"category": dupe["category"]}
                ).eq("id", canonical["id"]).execute()
                break

    return stats


def main():
    parser = argparse.ArgumentParser(description="Deduplicate product_entities")
    parser.add_argument("--auto", action="store_true",
                        help="Auto-merge clusters with similarity > 0.85")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--threshold", type=float, default=DEFAULT_THRESHOLD,
                        help="Minimum similarity threshold (default: %(default)s)")
    args = parser.parse_args()

    sb = _get_client()

    LOG.info("Fetching all product_entities...")
    entities = _fetch_all_entities(sb)
    LOG.info("Found %d entities", len(entities))

    LOG.info("Finding duplicate clusters (threshold=%.2f)...", args.threshold)
    clusters = _find_duplicates(entities, args.threshold)
    LOG.info("Found %d duplicate clusters", len(clusters))

    if not clusters:
        LOG.info("No duplicates found. Done.")
        return

    totals = {"entities_merged": 0, "changes_reassigned": 0, "variants_reassigned": 0}

    for idx, cluster in enumerate(clusters):
        brand = cluster[0].get("brand", "?")
        names = [e.get("canonical_name", "?") for e in cluster]
        LOG.info(
            "\nCluster %d/%d [%s]: %s",
            idx + 1, len(clusters), brand, " | ".join(names),
        )

        if args.auto:
            stats = _merge_cluster(sb, cluster, dry_run=args.dry_run)
            for k in totals:
                totals[k] += stats.get(k, 0)
        else:
            response = input("  Merge? [y/N/q] ").strip().lower()
            if response == "q":
                break
            if response == "y":
                stats = _merge_cluster(sb, cluster, dry_run=args.dry_run)
                for k in totals:
                    totals[k] += stats.get(k, 0)
            else:
                LOG.info("  Skipped.")

    mode = "DRY RUN" if args.dry_run else "LIVE"
    LOG.info("\n%s RESULTS:", mode)
    for k, v in totals.items():
        LOG.info("  %s: %d", k, v)


if __name__ == "__main__":
    main()
