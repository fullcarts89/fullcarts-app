#!/usr/bin/env python3
"""
FullCarts Staging Promotion Job
================================
Promotes high-confidence reddit_staging entries into the normalized
product_versions table (instead of the legacy products+events flow).

Modes:
  --auto-only    Only promote tier=auto entries (default)
  --include-reviewed  Also promote entries with status=approved
  --dry-run      Show what would be promoted without writing

Data flow:
  reddit_staging (tier=auto, status=pending)
    → create/update product in products table
    → insert product_version (old state + new state)
    → mark staging entry as promoted
    → run change detection on affected products
"""

import sys
import logging
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")

from backend.lib.supabase_client import get_client
from backend.lib.nlp import guess_category
from typing import Optional, Dict, Set, List, Tuple
from backend.jobs.change_detector import detect_changes_for_product

log = logging.getLogger("fullcarts.promote")

# Cache detected columns per table to avoid repeated queries within a run.
_column_cache = {}  # type: Dict[str, Optional[Set]]


def _detect_table_columns(sb, table_name: str) -> Optional[set]:
    """Query a table to discover which columns actually exist."""
    if table_name in _column_cache:
        return _column_cache[table_name]
    try:
        result = sb.table(table_name).select("*").limit(1).execute()
        cols = set(result.data[0].keys()) if result.data else None
    except Exception:
        cols = None
    _column_cache[table_name] = cols
    return cols


def _strip_cols(record: dict, table_name: str, sb) -> dict:
    """Remove keys from a record that don't exist as columns in the DB table."""
    known = _detect_table_columns(sb, table_name)
    if known is None:
        return record
    return {k: v for k, v in record.items() if k in known or k in ("id", "created_at")}


def _promote_news_article(sb, entry, dry_run=False):
    """Promote a news-sourced staging entry to the news_articles table.

    If the entry also has structured size data, it gets the normal product
    promotion too (handled by the caller). This function handles the
    news_articles insert and auto-links to any matching product.

    Returns True if the news article was successfully created.
    """
    source_url = entry.get("source_url", "")
    title = (entry.get("title") or "")[:200]

    if not source_url:
        return False

    if dry_run:
        log.info(f"  [DRY RUN] Would create news article: {title[:60]}")
        return True

    try:
        # Determine article type from the NLP tier/fields
        article_type = "shrinkflation"  # default
        if entry.get("product_hint"):
            hint_lower = (entry["product_hint"] or "").lower()
            if "skimpflation" in hint_lower:
                article_type = "skimpflation"
            elif "downsiz" in hint_lower:
                article_type = "downsizing"

        # Build tags from title keywords
        tags = []
        title_lower = title.lower()
        for tag_word in ("policy", "investigation", "consumer", "analysis",
                         "data", "viral", "industry", "economy"):
            if tag_word in title_lower:
                tags.append(tag_word.capitalize())
        if not tags:
            tags.append("News")

        # Parse outlet from subreddit field or title
        outlet = None
        if "—" in title:
            outlet = title.rsplit("—", 1)[-1].strip()
        elif " - " in title:
            outlet = title.rsplit(" - ", 1)[-1].strip()

        # Parse published_at
        published_at = entry.get("posted_utc")

        article_record = {
            "url": source_url,
            "title": title.split(" — ")[0].split(" - ")[0].strip() if outlet else title,
            "outlet": outlet,
            "published_at": published_at,
            "summary": (entry.get("title") or "")[:500],
            "article_type": article_type,
            "tags": tags if tags else None,
            "staging_id": entry.get("id"),
            "products_extracted": 1 if entry.get("old_size") and entry.get("new_size") else 0,
            "status": "active",
        }

        result = sb.table("news_articles").upsert(
            _strip_cols(article_record, "news_articles", sb),
            on_conflict="url",
        ).execute()

        log.info(f"  News article created: {title[:60]} ({outlet or 'unknown outlet'})")
        return True

    except Exception as exc:
        log.warning(f"  News article creation failed for {source_url[:60]}: {exc}")
        return False


