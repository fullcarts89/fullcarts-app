"""Reddit recent-posts scraper.

Fetches new posts from r/shrinkflation via Arctic Shift (primary) with
Reddit's public JSON API as fallback.

Arctic Shift is an open archive of Reddit data — no credentials needed,
and it has near-real-time coverage. Reddit's public JSON API is used as
a fallback in case Arctic Shift is temporarily down or missing recent posts.
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import (
    ARCTIC_SHIFT_BASE,
    ARCTIC_SHIFT_DELAY,
    REDDIT_JSON_DELAY,
    TARGET_SUBREDDIT,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.scrapers.base import BaseScraper

_ARCTIC_SHIFT_SEARCH_URL = "{base}/posts/search"
_REDDIT_NEW_URL = "https://www.reddit.com/r/{subreddit}/new.json"

_ARCTIC_SHIFT_MAX_PAGES = 20
_REDDIT_MAX_PAGES = 10

# Minimum number of posts from Arctic Shift before we skip the Reddit fallback
_ARCTIC_SHIFT_MIN_THRESHOLD = 3


class RedditRecentScraper(BaseScraper):
    """Incrementally fetches new posts from r/shrinkflation.

    Strategy:
        1. Try Arctic Shift API first (reliable, no auth needed)
        2. Fall back to Reddit public JSON API if Arctic Shift
           returns fewer than _ARCTIC_SHIFT_MIN_THRESHOLD posts
    """

    scraper_name = "reddit_recent"
    source_type = "reddit"

    def __init__(self) -> None:
        super().__init__()
        self._arctic_session = RateLimitedSession(
            requests_per_second=1.0 / ARCTIC_SHIFT_DELAY,
            user_agent=USER_AGENT,
        )
        self._reddit_session = RateLimitedSession(
            requests_per_second=1.0 / REDDIT_JSON_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch posts newer than cursor["last_created_utc"].

        Tries Arctic Shift first, then falls back to Reddit JSON API
        if too few results come back.
        """
        last_utc: float = float(cursor.get("last_created_utc", 0.0))

        # 1. Primary: Arctic Shift
        self.log.info("Fetching from Arctic Shift (after_utc=%.0f)...", last_utc)
        collected = self._fetch_arctic_shift(last_utc)
        self.log.info(
            "Arctic Shift returned %d posts", len(collected)
        )

        # 2. Fallback: Reddit JSON API (if Arctic Shift returned too few)
        if len(collected) < _ARCTIC_SHIFT_MIN_THRESHOLD:
            self.log.info(
                "Arctic Shift returned only %d posts (threshold=%d), "
                "trying Reddit JSON fallback...",
                len(collected), _ARCTIC_SHIFT_MIN_THRESHOLD,
            )
            reddit_posts = self._fetch_reddit_json(last_utc)
            self.log.info(
                "Reddit JSON returned %d posts", len(reddit_posts)
            )
            collected.extend(reddit_posts)

        # Deduplicate by post ID
        seen_ids: Dict[str, bool] = {}
        unique: List[Dict[str, Any]] = []
        for post in collected:
            pid = post.get("id", "")
            if pid and pid not in seen_ids:
                seen_ids[pid] = True
                unique.append(post)

        self.log.info(
            "Collected %d unique new posts (cursor_utc=%.0f)",
            len(unique), last_utc,
        )
        return unique

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return str(item["id"])

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        permalink = item.get("permalink", "")
        return "https://www.reddit.com%s" % permalink if permalink else None

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

    # ── Arctic Shift ───────────────────────────────────────────────────────

    def _fetch_arctic_shift(self, after_utc: float) -> List[Dict[str, Any]]:
        """Paginate through Arctic Shift API for posts newer than after_utc.

        Arctic Shift returns posts in a flat `data` array, sorted by
        created_utc descending. We paginate using the `before` parameter
        set to the oldest post's timestamp from the previous batch.
        """
        url = _ARCTIC_SHIFT_SEARCH_URL.format(base=ARCTIC_SHIFT_BASE)
        collected: List[Dict[str, Any]] = []
        before_utc: Optional[int] = None

        for page in range(_ARCTIC_SHIFT_MAX_PAGES):
            params: Dict[str, Any] = {
                "subreddit": TARGET_SUBREDDIT,
                "limit": 100,
                "sort": "desc",
            }
            if after_utc > 0:
                params["after"] = int(after_utc)
            if before_utc is not None:
                params["before"] = before_utc

            self.log.debug(
                "Arctic Shift page %d (before=%s, after=%.0f)",
                page + 1, before_utc, after_utc,
            )

            resp = self._arctic_session.get(url, params=params)
            if resp is None:
                self.log.warning(
                    "Arctic Shift request failed on page %d; stopping.",
                    page + 1,
                )
                break

            try:
                posts = resp.json().get("data", [])
            except Exception as exc:
                self.log.warning(
                    "Arctic Shift JSON parse failed: %s", exc
                )
                break

            if not posts:
                self.log.debug("Arctic Shift: no more posts after page %d", page + 1)
                break

            collected.extend(posts)

            # Paginate backwards: set before to the oldest post in this batch
            oldest_ts = min(int(p.get("created_utc", 0)) for p in posts)
            before_utc = oldest_ts

            if len(posts) < 100:
                # Last page — fewer than requested means we've seen everything
                break

        return collected

    # ── Reddit JSON fallback ───────────────────────────────────────────────

    def _fetch_reddit_json(self, after_utc: float) -> List[Dict[str, Any]]:
        """Fetch recent posts from Reddit's public JSON API.

        Uses /new listing with Reddit's `after` token pagination.
        Stops when posts are older than after_utc or after MAX_PAGES.
        """
        url = _REDDIT_NEW_URL.format(subreddit=TARGET_SUBREDDIT)
        collected: List[Dict[str, Any]] = []
        after_token: Optional[str] = None

        for page in range(_REDDIT_MAX_PAGES):
            params: Dict[str, Any] = {"limit": 100}
            if after_token:
                params["after"] = after_token

            self.log.debug(
                "Reddit JSON page %d (after=%s)", page + 1, after_token
            )
            resp = self._reddit_session.get(url, params=params)
            if resp is None:
                self.log.warning(
                    "Reddit JSON request failed on page %d; stopping.",
                    page + 1,
                )
                break

            data = resp.json()
            posts = data.get("data", {}).get("children", [])
            if not posts:
                self.log.info("Reddit JSON: no posts returned; done.")
                break

            stop_paging = False
            for child in posts:
                post = child.get("data", {})
                created_utc = float(post.get("created_utc", 0))

                if created_utc <= after_utc:
                    self.log.info(
                        "Reddit JSON: hit cursor boundary at %.0f; stopping.",
                        created_utc,
                    )
                    stop_paging = True
                    break

                collected.append(post)

            after_token = data.get("data", {}).get("after")
            if stop_paging or not after_token:
                break

        return collected
