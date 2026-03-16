#!/usr/bin/env python3
"""Extract structured shrinkflation claims from raw_items using Claude Haiku.

Reads Reddit posts and news articles from raw_items that don't yet have
a corresponding claim row, calls Claude Haiku for structured extraction,
and writes the results to the claims table.

Usage:
    python -m pipeline.scripts.extract_claims [OPTIONS]

Options:
    --limit N          Process at most N items (default: all)
    --source-type TYPE Only process 'reddit' or 'news' (default: both)
    --batch-size N     Items per batch (default: 50)
    --dry-run          Print what would be extracted without writing
    --extractor VER    Extractor version string (default: haiku-v1)
"""
import argparse
import sys
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from pipeline.lib.claude_client import CreditExhaustedError, extract_claim_text
from pipeline.lib.extraction_prompt import (
    SYSTEM_PROMPT_TEXT,
    build_news_text_message,
    build_reddit_text_message,
    parse_claim_response,
)
from pipeline.lib.image_archiver import archive_claim_image
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client

log = get_logger("extract_claims")

DEFAULT_EXTRACTOR = "haiku-v1"
POSTG_REST_PAGE_SIZE = 1000  # Supabase PostgREST max rows per request


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Extract claims from raw_items using Claude Haiku"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max items to process (0 = all)",
    )
    parser.add_argument(
        "--source-type", type=str, default=None,
        choices=["reddit", "news", "gdelt"],
        help="Only process this source type (default: both)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Items per processing batch",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be extracted without writing",
    )
    parser.add_argument(
        "--extractor", type=str, default=DEFAULT_EXTRACTOR,
        help="Extractor version string",
    )
    args = parser.parse_args()

    log.info(
        "Starting extraction (limit=%s, source=%s, dry_run=%s, extractor=%s)",
        args.limit or "all",
        args.source_type or "reddit+news",
        args.dry_run,
        args.extractor,
    )

    # Step 1: Find raw_items that haven't been processed yet
    unprocessed = _find_unprocessed_items(
        extractor_version=args.extractor,
        source_type=args.source_type,
        limit=args.limit,
    )
    log.info("Found %d unprocessed items", len(unprocessed))

    if not unprocessed:
        log.info("Nothing to process. Done.")
        return

    # Step 2: Process in batches
    total_extracted = 0
    total_discarded = 0
    total_failed = 0
    start_time = time.time()

    for i in range(0, len(unprocessed), args.batch_size):
        batch = unprocessed[i:i + args.batch_size]
        batch_num = i // args.batch_size + 1
        log.info(
            "Processing batch %d (%d items, %d/%d total)",
            batch_num, len(batch), i + len(batch), len(unprocessed),
        )

        for item in batch:
            try:
                results = _extract_single_item(item, args.extractor)
            except CreditExhaustedError:
                log.error("Anthropic credits exhausted. Stopping extraction.")
                sys.exit(1)

            if results is None:
                total_failed += 1
                continue

            for claim_index, result in enumerate(results):
                if result["confidence"]["overall"] == 0:
                    total_discarded += 1
                    status = "discarded"
                else:
                    total_extracted += 1
                    status = "pending"

                if args.dry_run:
                    log.info(
                        "[DRY RUN] %s | %s | %s | conf=%.2f | %s",
                        item.get("source_type"),
                        result.get("brand") or "?",
                        result.get("product_name") or "?",
                        result["confidence"]["overall"],
                        result.get("change_description", "")[:60],
                    )
                else:
                    _write_claim(item, result, args.extractor, status, claim_index)

        elapsed = time.time() - start_time
        rate = (total_extracted + total_discarded + total_failed) / max(elapsed, 1)
        log.info(
            "Progress: extracted=%d, discarded=%d, failed=%d, "
            "rate=%.1f items/sec, elapsed=%.0fs",
            total_extracted, total_discarded, total_failed, rate, elapsed,
        )

    elapsed = time.time() - start_time
    log.info(
        "Done: extracted=%d, discarded=%d, failed=%d, elapsed=%.0fs",
        total_extracted, total_discarded, total_failed, elapsed,
    )


def _find_unprocessed_items(
    extractor_version,  # type: str
    source_type,  # type: Optional[str]
    limit,  # type: int
):
    # type: (...) -> List[Dict[str, Any]]
    """Find raw_items that don't have a claim for this extractor version.

    Uses a two-step approach since PostgREST can't do LEFT JOIN anti-joins:
    1. Get all raw_item_ids already in claims for this extractor_version
    2. Get raw_items excluding those IDs
    """
    client = get_client()

    # Step 1: Get already-processed raw_item_ids
    log.info("Fetching already-processed item IDs for extractor=%s...", extractor_version)
    processed_ids = _get_processed_ids(client, extractor_version)
    log.info("Found %d already-processed items", len(processed_ids))

    # Step 2: Fetch unprocessed raw_items
    source_types = [source_type] if source_type else ["reddit", "news", "gdelt"]
    all_items = []  # type: List[Dict[str, Any]]

    for st in source_types:
        items = _fetch_raw_items(client, st, processed_ids, limit)
        all_items.extend(items)
        log.info("Found %d unprocessed %s items", len(items), st)

        if limit and len(all_items) >= limit:
            all_items = all_items[:limit]
            break

    return all_items


