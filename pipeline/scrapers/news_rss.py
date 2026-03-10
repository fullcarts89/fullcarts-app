"""Google News RSS scraper.

For each query in config.NEWS_QUERIES, fetches the Google News RSS feed and
parses articles.  Deduplicates across queries within a single run by tracking
seen URLs.  source_id is a SHA-256 hash of the article link.
"""
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote_plus

from pipeline.config import NEWS_QUERIES, NEWS_RSS_DELAY, USER_AGENT
from pipeline.lib.hashing import content_hash
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

_GNEWS_RSS = (
    "https://news.google.com/rss/search"
    "?q={query}&hl=en-US&gl=US&ceid=US:en"
)


def _parse_pubdate(pubdate_str: Optional[str]) -> Optional[str]:
    """Parse RFC 2822 pubDate into an ISO 8601 UTC string.

    Returns None if parsing fails.
    """
    if not pubdate_str:
        return None
    try:
        dt = parsedate_to_datetime(pubdate_str)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return None


def _source_name_from_item(item: ET.Element) -> str:
    """Extract the <source> element text from an RSS <item>."""
    source_el = item.find("source")
    if source_el is not None and source_el.text:
        return source_el.text.strip()
    return ""


class NewsRssScraper(BaseScraper):
    """Fetches shrinkflation news articles via Google News RSS."""

    scraper_name = "news_rss"
    source_type = "news"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=1.0 / NEWS_RSS_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch articles for every query, deduplicating by URL across queries."""
        seen_urls: Set[str] = set()
        collected: List[Dict[str, Any]] = []

        for query in NEWS_QUERIES:
            url = _GNEWS_RSS.format(query=quote_plus(query))
            self.log.debug("Fetching RSS for query=%r", query)

            resp = self._session.get(url)
            if resp is None:
                self.log.warning(
                    "RSS fetch failed for query=%r; skipping.", query
                )
                continue

            try:
                root = ET.fromstring(resp.text)
            except ET.ParseError as exc:
                self.log.warning(
                    "XML parse error for query=%r: %s; skipping.", query, exc
                )
                continue

            channel = root.find("channel")
            if channel is None:
                self.log.warning(
                    "No <channel> in RSS for query=%r; skipping.", query
                )
                continue

            items = channel.findall("item")
            self.log.debug(
                "query=%r returned %d items", query, len(items)
            )

            for item in items:
                link_el = item.find("link")
                link = (link_el.text or "").strip() if link_el is not None else ""

                if not link or link in seen_urls:
                    continue
                seen_urls.add(link)

                title_el = item.find("title")
                desc_el = item.find("description")
                pubdate_el = item.find("pubDate")

                title = (title_el.text or "").strip() if title_el is not None else ""
                pubdate = (
                    (pubdate_el.text or "").strip() if pubdate_el is not None else ""
                )
                description = (
                    (desc_el.text or "").strip() if desc_el is not None else ""
                )
                source_name = _source_name_from_item(item)

                collected.append(
                    {
                        "title": title,
                        "link": link,
                        "pubdate": pubdate,
                        "description": description,
                        "source_name": source_name,
                        "query": query,
                    }
                )

        self.log.info("Collected %d unique articles across all queries", len(collected))
        return collected

    def source_id_for(self, item: Dict[str, Any]) -> str:
        import hashlib

        link = item.get("link", "")
        return hashlib.sha256(link.encode("utf-8")).hexdigest()

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("link") or None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return _parse_pubdate(item.get("pubdate"))

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record today's date so downstream jobs can track freshness."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {"last_run_date": today}
