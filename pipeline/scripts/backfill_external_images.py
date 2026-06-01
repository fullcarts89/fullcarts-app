#!/usr/bin/env python3
"""Backfill external news/GDELT hero images into our own storage.

Reddit side-by-side photos are already archived into the `claim-images`
bucket (see backfill_claim_images.py). News/GDELT events instead carry only
a LIVE link to the publisher's own image (raw_payload.socialimage), which we
never copied. Those links rot: publishers delete or replace the image, and
the page then shows a 404 or a "Media Removed" tombstone (e.g. InsideEdition).

This script copies the *still-good, product-specific* external hero images
into our bucket and sets claims.image_storage_path, so the frontend (which
already prefers claim_image_path) renders our permanent copy instead of the
rotting external URL. Pairs with the frontend change that stops trusting
un-archived external images as the lead photo.

Selection (mirrors web leadImageFromSources): only events whose lead image is
currently an external socialimage with no archived copy are considered.

Quality filters (skip, do NOT archive):
  * dead       — download fails / non-200 / non-image / < 3KB
  * og-image   — URL is a social-share fallback (`og-image` / `type=og`)
  * generic    — same image bytes reused across >= 2 DIFFERENT brands
                 (publisher stock / "image not available" placeholder).
                 Single-brand reuse is kept (legit syndication).

Examples:
    # Dry run — full classification report, writes nothing
    python -m pipeline.scripts.backfill_external_images --dry-run

    # Archive the keepers
    python -m pipeline.scripts.backfill_external_images
"""
import argparse
import collections
import concurrent.futures
import hashlib
import time
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