def _get_processed_ids(client, extractor_version):
    # type: (Any, str) -> Set[str]
    """Get all raw_item_ids that already have claims for this extractor."""
    processed = set()  # type: Set[str]
    offset = 0

    while True:
        resp = (
            client.table("claims")
            .select("raw_item_id")
            .eq("extractor_version", extractor_version)
            .range(offset, offset + POSTG_REST_PAGE_SIZE - 1)
            .execute()
        )
        if not resp.data:
            break

        for row in resp.data:
            processed.add(row["raw_item_id"])

        if len(resp.data) < POSTG_REST_PAGE_SIZE:
            break
        offset += POSTG_REST_PAGE_SIZE

    return processed


def _fetch_raw_items(client, source_type, exclude_ids, limit):
    # type: (Any, str, Set[str], int) -> List[Dict[str, Any]]
    """Fetch raw_items for a source type, excluding already-processed IDs.

    Since PostgREST can't filter by 'NOT IN (large set)', we fetch
    pages and filter client-side. For 16.5K Reddit items with ~0
    processed initially, this is fine.
    """
    items = []  # type: List[Dict[str, Any]]
    offset = 0
    target = limit if limit else float("inf")

    while len(items) < target:
        resp = (
            client.table("raw_items")
            .select("id,source_type,source_id,source_url,source_date,raw_payload")
            .eq("source_type", source_type)
            .order("captured_at", desc=False)
            .range(offset, offset + POSTG_REST_PAGE_SIZE - 1)
            .execute()
        )

        if not resp.data:
            break

        for row in resp.data:
            if row["id"] not in exclude_ids:
                items.append(row)
                if limit and len(items) >= limit:
                    return items

        if len(resp.data) < POSTG_REST_PAGE_SIZE:
            break
        offset += POSTG_REST_PAGE_SIZE

        # Reset client periodically for long-running fetches
        if offset > 0 and offset % (POSTG_REST_PAGE_SIZE * 20) == 0:
            reset_client()
            client = get_client()

    return items


def _extract_single_item(item, extractor_version):
    # type: (Dict[str, Any], str) -> Optional[List[Dict[str, Any]]]
    """Extract claims from a single raw_item using Claude Haiku.

    Returns a list of parsed + validated claim dicts, or None on API failure.
    For Reddit posts, typically returns a single-element list.
    For news articles, may return multiple claims if the article mentions
    multiple products.
    """
    source_type = item["source_type"]
    payload = item.get("raw_payload", {})

    if source_type == "reddit":
        user_message = build_reddit_text_message(
            title=payload.get("title", ""),
            selftext=payload.get("selftext", ""),
            score=int(payload.get("score", 0)),
            created_utc=float(payload.get("created_utc", 0)),
        )
    elif source_type in ("news", "gdelt"):
        user_message = build_news_text_message(
            title=payload.get("title", ""),
            description=payload.get("description", payload.get("summary", "")),
            published=payload.get("published", payload.get("pubdate",
                      payload.get("pub_date", payload.get("seendate", "")))),
            body=payload.get("article_body", payload.get("body")),
            source_name=payload.get("source_name", payload.get("domain", "")),
        )
    else:
        log.warning("Unknown source_type: %s", source_type)
        return None

    max_tokens = 1024
    if source_type in ("news", "gdelt"):
        max_tokens = 2048  # More room for multi-claim responses

    response = extract_claim_text(
        system_prompt=SYSTEM_PROMPT_TEXT,
        user_message=user_message,
        max_tokens=max_tokens,
    )

    if response is None:
        log.warning(
            "API failure for %s/%s",
            source_type, item.get("source_id", "?"),
        )
        return None

    # Handle array responses (multi-claim) and single object responses
    if isinstance(response, list):
        return [parse_claim_response(r) for r in response]
    else:
        return [parse_claim_response(response)]


def _write_claim(item, claim_data, extractor_version, status, claim_index=0):
    # type: (Dict[str, Any], Dict[str, Any], str, str, int) -> None
    """Write an extracted claim to the claims table."""
    client = get_client()

    row = {
        "raw_item_id": item["id"],
        "extractor_version": extractor_version,
        "claim_index": claim_index,
        "extracted_at": datetime.now(timezone.utc).isoformat(),
        "brand": claim_data.get("brand"),
        "product_name": claim_data.get("product_name"),
        "category": claim_data.get("category"),
        "old_size": claim_data.get("old_size"),
        "old_size_unit": claim_data.get("old_size_unit"),
        "new_size": claim_data.get("new_size"),
        "new_size_unit": claim_data.get("new_size_unit"),
        "old_price": claim_data.get("old_price"),
        "new_price": claim_data.get("new_price"),
        "retailer": claim_data.get("retailer"),
        "upc": claim_data.get("upc"),
        "observed_date": claim_data.get("observed_date"),
        "change_description": claim_data.get("change_description"),
        "confidence": claim_data.get("confidence", {}),
        "status": status,
    }

    try:
        resp = (
            client.table("claims")
            .upsert(row, on_conflict="raw_item_id,extractor_version,claim_index")
            .execute()
        )
        # Archive image (best-effort, non-blocking for extraction)
        if resp.data and item.get("source_type") == "reddit":
            claim_id = resp.data[0].get("id")
            if claim_id:
                storage_path = archive_claim_image(claim_id, item.get("raw_payload", {}))
                if storage_path:
                    client.table("claims").update(
                        {"image_storage_path": storage_path}
                    ).eq("id", claim_id).execute()
    except Exception as exc:
        log.error(
            "Failed to write claim for raw_item %s (index %d): %s",
            item["id"], claim_index, str(exc)[:200],
        )


if __name__ == "__main__":
    main()
