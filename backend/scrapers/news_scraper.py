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

import os
import re
import sys
import time
import logging
import argparse
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html import unescape
from typing import Optional, List
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


def fetch_rss(query: str) -> List[dict]:
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
        description = re.sub(r"<[^>]+>", " ", description).strip()

        items.append({
            "title": title,
            "link": link,
            "pubdate": pubdate,
            "description": description,
        })

    return items


def parse_pubdate(pubdate_str: str) -> Optional[str]:
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
        "source_type": "news",
        # status is NOT included — the DB default ('pending') applies on
        # first insert, and omitting it ensures re-scraping the same
        # source_url does not reset an already-reviewed record.
        "title": article["title"][:200],
        "body": article.get("description", "")[:2000],
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


def write_step_summary(entries: List[dict], stats: dict, dry_run: bool):
    """Write a GitHub Actions Step Summary with a table of staged entries."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    lines = []
    mode = "DRY RUN" if dry_run else "Live"
    lines.append(f"## News Scraper Results ({mode})\n")
    lines.append(f"**{stats['articles']}** articles scanned, "
                 f"**{stats['relevant']}** relevant, "
                 f"**{len(entries)}** staged "
                 f"(auto: {stats['auto']}, review: {stats['review']}, "
                 f"discard: {stats['discard']})\n")

    if entries:
        lines.append("| # | Tier | Title | Brand | Product | Old Size | New Size |")
        lines.append("|---|------|-------|-------|---------|----------|----------|")
        for i, e in enumerate(entries, 1):
            tier = e.get("tier", "").upper()
            title = (e.get("title") or "")[:60]
            brand = e.get("brand") or "—"
            product = e.get("product_hint") or "—"
            old_sz = f"{e['old_size']} {e['old_unit']}" if e.get("old_size") else "—"
            new_sz = f"{e['new_size']} {e['new_unit']}" if e.get("new_size") else "—"
            lines.append(f"| {i} | {tier} | {title} | {brand} | {product} | {old_sz} | {new_sz} |")
    else:
        lines.append("*No entries matched the staging criteria.*\n")

    with open(summary_path, "a") as f:
        f.write("\n".join(lines) + "\n")


def run(queries: Optional[List[str]] = None, dry_run: bool = False):
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

    write_step_summary(all_entries, stats, dry_run)

    if dry_run:
        log.info("[DRY RUN] Skipping Supabase upsert")
        return

    if not all_entries:
        log.info("No entries to upsert")
        return

    # Pre-filter: skip entries whose source_url already has a non-pending
    # status (promoted/dismissed/rejected/evidence_wall) so we never
    # accidentally overwrite a reviewed record.
    source_urls = [e["source_url"] for e in all_entries if e.get("source_url")]
    reviewed_urls = set()  # type: Set[str]
    for chunk_start in range(0, len(source_urls), 200):
        chunk = source_urls[chunk_start:chunk_start + 200]
        try:
            result = (sb.table("reddit_staging")
                      .select("source_url")
                      .in_("source_url", chunk)
                      .neq("status", "pending")
                      .execute())
            reviewed_urls.update(row["source_url"] for row in (result.data or []))
        except Exception:
            pass  # If the check fails, ignore_duplicates still protects us

    if reviewed_urls:
        all_entries = [e for e in all_entries if e.get("source_url") not in reviewed_urls]
        log.info(f"  Skipped {len(reviewed_urls)} already-reviewed entries")

    if not all_entries:
        log.info("All entries already reviewed — nothing to upsert")
        return

    # Upsert to reddit_staging (same table, same pipeline)
    upserted = 0
    for i in range(0, len(all_entries), 50):
        batch = all_entries[i:i + 50]
        try:
            sb.table("reddit_staging").upsert(
                batch, on_conflict="source_url",
                ignore_duplicates=False,
                default_to_null=False,
            ).execute()
            upserted += len(batch)
        except Exception as exc:
            log.warning(f"Batch upsert failed: {exc}")
            if hasattr(exc, "response") and exc.response is not None:
                log.warning(f"  Response: {getattr(exc.response, 'text', '')[:300]}")
            for entry in batch:
                try:
                    sb.table("reddit_staging").upsert(
                        entry, on_conflict="source_url",
                        ignore_duplicates=False,
                        default_to_null=False,
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
