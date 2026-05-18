#!/usr/bin/env python3
"""Backfill product_entities.image_url from available sources.

Priority order:
  1. Supabase Storage (claim-images bucket) — curated from Reddit posts
  2. Kroger API product images (from raw_items.raw_payload)
  3. Walmart API product images (from raw_items.raw_payload)
  4. Open Food Facts product images (from raw_items.raw_payload)
  5. Open Food Facts live API lookup by UPC/EAN — catches products not
     yet seen by off_discovery
  6. GDELT article hero image (raw_payload.socialimage via matched claims)

Usage:
    python -m pipeline.scripts.backfill_entity_images
    python -m pipeline.scripts.backfill_entity_images --dry-run
    python -m pipeline.scripts.backfill_entity_images --limit 500
    python -m pipeline.scripts.backfill_entity_images --no-off-api
"""
import argparse
import logging
import os
import sys
from typing import Any, Dict, List, Optional

LOG = logging.getLogger("backfill_entity_images")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ntyhbapphnzlariakgrw.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
STORAGE_BUCKET = "claim-images"
PAGE_SIZE = 200

# OFF live-lookup fallback. Kept module-level so a single
# RateLimitedSession is reused across all entities in a run.
_OFF_SESSION = None  # type: Optional[Any]


def _get_off_session():
    # type: () -> Any
    """Lazily build the OFF API session. Imports are local so the
    script still imports cleanly if pipeline.* deps aren't available
    (e.g. in a barebones CI image)."""
    global _OFF_SESSION
    if _OFF_SESSION is not None:
        return _OFF_SESSION
    from pipeline.config import OFF_DELAY, USER_AGENT
    from pipeline.lib.http_client import RateLimitedSession
    _OFF_SESSION = RateLimitedSession(
        requests_per_second=1.0 / OFF_DELAY,
        user_agent=USER_AGENT,
    )
    return _OFF_SESSION


def _normalize_to_ean13(upc):
    # type: (Optional[str]) -> Optional[str]
    """Normalize a barcode to the 13-digit EAN form OFF expects.

    OFF stores all products by 13-digit EAN. US-issued UPC-A codes
    are 12 digits; the convention is to prepend a leading "0" to get
    the EAN-13. Codes already 13 digits pass through. Anything else
    (synthetic CLAIM-/REDDIT- keys, non-numeric, wrong length) is
    rejected so we don't fire off useless OFF API calls.
    """
    if not upc:
        return None
    s = str(upc).strip()
    if not s.isdigit():
        return None
    if len(s) == 13:
        return s
    if len(s) == 12:
        return "0" + s
    # 8-digit EAN-8 codes exist but OFF rarely indexes US products
    # under them, and short numeric strings are often noise. Skip.
    return None


def _try_off_api_live(sb, entity_id):
    # type: (Any, str) -> Optional[str]
    """Live-fetch a product photo from the OFF API by UPC/EAN.

    Picks up products that `off_discovery` hasn't scraped yet — OFF has
    a far longer tail than our category-anchored crawl ever reaches.
    Tries each variant UPC in turn, returns the first image found.

    Costs at most `len(upcs) * (1 / OFF_DELAY)` seconds per entity, but
    only fires after all the cached-image lookups missed, so it's
    bounded by the ~15% imageless tail.
    """
    variants = (
        sb.table("pack_variants")
        .select("upc")
        .eq("entity_id", entity_id)
        .not_.is_("upc", "null")
        .execute()
    )
    upcs = [v["upc"] for v in (variants.data or []) if v.get("upc")]
    if not upcs:
        return None

    from pipeline.config import OFF_API_BASE
    session = _get_off_session()
    fields = "image_url,image_front_url,image_front_small_url"

    # Try at most 3 UPCs; if the first variant doesn't resolve, the
    # later ones (often size variants of the same product) usually
    # don't either, but it's cheap insurance for split entities.
    for upc in upcs[:3]:
        ean = _normalize_to_ean13(upc)
        if not ean:
            continue
        url = "{}/product/{}.json?fields={}".format(OFF_API_BASE, ean, fields)
        resp = session.get(url, raise_for_status=False)
        if resp is None or resp.status_code != 200:
            continue
        try:
            data = resp.json()
        except ValueError:
            continue
        # OFF returns {"status": 0} for unknown products.
        if data.get("status") != 1:
            continue
        product = data.get("product") or {}
        img = (
            product.get("image_front_url")
            or product.get("image_url")
            or product.get("image_front_small_url")
        )
        if img:
            return img.strip()

    return None