from pipeline.lib.image_archiver import (
    STORAGE_BUCKET,
    download_image,
    resize_to_webp,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client

log = get_logger("backfill_external_images")

PAGE_SIZE = 1000
DOWNLOAD_WORKERS = 24
MIN_BYTES = 3000

# Hosts whose images next/image already optimizes — these are retailer / OFF /
# Reddit images, not the rot-prone news long tail. If an event's lead is one of
# these we leave it alone (it's either already archived or low-risk).
WHITELISTED_HOSTS = {
    "i.redd.it",
    "i.imgur.com",
    "preview.redd.it",
    "external-preview.redd.it",
    "b.thumbs.redditmedia.com",
    "images.openfoodfacts.org",
    "images.openfoodfacts.net",
    "static.openfoodfacts.org",
    "i5.walmartimages.com",
    "i6.walmartimages.com",
    "www.kroger.com",
    "pics.kroger.com",
    "ntyhbapphnzlariakgrw.supabase.co",
}


def is_og_fallback(url):
    # type: (str) -> bool
    u = url.lower()
    return "og-image" in u or "type=og" in u


def host_of(url):
    # type: (str) -> str
    try:
        return urlparse(url).hostname or ""
    except Exception:
        return ""


def fetch_lead_external_candidates():
    # type: () -> List[Dict[str, Any]]
    """Walk event_evidence_summary and return one candidate per event whose
    lead image is an un-archived external socialimage.

    Each candidate: {event_id, claim_id, url, brand}. The claim_id is the
    source that owns the socialimage — the file is stored as {claim_id}.webp
    and claims.image_storage_path is updated on it.
    """
    client = get_client()
    candidates = []  # type: List[Dict[str, Any]]
    offset = 0
    while True:
        resp = (
            client.table("event_evidence_summary")
            .select("event_id,brand,sources")
            .order("event_id")
            .range(offset, offset + PAGE_SIZE - 1)
            .execute()
        )
        rows = resp.data or []
        for row in rows:
            sources = row.get("sources") or []
            # Already archived somewhere in the evidence → frontend shows that.
            if any(s.get("claim_image_path") for s in sources):
                continue
            # First source with an external socialimage becomes the lead.
            lead = None
            for s in sources:
                img = s.get("image")
                if img and host_of(img) not in WHITELISTED_HOSTS:
                    lead = s
                    break
            if not lead:
                continue
            candidates.append({
                "event_id": row["event_id"],
                "claim_id": lead.get("claim_id"),
                "url": lead.get("image"),
                "brand": (row.get("brand") or "").strip().lower(),
            })
        if len(rows) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return candidates


def probe(cand):
    # type: (Dict[str, Any]) -> Dict[str, Any]
    """Download + hash a candidate's image. Adds status/size/hash/raw."""
    out = dict(cand)
    raw = download_image(cand["url"])
    if raw is None:
        out["ok"] = False
        out["raw"] = None
        out["hash"] = None
        return out
    out["ok"] = True
    out["raw"] = raw
    out["hash"] = hashlib.md5(raw).hexdigest()
    out["size"] = len(raw)
    return out


def classify(probed):
    # type: (List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]
    """Bucket probed candidates into keep / dead / og / tiny / generic."""
    dead, og, tiny, alive = [], [], [], []
    for p in probed:
        if not p["ok"]:
            dead.append(p)
        elif is_og_fallback(p["url"]):
            og.append(p)
        elif p.get("size", 0) < MIN_BYTES:
            tiny.append(p)
        else:
            alive.append(p)

    # Generic = identical bytes across >= 2 different brands.
    brands_by_hash = collections.defaultdict(set)  # type: Dict[str, Set[str]]
    for p in alive:
        brands_by_hash[p["hash"]].add(p["brand"])
    generic, keep = [], []
    for p in alive:
        if len(brands_by_hash[p["hash"]]) >= 2:
            generic.append(p)
        else:
            keep.append(p)
    return {"keep": keep, "dead": dead, "og": og, "tiny": tiny, "generic": generic}


def upload_and_link(claim_id, webp_bytes):
    # type: (str, bytes) -> bool
    client = get_client()
    path = "{}.webp".format(claim_id)
    try:
        client.storage.from_(STORAGE_BUCKET).upload(
            path=path,
            file=webp_bytes,
            file_options={"content-type": "image/webp", "upsert": "true"},
        )
    except Exception as exc:
        log.error("Upload failed for %s: %s", claim_id[:8], str(exc)[:200])
        return False
    try:
        client.table("claims").update(
            {"image_storage_path": path}
        ).eq("id", claim_id).execute()
        return True
    except Exception as exc:
        log.error("Claim update failed for %s: %s", claim_id[:8], str(exc)[:200])
        return False


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Archive still-good external hero images into our storage"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Classify and report; write nothing")
    parser.add_argument("--limit", type=int, default=0,
                        help="Cap candidates probed (0 = all)")
    args = parser.parse_args()

    log.info("Collecting events whose lead image is an un-archived external URL")
    candidates = fetch_lead_external_candidates()
    candidates = [c for c in candidates if c.get("claim_id") and c.get("url")]
    if args.limit:
        candidates = candidates[:args.limit]
    log.info("Found %d external-lead candidates", len(candidates))
    if not candidates:
        return

    log.info("Downloading + hashing (%d workers)...", DOWNLOAD_WORKERS)
    probed = []  # type: List[Dict[str, Any]]
    with concurrent.futures.ThreadPoolExecutor(max_workers=DOWNLOAD_WORKERS) as ex:
        for p in ex.map(probe, candidates):
            probed.append(p)

    buckets = classify(probed)
    log.info(
        "Classification: keep=%d  dead=%d  og-image=%d  tiny=%d  generic=%d",
        len(buckets["keep"]), len(buckets["dead"]), len(buckets["og"]),
        len(buckets["tiny"]), len(buckets["generic"]),
    )

    if args.dry_run:
        log.info("[DRY RUN] would archive %d images. Sample keepers:",
                 len(buckets["keep"]))
        for p in buckets["keep"][:15]:
            log.info("  keep  brand=%-18s %s", p["brand"][:18], p["url"][:70])
        return

    keep = buckets["keep"]
    stats = {"archived": 0, "convert_fail": 0, "upload_fail": 0}
    start = time.time()
    for i, p in enumerate(keep):
        webp = resize_to_webp(p["raw"])
        if webp is None:
            stats["convert_fail"] += 1
            continue
        if upload_and_link(p["claim_id"], webp):
            stats["archived"] += 1
        else:
            stats["upload_fail"] += 1
        if (i + 1) % 25 == 0:
            log.info("Progress %d/%d  archived=%d", i + 1, len(keep),
                     stats["archived"])
            reset_client()
    log.info(
        "Done: archived=%d  convert_fail=%d  upload_fail=%d  elapsed=%.0fs",
        stats["archived"], stats["convert_fail"], stats["upload_fail"],
        time.time() - start,
    )


if __name__ == "__main__":
    main()
