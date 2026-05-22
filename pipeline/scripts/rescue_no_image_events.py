#!/usr/bin/env python3
"""Image rescue for published_changes events that have no image on any source.

The daily image backfill (backfill_claim_images.py) only processes claims with
status pending/approved. Claims that already produced a published_change carry
status='matched' or 'evidence' and were never re-checked. That gap left 350
events without an image as of the 2026-05-22 audit.

This script targets the exact cohort: every non-retracted event whose every
source has no image (`claim.image_storage_path IS NULL` AND
`raw_items.raw_payload->>'socialimage' IS NULL`). For each backing claim,
attempts a tailored recovery strategy:

  * reddit          — extract_image_url() on raw_payload + Wayback fallback
  * gdelt           — refetch og:image from source_url (might have been added
                       since first scrape), Wayback fallback
  * news            — decode Google News RSS redirect to real URL, then
                       og:image fetch, then Wayback fallback
  * kroger_change   — UPC -> Kroger Products API -> image
  * usda_size_change— UPC -> Kroger / Walmart / OFF cascade

Recovered images land in the claim-images bucket and `claim.image_storage_path`
is set, exactly mirroring the existing pipeline. Non-Reddit sources also have
their `raw_items.raw_payload.socialimage` populated so event_evidence_summary
surfaces the image without a schema change.

Usage:
    # Dry run — show counts per source_type, no writes
    python -m pipeline.scripts.rescue_no_image_events --dry-run

    # Live run, all source types
    python -m pipeline.scripts.rescue_no_image_events

    # Limit to a single source_type for testing
    python -m pipeline.scripts.rescue_no_image_events --source-type reddit --limit 10

    # Skip Wayback fallback (faster, fewer hits)
    python -m pipeline.scripts.rescue_no_image_events --no-wayback
"""
from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import time
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import requests as http_requests

from pipeline.lib.image_archiver import (
    STORAGE_BUCKET,
    download_image,
    extract_image_url,
    resize_to_webp,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client

log = get_logger("rescue_no_image_events")

WAYBACK_TIMEOUT = 10
FETCH_TIMEOUT = 15
USER_AGENT = (
    "Mozilla/5.0 (compatible; FullCarts/1.0 evidence-archival; +https://fullcarts.org)"
)


# ---------------------------------------------------------------------------
# Helpers shared with backfill_claim_images.py — kept inline to avoid a third
# place that needs editing whenever upload semantics change.
# ---------------------------------------------------------------------------

def upload_to_storage(claim_id: str, webp_bytes: bytes) -> Optional[str]:
    storage_path = f"{claim_id}.webp"
    sb = get_client()
    try:
        sb.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=webp_bytes,
            file_options={"content-type": "image/webp", "upsert": "true"},
        )
        return storage_path
    except Exception as exc:
        log.error("Upload failed for %s: %s", claim_id[:8], str(exc)[:200])
        return None


def update_claim_path(claim_id: str, storage_path: str) -> bool:
    try:
        get_client().table("claims").update(
            {"image_storage_path": storage_path}
        ).eq("id", claim_id).execute()
        return True
    except Exception as exc:
        log.error("Failed to update claim %s: %s", claim_id[:8], str(exc)[:200])
        return False


def update_raw_socialimage(raw_item_id: str, image_url: str) -> bool:
    """Patch raw_items.raw_payload.socialimage so event_evidence_summary
    surfaces the recovered image without a schema change.

    We can't do an in-place JSONB merge through PostgREST, so we read-modify-
    write the whole raw_payload. Fine at our cardinality (<100 non-reddit
    rescue attempts).
    """
    sb = get_client()
    try:
        resp = (sb.table("raw_items")
                .select("id, raw_payload")
                .eq("id", raw_item_id)
                .limit(1)
                .execute())
        if not resp.data:
            return False
        payload = resp.data[0].get("raw_payload") or {}
        payload["socialimage"] = image_url
        (sb.table("raw_items")
         .update({"raw_payload": payload})
         .eq("id", raw_item_id)
         .execute())
        return True
    except Exception as exc:
        log.error("Failed to patch raw_items %s socialimage: %s",
                  raw_item_id[:8], str(exc)[:200])
        return False


