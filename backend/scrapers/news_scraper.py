#!/usr/bin/env python3
"""
FullCarts Google News RSS Scraper
==================================
Fetches shrinkflation-related news articles from Google News RSS feeds,
extracts product/brand/size data via the shared NLP parser, and upserts
to the reddit_staging table for review or auto-promotion.

No API key required — uses Google News public RSS.

Usage:
  python -m backend.scrapers.news_scraper
  python -m backend.scrapers.news_scraper --dry-run
  python -m backend.scrapers.news_scraper --query "shrinkflation cereal"
"""

import sys
import time
import logging
import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from urllib.parse import quote_plus

import requests

sys.path.insert(0, ".")

from backend.lib.supabase_client import get_client
from backend.lib.nlp import parse_text, confidence_tier, has_shrink_keywords

log = logging.getLogger("fullcarts.news")

USER_AGENT = "FullCartsBot/1.0 (fullcarts.org community shrinkflation tracker)"

# Google News RSS searches
DEFAULT_QUERIES = [
    "shrinkflation",
    "shrinkflation grocery",
    "product downsizing",
    "package size reduction food",
    "skimpflation",
]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"


def fetch_rss(query: str) -> list[dict]:
    """Fetch and parse a Google News RSS feed for the given query."""
    url = GOOGLE_NEWS_RSS.format(query=quote_plus(query))
    headers = {"User-Agent": USER_AGENT}

    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        log.warning(f"RSS fetch failed for '{query}': {e}")
        return []

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError as e:
        log.warning(f"RSS parse failed for '{query}': {e}")
        return []

    items = []
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        pubdate_el = item.find("pubDate")
        desc_el = item.find("description")

        title = unescape(title_el.text or "") if title_el is not None else ""
        link = link_el.text or "" if link_el is not None else ""
        pubdate = pubdate_el.text or "" if pubdate_el is not None else ""
        description = unescape(desc_el.text or "") if desc_el is not None else ""

        # Strip HTML tags from description
        import re
        description = re.sub(r"<[^>]+>", " ", description).strip()

        items.append({
            "title": title,
            "link": link,
            "pubdate": pubdate,
            "description": description,
        })

    return items


def parse_pubdate(pubdate_str: str) -> str | None:
    """Parse RSS pubDate to ISO format."""
    if not pubdate_str:
        return None
    # Google News format: "Mon, 03 Mar 2026 12:00:00 GMT"
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%SZ",
    ):
        try:
            dt = datetime.strptime(pubdate_str.strip(), fmt)
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            continue
    return None


def build_staging_entry(article: dict, parsed: dict, tier: str) -> dict:
    """Build a reddit_staging-compatible entry from a news article."""
    pubdate_iso = parse_pubdate(article["pubdate"])

    # Date noticed = article publish month
    if pubdate_iso:
        date_noticed = pubdate_iso[:7] + "-01"
    else:
        date_noticed = datetime.now(tz=timezone.utc).strftime("%Y-%m-01")

    return {
        "source_url": article["link"],
        "subreddit": "google_news",
        "posted_utc": pubdate_iso,
        "scraped_utc": datetime.now(tz=timezone.utc).isoformat(),
        "tier": tier,
        "status": "pending",
        "title": article["title"][:200],
        "brand": parsed["brand"],
        "product_hint": parsed["product_hint"],
        "old_size": parsed["old_size"],
        "old_unit": parsed["old_unit"],
        "new_size": parsed["new_size"],
        "new_unit": parsed["new_unit"],
        "old_price": parsed["old_price"],
        "new_price": parsed["new_price"],
        "explicit_from_to": parsed["explicit_from_to"],
        "fields_found": parsed["fields_found"],
        "score": 0,
        "num_comments": 0,
        "date_noticed": date_noticed,
    }


def run(queries: list[str] | None = None, dry_run: bool = False):
    """Scrape Google News RSS for shrinkflation articles."""
    queries = queries or DEFAULT_QUERIES
    sb = None if dry_run else get_client()

    all_entries = []
    stats = {"articles": 0, "relevant": 0, "auto": 0, "review": 0, "discard": 0}

    for query in queries:
        log.info(f"Fetching RSS: '{query}'")
        articles = fetch_rss(query)
        log.info(f"  Got {len(articles)} articles")

        for article in articles:
            stats["articles"] += 1
            full_text = f"{article['title']}\n{article['description']}"

            # Only process articles with shrinkflation keywords
            if not has_shrink_keywords(full_text):
                continue

            stats["relevant"] += 1
            parsed = parse_text(full_text)
            tier = confidence_tier(parsed)
            stats[tier] += 1

            if tier == "discard":
                continue

            entry = build_staging_entry(article, parsed, tier)
            all_entries.append(entry)

            log.info(f"  [{tier.upper():6}] {article['title'][:80]}")

        time.sleep(1)  # Polite delay between queries

    log.info(f"\nTotal: {stats['articles']} articles, {stats['relevant']} relevant")
    log.info(f"  auto:{stats['auto']}  review:{stats['review']}  discard:{stats['discard']}")
    log.info(f"  Entries to stage: {len(all_entries)}")

    if dry_run:
        log.info("[DRY RUN] Skipping Supabase upsert")
        return

    if not all_entries:
        log.info("No entries to upsert")
        return

    # Upsert to reddit_staging (same table, same pipeline)
    upserted = 0
    for i in range(0, len(all_entries), 50):
        batch = all_entries[i:i + 50]
        try:
            sb.table("reddit_staging").upsert(
                batch, on_conflict="source_url"
            ).execute()
            upserted += len(batch)
        except Exception as exc:
            log.warning(f"Batch upsert failed: {exc}")
            for entry in batch:
                try:
                    sb.table("reddit_staging").upsert(
                        entry, on_conflict="source_url"
                    ).execute()
                    upserted += 1
                except Exception as exc2:
                    log.warning(f"  Single upsert failed: {entry.get('source_url', '?')[:60]} — {exc2}")

    log.info(f"Upserted {upserted} entries to reddit_staging")


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)s  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    parser = argparse.ArgumentParser(
        description="Scrape Google News RSS for shrinkflation articles"
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be staged without writing")
    parser.add_argument("--query", action="append",
                        help="Custom search query (can be repeated)")
    args = parser.parse_args()

    run(queries=args.query, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