def _link_article_to_product(sb, entry, upc, dry_run=False):
    """Link a news article to a product via article_product_links."""
    source_url = entry.get("source_url", "")
    if not source_url or dry_run:
        return

    try:
        # Look up the article ID by URL
        result = sb.table("news_articles").select("id").eq("url", source_url).limit(1).execute()
        if not result.data:
            return

        article_id = result.data[0]["id"]
        context = f"Mentioned in article: {(entry.get('title') or '')[:100]}"

        sb.table("article_product_links").upsert(
            _strip_cols({
                "article_id": article_id,
                "product_upc": upc,
                "context": context,
            }, "article_product_links", sb),
            on_conflict="article_id,product_upc",
        ).execute()

        log.info(f"  Linked article to product {upc}")

    except Exception as exc:
        log.warning(f"  Article-product link failed: {exc}")


def promote_entry(sb, entry, dry_run=False):
    """Promote a single staging entry to products + product_versions.

    If the entry is a news article (source_type='news'), also creates a
    news_articles record and links it to the product.

    Returns True if successfully promoted.
    """
    is_news = entry.get("source_type") == "news" or entry.get("subreddit") == "google_news"

    old_size = entry.get("old_size")
    new_size = entry.get("new_size")

    # News articles without size data still get promoted to news_articles table
    if not old_size or not new_size:
        if is_news:
            success = _promote_news_article(sb, entry, dry_run=dry_run)
            if success and not dry_run:
                sb.table("reddit_staging").update(
                    {"status": "promoted"}
                ).eq("id", entry["id"]).execute()
            return success
        return False

    old_size = float(old_size)
    new_size = float(new_size)
    unit = entry.get("new_unit") or entry.get("old_unit") or "oz"

    # Build product record
    upc = f"REDDIT-{entry['id'][:8]}"
    product_name = (entry.get("product_hint") or "Unknown Product")[:100]
    brand = entry.get("brand")
    category = guess_category(f"{product_name} {brand or ''}")

    # Date noticed: when the community member spotted the change
    date_noticed = entry.get("date_noticed") or entry.get("posted_utc", "")[:10]
    if not date_noticed or len(date_noticed) < 7:
        date_noticed = datetime.now(tz=timezone.utc).strftime("%Y-%m-01")

    # Estimate a "before" date for the old product_version record (internal only)
    try:
        noticed_dt = datetime.strptime(date_noticed[:10], "%Y-%m-%d")
        # Use timedelta to avoid leap year crash (Feb 29 → replace(year-1) fails)
        date_before = (noticed_dt - timedelta(days=365)).strftime("%Y-%m-%d")
    except ValueError:
        date_before = "2023-01-01"

    source_url = entry.get("source_url", "")
    retailer = entry.get("retailer")

    if dry_run:
        log.info(f"  [DRY RUN] Would promote: {product_name} ({brand}) "
                 f"— {old_size}{unit} → {new_size}{unit} [{date_noticed}]")
        return True

    try:
        # Upsert product
        sb.table("products").upsert(_strip_cols({
            "upc": upc,
            "name": product_name,
            "brand": brand,
            "category": category,
            "current_size": new_size,
            "unit": unit,
            "type": "shrinkflation",
            "repeat_offender": False,
            "source": "reddit_bot",
        }, "products", sb), on_conflict="upc").execute()

        # Insert "before" version
        sb.table("product_versions").upsert(_strip_cols({
            "product_upc": upc,
            "observed_date": date_before,
            "size": old_size,
            "unit": unit,
            "price": float(entry["old_price"]) if entry.get("old_price") else None,
            "retailer": retailer,
            "source": "reddit_bot",
            "source_url": source_url,
            "notes": "Before state from r/shrinkflation post",
            "created_by": "promote_staging",
        }, "product_versions", sb), on_conflict="product_upc,observed_date,source").execute()

        # Insert "after" version
        sb.table("product_versions").upsert(_strip_cols({
            "product_upc": upc,
            "observed_date": date_noticed,
            "size": new_size,
            "unit": unit,
            "price": float(entry["new_price"]) if entry.get("new_price") else None,
            "retailer": retailer,
            "source": "reddit_bot",
            "source_url": source_url,
            "notes": "After state from r/shrinkflation post",
            "created_by": "promote_staging",
        }, "product_versions", sb), on_conflict="product_upc,observed_date,source").execute()

        # Also upsert into legacy events table for backward compatibility
        pct = round(((old_size - new_size) / old_size) * 100, 2) if old_size > 0 else 0
        sb.table("events").upsert(_strip_cols({
            "upc": upc,
            "date": date_noticed,
            "old_size": old_size,
            "new_size": new_size,
            "unit": unit,
            "pct": pct,
            "price_before": float(entry["old_price"]) if entry.get("old_price") else None,
            "price_after": float(entry["new_price"]) if entry.get("new_price") else None,
            "type": "shrinkflation",
            "notes": f"Reviewed and promoted from r/shrinkflation: {source_url}",
            "source": "reddit_bot",
        }, "events", sb), on_conflict="upc,date,source").execute()

        # Mark staging entry as promoted
        sb.table("reddit_staging").update(
            {"status": "promoted"}
        ).eq("id", entry["id"]).execute()

        # Run change detection for this product
        detect_changes_for_product(sb, upc)

        # If this is a news article, also create a news_articles record and link it
        if is_news:
            _promote_news_article(sb, entry, dry_run=dry_run)
            _link_article_to_product(sb, entry, upc, dry_run=dry_run)

        log.info(f"  Promoted: {product_name} ({brand}) "
                 f"— {old_size}{unit} → {new_size}{unit} [{date_noticed}]")
        return True

    except Exception as exc:
        log.warning(f"  Promotion failed for {entry.get('id', '?')}: {exc}")
        return False


