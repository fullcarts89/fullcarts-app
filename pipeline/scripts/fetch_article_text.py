#!/usr/bin/env python3
"""Fetch full article body text for news/GDELT raw_items.

Follows redirects (e.g. Google News RSS links), extracts article body
text using BeautifulSoup heuristics, and stores the result back into
raw_payload.body for downstream claim extraction.

Usage:
    python -m pipeline.scripts.fetch_article_text [OPTIONS]

Options:
    --limit N       Process at most N items (default: all)
    --source-type   Only process 'news' or 'gdelt' (default: both)
    --dry-run       Print what would be fetched without writing
    --batch-size N  Items per batch (default: 50)
"""
import argparse
import html
import re
import time
from typing import Any, Dict, List, Optional, Set

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client

log = get_logger("fetch_article_text")

POSTGREST_PAGE_SIZE = 1000
# Polite rate limit: 1 request per second
_MIN_FETCH_INTERVAL = 1.0
_FETCH_TIMEOUT = 15  # seconds


def main():
    # type: () -> None
    parser = argparse.ArgumentParser(
        description="Fetch full article text for news items"
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Max items to process (0 = all)",
    )
    parser.add_argument(
        "--source-type", type=str, default=None,
        choices=["news", "gdelt"],
        help="Only process this source type (default: both)",
    )
    parser.add_argument(
        "--batch-size", type=int, default=50,
        help="Items per processing batch",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print URLs without fetching or writing",
    )
    args = parser.parse_args()

    log.info(
        "Starting article fetch (limit=%s, source=%s, dry_run=%s)",
        args.limit or "all",
        args.source_type or "news+gdelt",
        args.dry_run,
    )

    source_types = [args.source_type] if args.source_type else ["news", "gdelt"]
    items = _find_items_without_body(source_types, args.limit)
    log.info("Found %d items without article body text", len(items))

    if not items:
        log.info("Nothing to fetch. Done.")
        return

    total_fetched = 0
    total_failed = 0
    start_time = time.time()

    for i in range(0, len(items), args.batch_size):
        batch = items[i:i + args.batch_size]
        batch_num = i // args.batch_size + 1
        log.info(
            "Processing batch %d (%d items, %d/%d total)",
            batch_num, len(batch), i + len(batch), len(items),
        )

        for item in batch:
            url = _get_article_url(item)
            if not url:
                total_failed += 1
                continue

            if args.dry_run:
                log.info("[DRY RUN] Would fetch: %s", url[:100])
                total_fetched += 1
                continue

            body = _fetch_article_body(url)
            if body:
                _update_raw_payload_body(item, body)
                total_fetched += 1
            else:
                total_failed += 1

        elapsed = time.time() - start_time
        log.info(
            "Progress: fetched=%d, failed=%d, elapsed=%.0fs",
            total_fetched, total_failed, elapsed,
        )

    elapsed = time.time() - start_time
    log.info(
        "Done: fetched=%d, failed=%d, elapsed=%.0fs",
        total_fetched, total_failed, elapsed,
    )


def _find_items_without_body(source_types, limit):
    # type: (List[str], int) -> List[Dict[str, Any]]
    """Find news/gdelt raw_items that don't yet have body text."""
    client = get_client()
    items = []  # type: List[Dict[str, Any]]

    for st in source_types:
        offset = 0
        while True:
            resp = (
                client.table("raw_items")
                .select("id,source_type,source_id,raw_payload")
                .eq("source_type", st)
                .order("captured_at", desc=False)
                .range(offset, offset + POSTGREST_PAGE_SIZE - 1)
                .execute()
            )

            if not resp.data:
                break

            for row in resp.data:
                payload = row.get("raw_payload", {})
                # Skip if body already fetched
                if payload.get("body"):
                    continue
                items.append(row)
                if limit and len(items) >= limit:
                    return items

            if len(resp.data) < POSTGREST_PAGE_SIZE:
                break
            offset += POSTGREST_PAGE_SIZE

    return items