def _get_client():
    if not SUPABASE_KEY:
        print("ERROR: SUPABASE_KEY not set", file=sys.stderr)
        sys.exit(1)
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def _public_storage_url(path: str) -> str:
    """Build the public URL for a Supabase Storage object."""
    return "{}/storage/v1/object/public/{}/{}".format(
        SUPABASE_URL, STORAGE_BUCKET, path
    )


def _fetch_entities_without_images(sb, limit: int = 0) -> List[Dict[str, Any]]:
    """Fetch product_entities where image_url IS NULL.

    Paginates via id-keyset to bypass PostgREST's per-request row cap
    (default 1000). Ordered by id (not brand) so updating a row's image_url
    in-flight doesn't shift the cursor.
    """
    out = []  # type: List[Dict[str, Any]]
    last_id = None
    while True:
        q = (
            sb.table("product_entities")
            .select("id, brand, canonical_name")
            .is_("image_url", "null")
            .order("id")
            .limit(PAGE_SIZE)
        )
        if last_id is not None:
            q = q.gt("id", last_id)
        resp = q.execute()
        batch = resp.data or []
        if not batch:
            break
        out.extend(batch)
        last_id = batch[-1]["id"]
        if limit > 0 and len(out) >= limit:
            return out[:limit]
        if len(batch) < PAGE_SIZE:
            break
    return out


def _try_claim_image(sb, entity_id: str) -> Optional[str]:
    """Check if any matched claim has an image in Supabase Storage."""
    resp = (
        sb.table("claims")
        .select("image_storage_path")
        .eq("matched_entity_id", entity_id)
        .not_.is_("image_storage_path", "null")
        .limit(1)
        .execute()
    )
    if resp.data and resp.data[0].get("image_storage_path"):
        return _public_storage_url(resp.data[0]["image_storage_path"])
    return None


def _try_api_image(sb, entity_id: str, source_type: str) -> Optional[str]:
    """Check raw_items for an image URL from a retail API source.

    Joins entity -> pack_variants -> raw_items via UPC matching.
    """
    # Get UPCs for this entity's variants
    variants = (
        sb.table("pack_variants")
        .select("upc")
        .eq("entity_id", entity_id)
        .not_.is_("upc", "null")
        .execute()
    )
    upcs = [v["upc"] for v in (variants.data or []) if v.get("upc")]
    if not upcs:
        return None

    for upc in upcs[:3]:
        resp = (
            sb.table("raw_items")
            .select("raw_payload")
            .eq("source_type", source_type)
            .ilike("source_id", "%{}%".format(upc))
            .limit(1)
            .execute()
        )
        if not resp.data:
            continue

        payload = resp.data[0].get("raw_payload") or {}
        url = _extract_image_from_payload(payload, source_type)
        if url:
            return url

    return None


def _try_news_socialimage(sb, entity_id: str) -> Optional[str]:
    """Pull a GDELT article hero image via the entity's matched claims.

    Path: entity -> claims (matched_entity_id) -> raw_items.raw_payload.socialimage.
    Only GDELT articles carry socialimage; Google News RSS items have no image
    field, so source_type is restricted to 'gdelt'.
    """
    claims = (
        sb.table("claims")
        .select("raw_item_id")
        .eq("matched_entity_id", entity_id)
        .not_.is_("raw_item_id", "null")
        .limit(20)
        .execute()
    )
    raw_ids = [
        c["raw_item_id"] for c in (claims.data or []) if c.get("raw_item_id")
    ]
    if not raw_ids:
        return None

    resp = (
        sb.table("raw_items")
        .select("raw_payload")
        .in_("id", raw_ids)
        .eq("source_type", "gdelt")
        .execute()
    )
    for row in resp.data or []:
        payload = row.get("raw_payload") or {}
        url = (payload.get("socialimage") or "").strip()
        if url:
            return url
    return None


