#!/usr/bin/env python3
"""Backfill claim images: download, resize to WebP, upload to Supabase Storage.

Downloads original images from Reddit (i.redd.it, imgur, etc.), resizes to
max 1200px, converts to WebP (~100-200KB each), and uploads to the
'claim-images' bucket. Falls back to Wayback Machine for dead URLs.

Prioritizes approved + pending claims over discarded.

Examples:
    # Dry run — see what would be processed
    python -m pipeline.scripts.backfill_claim_images --dry-run --limit 20

    # Process approved claims first
    python -m pipeline.scripts.backfill_claim_images --status approved

    # Process everything (approved + pending, skip discarded)
    python -m pipeline.scripts.backfill_claim_images

    # Resume after interruption (skips claims that already have image_storage_path)
    python -m pipeline.scripts.backfill_claim_images
"""
import argparse
import time
from typing import Any, Dict, List, Optional

import requests as http_requests

from pipeline.lib.image_archiver import (
    STORAGE_BUCKET,
    download_image,
    extract_image_url,
    resize_to_webp,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client

log = get_logger("backfill_claim_images")

POSTGREST_PAGE_SIZE = 500
WAYBACK_TIMEOUT = 10


def try_wayback(original_url):
    # type: (str) -> Optional[bytes]
    """Try to fetch an archived version of the image from Wayback Machine."""
    wayback_url = "https://web.archive.org/web/2024/" + original_url
    try:
        resp = http_requests.get(wayback_url, timeout=WAYBACK_TIMEOUT, headers={
            "User-Agent": "FullCarts/1.0 (evidence archival)"
        })
        if resp.status_code == 200 and len(resp.content) > 1000:
            content_type = resp.headers.get("content-type", "")
            if "image" in content_type or "octet" in content_type:
                return resp.content
        return None
    except Exception:
        return None


def upload_to_storage(claim_id, webp_bytes):
    # type: (str, bytes) -> Optional[str]
    """Upload WebP image to Supabase Storage. Returns storage path or None."""
    storage_path = "{}.webp".format(claim_id)
    client = get_client()

    try:
        client.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=webp_bytes,
            file_options={"content-type": "image/webp", "upsert": "true"},
        )
        return storage_path
    except Exception as exc:
        log.error("Upload failed for %s: %s", claim_id[:8], str(exc)[:200])
        return None


def update_claim_path(claim_id, storage_path):
    # type: (str, str) -> bool
    """Set image_storage_path on the claim."""
    client = get_client()
    try:
        client.table("claims").update(
            {"image_storage_path": storage_path}
        ).eq("id", claim_id).execute()
        return True
    except Exception as exc:
        log.error("Failed to update claim %s: %s", claim_id[:8], str(exc)[:200])
        return False