def _fetch_all_rows(sb, table, filters: List[Tuple]) -> list:
    """Paginate through all matching rows (Supabase default limit is 1000)."""
    all_rows = []
    batch_size = 1000
    offset = 0
    while True:
        query = sb.table(table).select("*")
        for method, args in filters:
            query = getattr(query, method)(*args)
        result = query.range(offset, offset + batch_size - 1).execute()
        rows = result.data or []
        all_rows.extend(rows)
        if len(rows) < batch_size:
            break
        offset += batch_size
    return all_rows


def promote_pending(sb, include_reviewed=False, dry_run=False):
    """Promote all pending auto (and optionally approved) staging entries."""
    if include_reviewed:
        # Get both auto-tier pending and manually approved entries
        entries = _fetch_all_rows(sb, "reddit_staging", [
            ("eq", ("status", "pending")),
            ("eq", ("tier", "auto")),
        ])
        entries += _fetch_all_rows(sb, "reddit_staging", [
            ("eq", ("status", "approved")),
        ])
    else:
        entries = _fetch_all_rows(sb, "reddit_staging", [
            ("eq", ("status", "pending")),
            ("eq", ("tier", "auto")),
        ])

    log.info(f"Found {len(entries)} entries to promote")

    promoted = 0
    for entry in entries:
        if promote_entry(sb, entry, dry_run=dry_run):
            promoted += 1

    return promoted


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Promote reddit_staging entries to products + product_versions"
    )
    parser.add_argument("--include-reviewed", action="store_true",
                        help="Also promote admin-approved entries")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be promoted without writing")
    args = parser.parse_args()

    sb = get_client()
    promoted = promote_pending(sb, include_reviewed=args.include_reviewed, dry_run=args.dry_run)
    log.info(f"\n{'Would promote' if args.dry_run else 'Promoted'} {promoted} entries")


if __name__ == "__main__":
    main()