def _get_article_url(item):
    # type: (Dict[str, Any]) -> Optional[str]
    """Extract the article URL from a raw_item payload.

    For Google News RSS items, decodes the protobuf-encoded URL
    to get the real article URL.
    """
    payload = item.get("raw_payload", {})
    # GDELT uses 'url', RSS news uses 'link'
    url = payload.get("url") or payload.get("link") or None
    if not url:
        return None

    # Decode Google News RSS URLs
    if "news.google.com/rss/articles/" in url:
        decoded = _decode_google_news_url(url)
        if decoded:
            log.debug("Decoded Google News URL: %s -> %s", url[:60], decoded[:80])
            return decoded
        else:
            log.debug("Failed to decode Google News URL: %s", url[:80])
            return None

    return url


def _decode_google_news_url(source_url):
    # type: (str) -> Optional[str]
    """Decode a Google News RSS URL to the real article URL.

    Uses googlenewsdecoder library which handles both old (direct protobuf)
    and new (AU_yqL token requiring HTTP call) formats.
    """
    try:
        from googlenewsdecoder import gnewsdecoder
        result = gnewsdecoder(source_url, interval=0)
        if result.get("status"):
            return result["decoded_url"]
        log.debug("gnewsdecoder failed: %s", result.get("message", "unknown"))
        return None
    except Exception as exc:
        log.debug("Google News decode error: %s", str(exc)[:200])
        return None


def _fetch_article_body(url):
    # type: (str) -> Optional[str]
    """Fetch a URL, follow redirects, extract article body text.

    Returns the article text (up to 5000 chars) or None on failure.
    """
    import requests
    from bs4 import BeautifulSoup

    time.sleep(_MIN_FETCH_INTERVAL)

    try:
        headers = {
            "User-Agent": "FullCartsBot/1.0 (shrinkflation research; +https://fullcarts.org)",
            "Accept": "text/html,application/xhtml+xml",
        }
        resp = requests.get(
            url, headers=headers, timeout=_FETCH_TIMEOUT,
            allow_redirects=True,
        )

        if resp.status_code != 200:
            log.debug("HTTP %d for %s", resp.status_code, url[:80])
            return None

        content_type = resp.headers.get("content-type", "")
        if "html" not in content_type and "text" not in content_type:
            log.debug("Non-HTML content for %s: %s", url[:80], content_type)
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script, style, nav, header, footer, aside
        for tag in soup.find_all(["script", "style", "nav", "header",
                                   "footer", "aside", "noscript", "iframe"]):
            tag.decompose()

        # Try article tag first (most news sites)
        article = soup.find("article")
        if article:
            text = article.get_text(separator="\n", strip=True)
        else:
            # Fallback: look for common content containers
            main = (
                soup.find("main")
                or soup.find(class_=re.compile(r"article|post-content|entry-content|story-body", re.I))
                or soup.find(id=re.compile(r"article|content|story", re.I))
            )
            if main:
                text = main.get_text(separator="\n", strip=True)
            else:
                # Last resort: body text
                body = soup.find("body")
                text = body.get_text(separator="\n", strip=True) if body else ""

        # Clean up
        text = _clean_article_text(text)

        if len(text) < 50:
            log.debug("Article body too short (%d chars) for %s", len(text), url[:80])
            return None

        # Cap at 5000 chars to avoid bloating the DB
        if len(text) > 5000:
            text = text[:5000] + "\n[truncated]"

        return text

    except Exception as exc:
        log.debug("Fetch error for %s: %s", url[:80], str(exc)[:200])
        return None


def _clean_article_text(text):
    # type: (str) -> str
    """Clean extracted article text."""
    # Unescape HTML entities
    text = html.unescape(text)
    # Collapse multiple newlines
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Collapse multiple spaces
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Remove very short lines (likely nav items, ads)
    lines = text.split("\n")
    cleaned = []
    for line in lines:
        line = line.strip()
        if len(line) > 20 or not line:
            cleaned.append(line)
    return "\n".join(cleaned).strip()


def _update_raw_payload_body(item, body):
    # type: (Dict[str, Any], str) -> None
    """Update the raw_payload with the fetched body text."""
    client = get_client()
    payload = item.get("raw_payload", {})
    payload["body"] = body

    try:
        (
            client.table("raw_items")
            .update({"raw_payload": payload})
            .eq("id", item["id"])
            .execute()
        )
    except Exception as exc:
        log.error(
            "Failed to update raw_item %s: %s",
            item["id"], str(exc)[:200],
        )


if __name__ == "__main__":
    main()