def fetch_candidates(status_filter, limit):
    # type: (Optional[str], int) -> List[Dict[str, Any]]
    """Fetch claims that need image backfill (no image_storage_path yet)."""
    client = get_client()
    candidates = []  # type: List[Dict[str, Any]]

    # Process approved first, then pending
    statuses = [status_filter] if status_filter else ["approved", "pending"]

    for status in statuses:
        offset = 0
        while True:
            query = (
                client.table("claims")
                .select("id,raw_item_id,status")
                .eq("status", status)
                .is_("image_storage_path", "null")
                .order("id")
                .range(offset, offset + POSTGREST_PAGE_SIZE - 1)
            )
            resp = query.execute()

            if not resp.data:
                break

            # Batch-fetch raw_items
            raw_ids = list({c["raw_item_id"] for c in resp.data})
            raw_map = {}  # type: Dict[str, Dict[str, Any]]
            for bi in range(0, len(raw_ids), 40):
                batch_ids = raw_ids[bi:bi + 40]
                raw_resp = (
                    client.table("raw_items")
                    .select("id,source_type,raw_payload")
                    .in_("id", batch_ids)
                    .execute()
                )
                for ri in raw_resp.data:
                    raw_map[ri["id"]] = ri

            for claim in resp.data:
                raw = raw_map.get(claim["raw_item_id"])
                if not raw:
                    continue
                image_url = extract_image_url(raw.get("raw_payload", {}))
                if not image_url:
                    continue
                candidates.append({
                    "claim_id": claim["id"],
                    "status": claim["status"],
                    "image_url": image_url,
                    "source_type": raw.get("source_type", ""),
                })

                if limit and len(candidates) >= limit:
                    return candidates

            if len(resp.data) < POSTGREST_PAGE_SIZE:
                break
            offset += POSTGREST_PAGE_SIZE

            # Recycle connection periodically
            if offset % 3000 == 0:
                reset_client()

    return candidates


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(description="Backfill claim images to Supabase Storage")
    parser.add_argument("--limit", type=int, default=0, help="Max claims to process (0=all)")
    parser.add_argument("--status", type=str, default=None, help="Only process this status")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    parser.add_argument("--no-wayback", action="store_true", help="Skip Wayback Machine fallback")
    args = parser.parse_args()

    log.info("Starting image backfill (status=%s, limit=%s, dry_run=%s)",
             args.status or "approved+pending", args.limit or "all", args.dry_run)

    candidates = fetch_candidates(args.status, args.limit)
    log.info("Found %d claims with image URLs needing backfill", len(candidates))

    if not candidates:
        log.info("Nothing to backfill. Done.")
        return

    stats = {"downloaded": 0, "wayback": 0, "dead": 0, "upload_fail": 0}
    start = time.time()

    for i, cand in enumerate(candidates):
        claim_id = cand["claim_id"]
        image_url = cand["image_url"]

        if args.dry_run:
            log.info("[DRY RUN] %d/%d claim=%s url=%s",
                     i + 1, len(candidates), claim_id[:8], image_url[:80])
            continue

        # Try direct download
        raw_bytes = download_image(image_url)
        source = "direct"

        # Wayback fallback
        if raw_bytes is None and not args.no_wayback:
            raw_bytes = try_wayback(image_url)
            if raw_bytes:
                source = "wayback"
                stats["wayback"] += 1

        if raw_bytes is None:
            stats["dead"] += 1
            if (i + 1) % 50 == 0:
                log.info("Progress: %d/%d (ok=%d, wayback=%d, dead=%d)",
                         i + 1, len(candidates), stats["downloaded"],
                         stats["wayback"], stats["dead"])
            continue

        # Resize + convert to WebP
        webp_bytes = resize_to_webp(raw_bytes)
        if webp_bytes is None:
            stats["dead"] += 1
            continue

        # Upload
        storage_path = upload_to_storage(claim_id, webp_bytes)
        if storage_path is None:
            stats["upload_fail"] += 1
            continue

        # Update claim
        if update_claim_path(claim_id, storage_path):
            stats["downloaded"] += 1
        else:
            stats["upload_fail"] += 1

        # Progress logging
        if (i + 1) % 50 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            log.info(
                "Progress: %d/%d (ok=%d, wayback=%d, dead=%d, fail=%d, %.1f/s)",
                i + 1, len(candidates), stats["downloaded"],
                stats["wayback"], stats["dead"], stats["upload_fail"], rate,
            )

        # Recycle connection every 500 uploads
        if stats["downloaded"] % 500 == 0 and stats["downloaded"] > 0:
            reset_client()

        # Small delay to be polite to Reddit/Wayback CDN
        time.sleep(0.2)

    elapsed = time.time() - start
    log.info(
        "Done: downloaded=%d, wayback=%d, dead=%d, upload_fail=%d, elapsed=%.0fs",
        stats["downloaded"], stats["wayback"], stats["dead"],
        stats["upload_fail"], elapsed,
    )


if __name__ == "__main__":
    main()
