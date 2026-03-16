#!/usr/bin/env python3
"""Vision enrichment: fill in missing claim fields from image posts using Claude Haiku Vision.

Processes Reddit posts that have an image URL. Enriches existing text claims
by filling in NULL fields (sizes, brand, product, etc.) — never creates
duplicate claims.

Examples:
  Enrich pending claims with 80%+ confidence:
    python -m pipeline.scripts.extract_claims_vision --confidence-min 0.8 --status pending

  Enrich all non-discarded claims below 30% confidence:
    python -m pipeline.scripts.extract_claims_vision --confidence-max 0.3

  Dry-run to see what would change:
    python -m pipeline.scripts.extract_claims_vision --confidence-min 0.8 --limit 10 --dry-run

Usage:
    python -m pipeline.scripts.extract_claims_vision [OPTIONS]

Options:
    --limit N              Process at most N items (default: all)
    --confidence-min F     Lower bound of confidence range (default: 0.0)
    --confidence-max F     Upper bound of confidence range (default: 1.0)
    --status STATUS        Only process claims with this status (default: all non-discarded)
    --batch-size N         Items per batch (default: 20)
    --dry-run              Print what would be extracted without writing
"""
import argparse
import re
import time
from typing import Any, Dict, List, Optional, Set

from pipeline.lib.claude_client import extract_claim_vision
from pipeline.lib.extraction_prompt import (
    SYSTEM_PROMPT_VISION,
    build_reddit_vision_message,
    parse_claim_response,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("extract_claims_vision")

TEXT_EXTRACTOR = "haiku-v1"
POSTGREST_PAGE_SIZE = 1000

# Image URL patterns that Claude Vision can process
_IMAGE_PATTERNS = [
    r"i\.redd\.it/",
    r"i\.imgur\.com/",
    r"preview\.redd\.it/",
    r"external-preview\.redd\.it/",
    r"\.jpg$",
    r"\.jpeg$",
    r"\.png$",
    r"\.webp$",
    r"\.gif$",
]
_IMAGE_RE = re.compile("|".join(_IMAGE_PATTERNS), re.IGNORECASE)

# Fields that can be enriched from vision results
_ENRICHABLE_FIELDS = [
    "brand", "product_name", "category",
    "old_size", "old_size_unit", "new_size", "new_size_unit",
    "old_price", "new_price", "retailer", "upc",
    "observed_date", "change_description",
]


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Vision extraction for image posts (adjustable confidence targeting)"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max items to process (0 = all)",
    )
    parser.add_argument(
        "--confidence-min", type=float, default=0.0,
        help="Lower bound of confidence range to target (default: 0.0)",
    )
    parser.add_argument(
        "--confidence-max", type=float, default=1.0,
        help="Upper bound of confidence range to target (default: 1.0)",
    )
    parser.add_argument(
        "--status", type=str, default=None,
        help="Only process claims with this status (default: all non-discarded)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=20,
        help="Items per processing batch (smaller due to vision cost)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be extracted without writing",
    )
    args = parser.parse_args()

    log.info(
        "Starting vision enrichment (conf=%.2f-%.2f, status=%s, limit=%s, dry_run=%s)",
        args.confidence_min, args.confidence_max,
        args.status or "all",
        args.limit or "all", args.dry_run,
    )

    # Step 1: Find candidates
    candidates = _find_vision_candidates(
        confidence_min=args.confidence_min,
        confidence_max=args.confidence_max,
        status_filter=args.status,
        limit=args.limit,
    )
    log.info("Found %d vision candidates", len(candidates))

    if not candidates:
        log.info("No candidates for vision extraction. Done.")
        return

    # Step 2: Process with vision (enrich only — no duplicate claims)
    total_enriched = 0
    total_no_image = 0
    total_failed = 0
    total_skipped = 0
    start_time = time.time()

    for i in range(0, len(candidates), args.batch_size):
        batch = candidates[i:i + args.batch_size]
        batch_num = i // args.batch_size + 1
        log.info("Processing batch %d (%d items)", batch_num, len(batch))

        for item in batch:
            raw_payload = item.get("raw_payload", {})
            image_url = _extract_image_url(raw_payload)

            if not image_url:
                total_no_image += 1
                continue

            result = _extract_with_vision(raw_payload, image_url)

            if result is None:
                total_failed += 1
                continue

            old_conf = item.get("text_confidence", 0)
            new_conf = result["confidence"]["overall"]

            if args.dry_run:
                null_fields = _get_null_fields(item)
                fillable = {k: v for k, v in result.items()
                            if k in _ENRICHABLE_FIELDS and k in null_fields and v is not None}
                log.info(
                    "[DRY RUN] %s | %s | conf %.2f->%.2f | %s",
                    result.get("brand") or "?",
                    result.get("product_name") or "?",
                    old_conf, new_conf,
                    result.get("change_description", "")[:80],
                )
                if fillable:
                    log.info("  Would fill: %s", list(fillable.keys()))
                    total_enriched += 1
                else:
                    log.info("  No NULL fields to fill — skipping")
                    total_skipped += 1
            else:
                enriched = _enrich_existing_claim(item, result)
                if enriched:
                    total_enriched += 1
                else:
                    total_skipped += 1

        # Progress log
        processed = min(i + args.batch_size, len(candidates))
        elapsed = time.time() - start_time
        rate = processed / elapsed if elapsed > 0 else 0
        log.info(
            "Progress: %d/%d (enriched=%d, no_image=%d, failed=%d, skipped=%d, rate=%.1f/s)",
            processed, len(candidates),
            total_enriched, total_no_image, total_failed, total_skipped, rate,
        )

    elapsed = time.time() - start_time
    log.info(
        "Done: enriched=%d, no_image=%d, failed=%d, skipped=%d, elapsed=%.0fs",
        total_enriched, total_no_image, total_failed, total_skipped, elapsed,
    )