def _extract_image_from_payload(
    payload: Dict[str, Any], source_type: str
) -> Optional[str]:
    """Extract image URL from a raw_items payload by source type."""
    if source_type == "kroger_api":
        images = payload.get("images") or []
        if images:
            sizes = images[0].get("sizes") or []
            if sizes:
                return sizes[0].get("url")
        return None

    if source_type == "walmart":
        return payload.get("largeImage") or payload.get("mediumImage")

    if source_type == "openfoodfacts":
        return payload.get("image_url") or payload.get("image_front_url")

    return None


def main():
    parser = argparse.ArgumentParser(description="Backfill entity images")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument(
        "--no-off-api",
        action="store_true",
        help="Skip the live OFF API fallback (faster; loses ~5-10pct of catches)",
    )
    args = parser.parse_args()

    sb = _get_client()

    LOG.info("Fetching entities without images...")
    entities = _fetch_entities_without_images(sb, limit=args.limit)
    LOG.info("Found %d entities missing images", len(entities))

    if not entities:
        LOG.info("All entities have images. Done.")
        return

    stats = {"updated": 0, "still_missing": 0, "errors": 0}
    by_source = {"claim": 0, "kroger_api": 0, "walmart": 0,
                 "openfoodfacts": 0, "off_api_live": 0,
                 "gdelt_socialimage": 0}
    sources_tried = [
        ("claim", lambda sb, eid: _try_claim_image(sb, eid)),
        ("kroger_api", lambda sb, eid: _try_api_image(sb, eid, "kroger_api")),
        ("walmart", lambda sb, eid: _try_api_image(sb, eid, "walmart")),
        ("openfoodfacts",
         lambda sb, eid: _try_api_image(sb, eid, "openfoodfacts")),
    ]
    # OFF live fallback fires after the cached-image lookups, before
    # the GDELT social-image fallback. Article hero shots are a worse
    # product photo than a real OFF catalog image.
    if not args.no_off_api:
        sources_tried.append(
            ("off_api_live", lambda sb, eid: _try_off_api_live(sb, eid))
        )
    sources_tried.append(
        ("gdelt_socialimage", lambda sb, eid: _try_news_socialimage(sb, eid))
    )

    for i, entity in enumerate(entities):
        eid = entity["id"]
        image_url = None
        matched_source = None

        try:
            for source_name, fetcher in sources_tried:
                image_url = fetcher(sb, eid)
                if image_url:
                    matched_source = source_name
                    break

            if image_url:
                if not args.dry_run:
                    sb.table("product_entities").update(
                        {"image_url": image_url}
                    ).eq("id", eid).execute()
                stats["updated"] += 1
                by_source[matched_source] = by_source.get(matched_source, 0) + 1
                if stats["updated"] <= 5:
                    LOG.info(
                        "  [%s] %s / %s → %s",
                        "DRY" if args.dry_run else "SET",
                        entity.get("brand", "?"),
                        entity.get("canonical_name", "?"),
                        matched_source,
                    )
            else:
                stats["still_missing"] += 1

        except Exception as e:
            stats["errors"] += 1
            if stats["errors"] <= 10:
                LOG.error("Error on entity %s: %s", eid[:8], e)

        if (i + 1) % 100 == 0:
            LOG.info(
                "  Progress: %d/%d (updated=%d, missing=%d)",
                i + 1, len(entities), stats["updated"], stats["still_missing"],
            )

    mode = "DRY RUN" if args.dry_run else "LIVE"
    LOG.info("\n%s RESULTS:", mode)
    for k, v in stats.items():
        LOG.info("  %s: %d", k, v)
    LOG.info("  by_source:")
    for k, v in by_source.items():
        LOG.info("    %s: %d", k, v)


if __name__ == "__main__":
    main()
