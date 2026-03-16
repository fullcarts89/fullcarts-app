"""GDELT historical backfill scraper.

Walks backward through GDELT's DOC API in 3-month windows, from a
configurable start date (default: Jan 2022) to the point where the
daily scraper started collecting (Dec 2025).

Uses the same source_type='gdelt' and URL-based source_id as the daily
scraper, so ON CONFLICT deduplicates automatically.

Usage via CLI:
    python -m pipeline gdelt_backfill [--dry-run]
"""
import hashlib
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from pipeline.config import (
    GDELT_DELAY,
    GDELT_DOC_API,
    GDELT_QUERIES,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

# GDELT DOC API date format: YYYYMMDDHHMMSS
_DATE_FMT = "%Y%m%d%H%M%S"
_SEENDATE_FMT = "%Y%m%dT%H%M%SZ"

# Walk backward in 3-month windows
_WINDOW_DAYS = 90

# GDELT allows up to 250 results per query
_MAX_RECORDS = 250

# Default date range: Jan 2022 through Nov 2025
# (daily scraper covers Dec 2025 onward)
_BACKFILL_START = "20220101000000"
_BACKFILL_END = "20251201000000"


def _parse_seendate(seendate):
    # type: (Optional[str]) -> Optional[str]
    """Parse GDELT seendate into ISO 8601 UTC string."""
    if not seendate:
        return None
    try:
        dt = datetime.strptime(seendate, _SEENDATE_FMT).replace(
            tzinfo=timezone.utc
        )
        return dt.isoformat()
    except ValueError:
        return None


def _date_windows(start_str, end_str):
    # type: (str, str) -> List[tuple]
    """Generate (start, end) date windows walking forward in 3-month chunks.

    Returns list of (start_str, end_str) tuples in GDELT date format.
    """
    start = datetime.strptime(start_str, _DATE_FMT)
    end = datetime.strptime(end_str, _DATE_FMT)

    windows = []
    current = start
    while current < end:
        window_end = current
        # Advance ~3 months
        month = current.month + 3
        year = current.year
        while month > 12:
            month -= 12
            year += 1
        try:
            window_end = current.replace(year=year, month=month)
        except ValueError:
            # Handle month-end edge cases (e.g., Jan 31 -> Apr 30)
            import calendar
            last_day = calendar.monthrange(year, month)[1]
            window_end = current.replace(year=year, month=month, day=min(current.day, last_day))

        if window_end > end:
            window_end = end

        windows.append((
            current.strftime(_DATE_FMT),
            window_end.strftime(_DATE_FMT),
        ))
        current = window_end

    return windows


class GdeltBackfillScraper(BaseScraper):
    """Backfills GDELT shrinkflation articles from Jan 2022 to Nov 2025."""

    scraper_name = "gdelt_backfill"
    source_type = "gdelt"

    def __init__(self):
        # type: () -> None
        super().__init__()
        # Slower rate for backfill — 1 request per 2 seconds to avoid 429s
        self._session = RateLimitedSession(
            requests_per_second=0.5,
            max_retries=5,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor, dry_run=False
    ):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Fetch articles across all date windows and queries."""
        seen_urls = set()  # type: Set[str]
        collected = []  # type: List[Dict[str, Any]]

        windows = _date_windows(_BACKFILL_START, _BACKFILL_END)
        self.log.info(
            "Backfilling %d date windows from %s to %s (%d queries each)",
            len(windows), _BACKFILL_START[:8], _BACKFILL_END[:8],
            len(GDELT_QUERIES),
        )

        for win_idx, (win_start, win_end) in enumerate(windows):
            win_label = "%s - %s" % (win_start[:8], win_end[:8])
            self.log.info(
                "Window %d/%d: %s",
                win_idx + 1, len(windows), win_label,
            )

            window_count = 0
            for query in GDELT_QUERIES:
                params = {
                    "query": query,
                    "mode": "ArtList",
                    "maxrecords": _MAX_RECORDS,
                    "format": "json",
                    "startdatetime": win_start,
                    "enddatetime": win_end,
                }

                self.log.debug(
                    "Fetching GDELT: query=%r, window=%s", query, win_label,
                )

                resp = self._session.get(GDELT_DOC_API, params=params)
                if resp is None:
                    self.log.warning(
                        "GDELT fetch failed for query=%r window=%s",
                        query, win_label,
                    )
                    continue

                try:
                    data = resp.json()
                except Exception as exc:
                    self.log.warning(
                        "JSON parse error for query=%r: %s", query, exc,
                    )
                    continue

                articles = data.get("articles") or []
                self.log.debug(
                    "query=%r window=%s returned %d articles",
                    query, win_label, len(articles),
                )

                for article in articles:
                    language = (article.get("language") or "").strip().lower()
                    if language != "english":
                        continue

                    article_url = (article.get("url") or "").strip()
                    if not article_url or article_url in seen_urls:
                        continue
                    seen_urls.add(article_url)

                    collected.append(article)
                    window_count += 1

            self.log.info(
                "Window %s: %d new articles (total so far: %d)",
                win_label, window_count, len(collected),
            )

            # Brief pause between windows to avoid sustained rate limiting
            if win_idx < len(windows) - 1:
                time.sleep(3)

        self.log.info(
            "Backfill complete: %d unique English articles across all windows",
            len(collected),
        )
        return collected

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        url = item.get("url", "")
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return item.get("url") or None

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return _parse_seendate(item.get("seendate"))

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        return {
            "last_backfill_date": today,
            "articles_backfilled": len(items),
        }