def try_wayback(original_url: str) -> Optional[bytes]:
    """Wayback fallback — try a generic 2024 snapshot."""
    wayback_url = "https://web.archive.org/web/2024/" + original_url
    try:
        resp = http_requests.get(
            wayback_url, timeout=WAYBACK_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code == 200 and len(resp.content) > 1000:
            ctype = resp.headers.get("content-type", "")
            if "image" in ctype or "octet" in ctype:
                return resp.content
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Strategy: Reddit
# ---------------------------------------------------------------------------

def recover_reddit(claim: Dict[str, Any], raw: Dict[str, Any],
                   use_wayback: bool) -> Tuple[Optional[bytes], Optional[str], str]:
    """Returns (image_bytes, recovered_url, source_tag)."""
    payload = raw.get("raw_payload") or {}
    image_url = extract_image_url(payload)
    if not image_url:
        return None, None, "no_url_in_payload"

    raw_bytes = download_image(image_url)
    if raw_bytes:
        return raw_bytes, image_url, "direct"

    if use_wayback:
        raw_bytes = try_wayback(image_url)
        if raw_bytes:
            return raw_bytes, image_url, "wayback"

    return None, image_url, "dead_url"


# ---------------------------------------------------------------------------
# Strategy: news / gdelt — og:image scrape
# ---------------------------------------------------------------------------

_OG_IMAGE_RE = re.compile(
    r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)
_TWITTER_IMAGE_RE = re.compile(
    r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']',
    re.IGNORECASE,
)


def decode_google_news_redirect(url: str) -> Optional[str]:
    """Google News RSS articles wrap the real URL in a base64-ish payload after
    `/articles/`. The payload starts with `CBM...` for older formats (which we
    can parse from the base64 directly) or `AU_yqL...` for newer formats which
    require a Google API roundtrip. The `googlenewsdecoder` library handles
    both — same library already used by pipeline/scripts/fetch_article_text.py.
    """
    try:
        from googlenewsdecoder import gnewsdecoder
        result = gnewsdecoder(url, interval=0)
        if result.get("status") and result.get("decoded_url"):
            return result["decoded_url"]
    except Exception:
        pass
    return None


def scrape_og_image(article_url: str) -> Optional[str]:
    try:
        resp = http_requests.get(
            article_url, timeout=FETCH_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        if resp.status_code != 200:
            return None
        html = resp.text[:200_000]  # cap at 200KB
        m = _OG_IMAGE_RE.search(html)
        if m:
            return m.group(1)
        m = _TWITTER_IMAGE_RE.search(html)
        if m:
            return m.group(1)
    except Exception:
        return None
    return None


def recover_article(claim: Dict[str, Any], raw: Dict[str, Any],
                    use_wayback: bool) -> Tuple[Optional[bytes], Optional[str], str]:
    source_url = raw.get("source_url") or ""
    if not source_url:
        return None, None, "no_source_url"

    target_url = source_url
    if "news.google.com" in source_url:
        decoded = decode_google_news_redirect(source_url)
        if decoded:
            target_url = decoded
        else:
            return None, None, "google_news_decode_failed"

    image_url = scrape_og_image(target_url)
    if image_url:
        raw_bytes = download_image(image_url)
        if raw_bytes:
            return raw_bytes, image_url, "og_image_direct"
        if use_wayback:
            raw_bytes = try_wayback(image_url)
            if raw_bytes:
                return raw_bytes, image_url, "og_image_wayback"

    # Last resort: Wayback snapshot of the article page itself, then re-scrape
    if use_wayback:
        wb_article = "https://web.archive.org/web/2024/" + target_url
        wb_og = scrape_og_image(wb_article)
        if wb_og:
            raw_bytes = download_image(wb_og)
            if raw_bytes:
                return raw_bytes, wb_og, "wayback_article_og"

    return None, None, "no_og_image"


# ---------------------------------------------------------------------------
# Strategy: kroger_change / usda_size_change — UPC cascade
# ---------------------------------------------------------------------------

def _upc_for_claim(claim: Dict[str, Any]) -> Optional[str]:
    upc = claim.get("upc")
    if upc:
        return str(upc).strip()
    return None


def lookup_kroger_image(upc: str) -> Optional[str]:
    """Kroger Products API — requires KROGER_CLIENT_ID/SECRET. Returns image URL."""
    try:
        from pipeline.lib.kroger_auth import get_kroger_token
    except ImportError:
        return None
    try:
        token = get_kroger_token()
    except Exception:
        return None
    if not token:
        return None
    try:
        resp = http_requests.get(
            "https://api.kroger.com/v1/products",
            params={"filter.term": upc, "filter.limit": 1},
            headers={"Authorization": f"Bearer {token}",
                     "User-Agent": USER_AGENT},
            timeout=FETCH_TIMEOUT,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        for prod in data.get("data") or []:
            for img in prod.get("images") or []:
                # prefer "front" perspective and "xlarge" size
                if img.get("perspective") == "front":
                    for size in img.get("sizes") or []:
                        if size.get("size") in ("xlarge", "large", "medium"):
                            return size.get("url")
                # fallback any image
                for size in img.get("sizes") or []:
                    return size.get("url")
    except Exception:
        return None
    return None


def lookup_off_image(upc: str) -> Optional[str]:
    """Open Food Facts public API."""
    try:
        resp = http_requests.get(
            f"https://world.openfoodfacts.org/api/v2/product/{upc}.json",
            timeout=FETCH_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        prod = data.get("product") or {}
        for key in ("image_front_url", "image_url", "image_small_url"):
            if prod.get(key):
                return prod[key]
        # selected_images.front.display.<lang>
        sel = prod.get("selected_images", {}).get("front", {})
        display = sel.get("display") or {}
        for v in display.values():
            if isinstance(v, str) and v.startswith("http"):
                return v
    except Exception:
        return None
    return None


def recover_upc(claim: Dict[str, Any], raw: Dict[str, Any],
                use_wayback: bool) -> Tuple[Optional[bytes], Optional[str], str]:
    upc = _upc_for_claim(claim)
    if not upc:
        # Try variant table
        try:
            variant_id = claim.get("matched_variant_id")
            if variant_id:
                resp = (get_client().table("pack_variants")
                        .select("upc").eq("id", variant_id).limit(1).execute())
                if resp.data:
                    upc = (resp.data[0].get("upc") or "").strip() or None
        except Exception:
            upc = None
    if not upc:
        return None, None, "no_upc"

    for fn, tag in ((lookup_kroger_image, "kroger_api"),
                    (lookup_off_image, "off_api")):
        image_url = fn(upc)
        if image_url:
            raw_bytes = download_image(image_url)
            if raw_bytes:
                return raw_bytes, image_url, tag
            if use_wayback:
                raw_bytes = try_wayback(image_url)
                if raw_bytes:
                    return raw_bytes, image_url, tag + "_wayback"
    return None, None, "upc_no_hit"


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

STRATEGY = {
    "reddit": recover_reddit,
    "gdelt": recover_article,
    "news": recover_article,
    "kroger_change": recover_upc,
    "usda_size_change": recover_upc,
}


def fetch_no_image_candidate_claims(source_filter: Optional[str]
                                    ) -> List[Dict[str, Any]]:
    """Walk event_evidence_summary, return the claim rows backing every
    no-image event, joined with raw_items for the rescue strategies.

    Filters out claims that already have image_storage_path set (defensive —
    they shouldn't appear in no-image events, but if a parallel run beats us
    to it we skip them cleanly).
    """
    sb = get_client()
    PAGE = 1000
    all_events: List[Dict[str, Any]] = []
    offset = 0
    while True:
        resp = (sb.table("event_evidence_summary")
                  .select("event_id, entity_id, brand, product_name, sources")
                  .range(offset, offset + PAGE - 1).execute())
        rows = resp.data or []
        all_events.extend(rows)
        if len(rows) < PAGE:
            break
        offset += PAGE

    claim_ids: List[str] = []
    claim_to_event: Dict[str, str] = {}
    for ev in all_events:
        srcs = ev.get("sources") or []
        if not srcs:
            continue
        any_image = any((s.get("claim_image_path") or s.get("image"))
                        for s in srcs)
        if any_image:
            continue
        # Optional source-type filter
        if source_filter:
            types = {s.get("source_type") for s in srcs}
            if source_filter not in types:
                continue
        for s in srcs:
            cid = s.get("claim_id")
            if cid:
                claim_ids.append(cid)
                claim_to_event[cid] = ev["event_id"]

    if not claim_ids:
        return []

    # Batch-fetch the actual claim rows (we have status=matched/evidence
    # backing these events). 80 per .in_() to stay under URL length cap.
    claims: List[Dict[str, Any]] = []
    for i in range(0, len(claim_ids), 80):
        chunk = claim_ids[i : i + 80]
        resp = (sb.table("claims")
                  .select("id, raw_item_id, status, upc, matched_variant_id, "
                          "image_storage_path, brand, product_name, "
                          "old_size, new_size")
                  .in_("id", chunk)
                  .execute())
        for c in resp.data or []:
            if c.get("image_storage_path"):
                continue  # already has image (defensive)
            c["_event_id"] = claim_to_event.get(c["id"])
            claims.append(c)

    # Now batch-fetch raw_items so each claim has its raw_payload available
    raw_ids = list({c["raw_item_id"] for c in claims if c.get("raw_item_id")})
    raw_map: Dict[str, Dict[str, Any]] = {}
    for i in range(0, len(raw_ids), 80):
        chunk = raw_ids[i : i + 80]
        resp = (sb.table("raw_items")
                  .select("id, source_type, source_url, raw_payload")
                  .in_("id", chunk)
                  .execute())
        for ri in resp.data or []:
            raw_map[ri["id"]] = ri

    out = []
    for c in claims:
        raw = raw_map.get(c["raw_item_id"])
        if not raw:
            continue
        if source_filter and raw.get("source_type") != source_filter:
            continue
        c["_raw_item"] = raw
        out.append(c)
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dry-run", action="store_true",
                   help="Show counts per source_type, no writes")
    p.add_argument("--source-type", default=None,
                   choices=list(STRATEGY) + [None],
                   help="Restrict to one source_type")
    p.add_argument("--limit", type=int, default=0,
                   help="Max claims to process (0=all)")
    p.add_argument("--no-wayback", action="store_true",
                   help="Skip Wayback fallback")
    p.add_argument("--sleep", type=float, default=0.25,
                   help="Sleep seconds between claims to be polite to CDNs")
    args = p.parse_args()

    log.info("Loading no-image event candidates (source_filter=%s)...",
             args.source_type or "all")
    claims = fetch_no_image_candidate_claims(args.source_type)
    if args.limit and len(claims) > args.limit:
        claims = claims[: args.limit]

    by_type = defaultdict(int)
    for c in claims:
        by_type[c["_raw_item"].get("source_type") or "unknown"] += 1
    log.info("Loaded %d candidate claims backing no-image events.", len(claims))
    for st, n in sorted(by_type.items(), key=lambda kv: -kv[1]):
        log.info("    %s: %d", st, n)

    if args.dry_run:
        log.info("Dry run — exiting before any fetches.")
        return 0

    stats: Dict[str, Dict[str, int]] = defaultdict(
        lambda: defaultdict(int)
    )
    use_wayback = not args.no_wayback
    start = time.time()

    for i, claim in enumerate(claims):
        raw = claim["_raw_item"]
        source_type = raw.get("source_type") or "unknown"
        strategy = STRATEGY.get(source_type)
        if strategy is None:
            stats[source_type]["unhandled"] += 1
            continue

        stats[source_type]["attempted"] += 1

        try:
            image_bytes, image_url, tag = strategy(claim, raw, use_wayback)
        except Exception as exc:
            log.error("Strategy crash %s/%s: %s",
                      source_type, claim["id"][:8], str(exc)[:200])
            stats[source_type]["strategy_crash"] += 1
            continue

        if not image_bytes:
            stats[source_type][f"miss_{tag}"] += 1
            if args.sleep:
                time.sleep(args.sleep / 4)
            continue

        webp_bytes = resize_to_webp(image_bytes)
        if not webp_bytes:
            stats[source_type]["resize_fail"] += 1
            continue

        storage_path = upload_to_storage(claim["id"], webp_bytes)
        if not storage_path:
            stats[source_type]["upload_fail"] += 1
            continue

        if not update_claim_path(claim["id"], storage_path):
            stats[source_type]["claim_update_fail"] += 1
            continue

        stats[source_type][f"rescued_{tag}"] += 1
        stats[source_type]["rescued_total"] += 1

        # For non-reddit, also patch raw_items.socialimage so the view picks
        # the image up without a schema change (reddit uses image_storage_path
        # which the view already reads).
        if source_type != "reddit" and image_url:
            if update_raw_socialimage(claim["raw_item_id"], image_url):
                stats[source_type]["socialimage_patched"] += 1

        if (i + 1) % 25 == 0:
            elapsed = time.time() - start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            tot_rescued = sum(s["rescued_total"] for s in stats.values())
            log.info("Progress: %d/%d (rescued=%d, %.1f/s)",
                     i + 1, len(claims), tot_rescued, rate)

        if args.sleep:
            time.sleep(args.sleep)

        # Periodic connection recycle
        if (i + 1) % 200 == 0:
            reset_client()

    elapsed = time.time() - start
    log.info("=" * 60)
    log.info("Done in %.0fs.", elapsed)
    for st, sub in sorted(stats.items()):
        log.info("%s:", st)
        for k, v in sorted(sub.items(), key=lambda kv: -kv[1]):
            log.info("    %-30s %d", k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())
