"""Reddit historical backfill scraper via Arctic Shift.

Uses the Arctic Shift public API to paginate backward through all posts in
r/shrinkflation.  Writes to the same raw_items table as reddit_recent; the
(source_type, source_id) UNIQUE constraint deduplicates automatically.
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import (
    ARCTIC_SHIFT_BASE,
    ARCTIC_SHIFT_DELAY,
    TARGET_SUBREDDIT,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

_SEARCH_URL = f"{ARCTIC_SHIFT_BASE}/posts/search"
_BATCH_SIZE = 100
_MAX_BATCHES = 500  # 50,000 posts max per run


class RedditBackfillScraper(BaseScraper):
    """Paginates backward through r/shrinkflation history via Arctic Shift."""

    scraper_name = "reddit_backfill"
    source_type = "reddit"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=1.0 / ARCTIC_SHIFT_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch posts from Arctic Shift, paging backward through history.

        Resumes from cursor["before_utc"] if present.  Stops when the API
        returns an empty batch or after MAX_BATCHES iterations.
        """
        before_utc: Optional[int] = cursor.get("before_utc")
        total_fetched_so_far: int = int(cursor.get("total_fetched", 0))

        collected: List[Dict[str, Any]] = []

        for batch_num in range(_MAX_BATCHES):
            params: Dict[str, Any] = {
                "subreddit": TARGET_SUBREDDIT,
                "limit": _BATCH_SIZE,
            }
            if before_utc is not None:
                params["before"] = before_utc

            self.log.debug(
                "Fetching batch %d (before_utc=%s)", batch_num + 1, before_utc
            )
            resp = self._session.get(_SEARCH_URL, params=params)
            if resp is None:
                self.log.warning(
                    "Request failed on batch %d; stopping.", batch_num + 1
                )
                break

            data = resp.json()
            posts = data.get("data", [])
            if not posts:
                self.log.info(
                    "Arctic Shift returned empty batch; backfill complete."
                )
                break

            collected.extend(posts)

            # Advance the before cursor to the oldest post in this batch.
            oldest_utc = min(
                int(p.get("created_utc", 0)) for p in posts
            )
            before_utc = oldest_utc

            self.log.debug(
                "Batch %d: got %d posts; oldest created_utc=%d",
                batch_num + 1,
                len(posts),
                oldest_utc,
            )

            # If we got fewer than requested, we've hit the beginning.
            if len(posts) < _BATCH_SIZE:
                self.log.info("Partial batch received; backfill complete.")
                break

        self.log.info(
            "Collected %d posts (total_fetched_cumulative=%d)",
            len(collected),
            total_fetched_so_far + len(collected),
        )
        return collected

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return str(item["id"])

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        post_id = item.get("id", "")
        if not post_id:
            return None
        return (
            f"https://www.reddit.com/r/{TARGET_SUBREDDIT}/comments/{post_id}"
        )

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
        """Advance cursor to continue from the oldest post seen this run."""
        prev_total: int = int(prev_cursor.get("total_fetched", 0))
        new_total: int = prev_total + len(items)

        if not items:
            return {**prev_cursor, "total_fetched": new_total}

        oldest_utc = min(int(item.get("created_utc", 0)) for item in items)
        return {
            "before_utc": oldest_utc,
            "total_fetched": new_total,
        }
