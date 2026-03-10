"""Reddit recent-posts scraper.

Fetches new posts from r/shrinkflation using the Reddit JSON API (no auth).
Paginates forward through /new until it hits posts older than the last run.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import (
    ARCTIC_SHIFT_BASE,
    REDDIT_JSON_DELAY,
    TARGET_SUBREDDIT,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

_REDDIT_NEW_URL = (
    "https://www.reddit.com/r/{subreddit}/new.json"
)
_MAX_PAGES = 10


class RedditRecentScraper(BaseScraper):
    """Incrementally fetches new posts from r/shrinkflation via Reddit JSON."""

    scraper_name = "reddit_recent"
    source_type = "reddit"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=1.0 / REDDIT_JSON_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch posts newer than cursor["last_created_utc"].

        Paginates through /new using Reddit's `after` token.  Stops when it
        encounters a post older than the cursor timestamp, or after MAX_PAGES.
        """
        last_utc: float = float(cursor.get("last_created_utc", 0.0))
        url = _REDDIT_NEW_URL.format(subreddit=TARGET_SUBREDDIT)

        collected: List[Dict[str, Any]] = []
        after: Optional[str] = None

        for page in range(_MAX_PAGES):
            params: Dict[str, Any] = {"limit": 100}
            if after:
                params["after"] = after

            self.log.debug(
                "Fetching page %d (after=%s)", page + 1, after
            )
            resp = self._session.get(url, params=params)
            if resp is None:
                self.log.warning("Request failed on page %d; stopping.", page + 1)
                break

            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            if not posts:
                self.log.info("No posts returned; pagination complete.")
                break

            stop_paging = False
            for child in posts:
                post = child.get("data", {})
                created_utc: float = float(post.get("created_utc", 0))

                if created_utc <= last_utc:
                    # Everything from here on is older than our cursor.
                    self.log.info(
                        "Hit cursor boundary at created_utc=%.0f; stopping.",
                        created_utc,
                    )
                    stop_paging = True
                    break

                collected.append(post)

            after = data.get("data", {}).get("after")
            if stop_paging or not after:
                break

        self.log.info(
            "Collected %d new posts (cursor_utc=%.0f)",
            len(collected),
            last_utc,
        )
        return collected

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return str(item["id"])

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        permalink = item.get("permalink", "")
        return f"https://www.reddit.com{permalink}" if permalink else None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        created_utc = item.get("created_utc")
        if created_utc is None:
            return None
        return datetime.fromtimestamp(
            float(created_utc), tz=timezone.utc
        ).isoformat()

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advance cursor to the newest post seen this run."""
        if not items:
            return prev_cursor

        newest_utc = max(float(item.get("created_utc", 0)) for item in items)
        return {"last_created_utc": newest_utc}
