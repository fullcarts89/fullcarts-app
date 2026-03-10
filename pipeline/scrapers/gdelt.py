"""GDELT DOC API scraper.

For each query in config.GDELT_QUERIES, fetches articles from the GDELT v2
Document API in ArtList mode.  Filters to English-language articles and
deduplicates across queries within a single run by tracking seen URLs.
source_id is a SHA-256 hash of the article URL.
"""
import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote_plus

from pipeline.config import (
    GDELT_DELAY,
    GDELT_DOC_API,
    GDELT_MAX_RECORDS,
    GDELT_QUERIES,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

_SEENDATE_FMT = "%Y%m%dT%H%M%SZ"


def _parse_seendate(seendate: Optional[str]) -> Optional[str]:
    """Parse GDELT seendate ("YYYYMMDDTHHMMSSZ") into ISO 8601 UTC string.

    Returns None if the value is absent or unparseable.
    """
    if not seendate:
        return None
    try:
        dt = datetime.strptime(seendate, _SEENDATE_FMT).replace(
            tzinfo=timezone.utc
        )
        return dt.isoformat()
    except ValueError:
        return None


class GdeltScraper(BaseScraper):
    """Fetches shrinkflation articles from the GDELT DOC API."""

    scraper_name = "gdelt_news"
    source_type = "gdelt"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=1.0 / GDELT_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch articles for every GDELT query, deduplicating by URL."""
        seen_urls: Set[str] = set()
        collected: List[Dict[str, Any]] = []

        for query in GDELT_QUERIES:
            params = {
                "query": query,
                "mode": "ArtList",
                "maxrecords": GDELT_MAX_RECORDS,
                "format": "json",
            }
            self.log.debug("Fetching GDELT for query=%r", query)

            resp = self._session.get(GDELT_DOC_API, params=params)
            if resp is None:
                self.log.warning(
                    "GDELT fetch failed for query=%r; skipping.", query
                )
                continue

            try:
                data = resp.json()
            except Exception as exc:
                self.log.warning(
                    "JSON parse error for query=%r: %s; skipping.", query, exc
                )
                continue

            articles = data.get("articles") or []
            self.log.debug(
                "query=%r returned %d articles", query, len(articles)
            )

            for article in articles:
                # Filter: English only.
                language = (article.get("language") or "").strip().lower()
                if language != "english":
                    continue

                article_url = (article.get("url") or "").strip()
                if not article_url or article_url in seen_urls:
                    continue
                seen_urls.add(article_url)

                collected.append(article)

        self.log.info(
            "Collected %d unique English articles across all queries",
            len(collected),
        )
        return collected

    def source_id_for(self, item: Dict[str, Any]) -> str:
        url = item.get("url", "")
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("url") or None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return _parse_seendate(item.get("seendate"))

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record today's date so downstream jobs can track freshness."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {"last_run_date": today}