def _find_vision_candidates(confidence_min, confidence_max, status_filter, limit):
    # type: (float, float, Optional[str], int) -> List[Dict[str, Any]]
    """Find Reddit claims within the specified confidence range that have images.

    Returns claim + raw_item data joined together.
    Uses batched raw_item lookups to avoid N+1 query pattern and HTTP/2
    connection exhaustion.
    """
    client = get_client()
    candidates = []  # type: List[Dict[str, Any]]
    offset = 0

    while True:
        # Build query for claims in the confidence range
        query = (
            client.table("claims")
            .select("id,raw_item_id,confidence,status,brand,product_name,category,"
                    "old_size,old_size_unit,new_size,new_size_unit,old_price,new_price,"
                    "retailer,upc,observed_date,change_description")
            .eq("extractor_version", TEXT_EXTRACTOR)
            .gte("confidence->>overall", str(confidence_min))
        )

        # Upper bound: use lte for max=1.0 (include perfect scores), lt otherwise
        if confidence_max >= 1.0:
            query = query.lte("confidence->>overall", str(confidence_max))
        else:
            query = query.lt("confidence->>overall", str(confidence_max))

        # Status filter
        if status_filter:
            query = query.eq("status", status_filter)
        else:
            query = query.neq("status", "discarded")

        resp = (
            query
            .order("extracted_at", desc=False)
            .range(offset, offset + POSTGREST_PAGE_SIZE - 1)
            .execute()
        )

        if not resp.data:
            break

        # Batch-fetch raw_items for this page of claims (groups of 40 to
        # avoid PostgREST URL-length limits with UUIDs)
        raw_item_ids = list({c["raw_item_id"] for c in resp.data})
        raw_items_map = {}  # type: Dict[str, Dict[str, Any]]
        batch_sz = 40
        for bi in range(0, len(raw_item_ids), batch_sz):
            batch_ids = raw_item_ids[bi:bi + batch_sz]
            raw_resp = (
                client.table("raw_items")
                .select("id,source_type,raw_payload")
                .in_("id", batch_ids)
                .eq("source_type", "reddit")
                .execute()
            )
            for ri in raw_resp.data:
                raw_items_map[ri["id"]] = ri

        for claim in resp.data:
            raw_item = raw_items_map.get(claim["raw_item_id"])
            if not raw_item:
                continue

            text_conf = 0.0
            try:
                text_conf = float(claim.get("confidence", {}).get("overall", 0))
            except (TypeError, ValueError):
                pass

            candidates.append({
                "claim_id": claim["id"],
                "raw_item_id": claim["raw_item_id"],
                "raw_payload": raw_item["raw_payload"],
                "text_confidence": text_conf,
                "existing_claim": claim,
            })

            if limit and len(candidates) >= limit:
                return candidates

        log.info("Candidate scan progress: %d found so far (page offset=%d)", len(candidates), offset)

        if len(resp.data) < POSTGREST_PAGE_SIZE:
            break
        offset += POSTGREST_PAGE_SIZE

        # Recycle HTTP/2 connection every 5000 claims to prevent termination
        if offset % 5000 == 0:
            client = get_client()

    return candidates



def _extract_image_url(raw_payload):
    # type: (Dict[str, Any]) -> Optional[str]
    """Extract an image URL from a Reddit post payload.

    Checks multiple possible fields where Reddit stores image URLs.
    """
    # Direct URL field (for link posts)
    url = raw_payload.get("url", "")
    if url and _IMAGE_RE.search(url):
        return url

    # Gallery images (Reddit image gallery posts)
    media_metadata = raw_payload.get("media_metadata", {})
    if isinstance(media_metadata, dict):
        for media_id, meta in media_metadata.items():
            if isinstance(meta, dict):
                source = meta.get("s", {})
                if isinstance(source, dict):
                    img_url = source.get("u", "")
                    if img_url:
                        # Reddit encodes ampersands in gallery URLs
                        return img_url.replace("&amp;", "&")

    # Preview images
    preview = raw_payload.get("preview", {})
    if isinstance(preview, dict):
        images = preview.get("images", [])
        if images and isinstance(images, list):
            first = images[0]
            if isinstance(first, dict):
                source = first.get("source", {})
                if isinstance(source, dict):
                    img_url = source.get("url", "")
                    if img_url:
                        return img_url.replace("&amp;", "&")

    # Thumbnail (last resort)
    thumbnail = raw_payload.get("thumbnail", "")
    if thumbnail and thumbnail.startswith("http") and _IMAGE_RE.search(thumbnail):
        return thumbnail

    return None


def _extract_with_vision(raw_payload, image_url):
    # type: (Dict[str, Any], str) -> Optional[Dict[str, Any]]
    """Run vision extraction on a Reddit post + image."""
    text_content = build_reddit_vision_message(
        title=raw_payload.get("title", ""),
        selftext=raw_payload.get("selftext", ""),
        score=int(raw_payload.get("score", 0)),
        created_utc=float(raw_payload.get("created_utc", 0)),
    )

    response = extract_claim_vision(
        system_prompt=SYSTEM_PROMPT_VISION,
        text_content=text_content,
        image_url=image_url,
    )

    if response is None:
        return None

    return parse_claim_response(response)


def _get_null_fields(item):
    # type: (Dict[str, Any]) -> Set[str]
    """Get the set of enrichable fields that are NULL on the existing claim."""
    claim = item.get("existing_claim", {})
    null_fields = set()  # type: Set[str]
    for field in _ENRICHABLE_FIELDS:
        if claim.get(field) is None:
            null_fields.add(field)
    return null_fields


def _enrich_existing_claim(item, vision_result):
    # type: (Dict[str, Any], Dict[str, Any]) -> bool
    """Update existing text claim's NULL fields with vision data.

    Returns True if any fields were enriched.
    """
    null_fields = _get_null_fields(item)
    if not null_fields:
        log.debug("No NULL fields to enrich for %s", item.get("claim_id", "?"))
        return False

    # Build update dict: only fill in fields that are NULL and vision has a value
    updates = {}  # type: Dict[str, Any]
    for field in null_fields:
        vision_val = vision_result.get(field)
        if vision_val is not None:
            updates[field] = vision_val

    if not updates:
        log.debug("Vision didn't provide new data for NULL fields of %s", item.get("claim_id", "?"))
        return False

    client = get_client()
    try:
        (
            client.table("claims")
            .update(updates)
            .eq("id", item["claim_id"])
            .execute()
        )
        log.info(
            "Enriched claim %s with vision data: %s",
            item["claim_id"][:8], list(updates.keys()),
        )
        return True
    except Exception as exc:
        log.error(
            "Failed to enrich claim %s: %s",
            item["claim_id"][:8], str(exc)[:200],
        )
        return False



if __name__ == "__main__":
    main()
