"""Abstract base scraper — every concrete scraper inherits this.

The lifecycle is:
    load cursor → fetch → store → update cursor → write summary
"""
import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import SCRAPER_VERSION
from pipeline.lib.cursor import load_cursor, save_cursor
from pipeline.lib.hashing import content_hash
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.lib.github_summary import write_summary

# Retry config for transient Supabase errors (502, 503, connection drops)
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 5  # seconds — exponential backoff: 5, 10, 20


class BaseScraper(ABC):
    """Base class for all pipeline scrapers.

    Subclasses must define:
        scraper_name  — identifier stored in scraper_state
        source_type   — must match raw_items CHECK constraint
    and implement:
        fetch()       — collect raw data from external source
        source_id_for() — extract the unique source ID from one item
        next_cursor() — compute cursor for the next run
    """

    scraper_name: str
    source_type: str

    def __init__(self) -> None:
        self.log = get_logger(self.scraper_name)

    # ── Public entry point ────────────────────────────────────────────────

    def run(self, dry_run: bool = False) -> None:
        """Full lifecycle: load cursor → fetch → store → update cursor."""
        self.log.info(
            "Starting %s (dry_run=%s)", self.scraper_name, dry_run
        )

        cursor = load_cursor(self.scraper_name) if not dry_run else {}
        self.log.info("Loaded cursor: %s", cursor)

        items = self.fetch(cursor, dry_run=dry_run)
        self.log.info("Fetched %d items", len(items))

        stored = 0
        if not dry_run and items:
            stored = self.store(items)
            new_cursor = self.next_cursor(items, cursor)
            save_cursor(
                self.scraper_name,
                new_cursor,
                status="success",
                items_processed=stored,
            )
        elif dry_run and items:
            self.log.info("[DRY RUN] Would store %d items", len(items))

        self._write_summary(items, stored, dry_run)
        self.log.info(
            "Done: fetched=%d stored=%d", len(items), stored
        )

    # ── Abstract methods (subclass must implement) ────────────────────────

    @abstractmethod
    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch raw data from the external source.

        Returns a list of raw payloads (dicts).
        """

    @abstractmethod
    def source_id_for(self, item: Dict[str, Any]) -> str:
        """Extract the unique source identifier from one raw payload."""

    @abstractmethod
    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compute the cursor for the next run."""

    # ── Optional overrides ────────────────────────────────────────────────

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract source URL from a raw payload.  Override per scraper."""
        return None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        """Extract source date as ISO string.  Override per scraper."""
        return None

    # ── Default store implementation ──────────────────────────────────────

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Batch upsert items to raw_items.

        Uses ON CONFLICT (source_type, source_id) DO NOTHING for
        idempotent, deduplicated writes.  Returns count of new rows.

        Resilience features:
        - Recycles HTTP/2 connection every _RECYCLE_EVERY batches
        - Retries with exponential backoff on 502/503/connection errors
        """
        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        total_new = 0
        batch_size = 50
        _RECYCLE_EVERY = 4000  # ~200K rows — safely under HTTP/2 10K stream limit

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            rows = []
            for item in batch:
                rows.append({
                    "source_type": self.source_type,
                    "source_id": self.source_id_for(item),
                    "source_url": self.source_url_for(item),
                    "captured_at": now,
                    "source_date": self.source_date_for(item),
                    "raw_payload": item,
                    "content_hash": content_hash(item),
                    "scraper_version": SCRAPER_VERSION,
                })

            batch_num = i // batch_size

            # Recycle connection periodically to avoid HTTP/2 stream limits
            if batch_num > 0 and batch_num % _RECYCLE_EVERY == 0:
                reset_client()
                client = get_client()
                self.log.info(
                    "Recycled Supabase connection at batch %d (%d items)",
                    batch_num, i,
                )

            resp = self._upsert_with_retry(client, rows, batch_num)
            if resp is None:
                # _upsert_with_retry returns None only if it had to
                # reset the client; re-acquire for subsequent batches
                client = get_client()
                resp = self._upsert_with_retry(client, rows, batch_num)

            # Count rows that were actually inserted (not conflict-skipped)
            if resp and resp.data:
                total_new += len(resp.data)

            self.log.debug(
                "Batch %d-%d: upserted %d rows",
                i, i + len(batch),
                len(resp.data) if resp and resp.data else 0,
            )

        return total_new

    def _upsert_with_retry(self, client, rows, batch_num):
        """Attempt upsert with retries on transient errors.

        Handles HTTP/2 connection drops, 502/503 gateway errors,
        and other transient Supabase failures with exponential backoff.
        """
        for attempt in range(_MAX_RETRIES):
            try:
                return (
                    client.table("raw_items")
                    .upsert(rows, on_conflict="source_type,source_id")
                    .execute()
                )
            except Exception as exc:
                exc_name = type(exc).__name__
                exc_str = str(exc)
                is_transient = (
                    "RemoteProtocolError" in exc_name
                    or "ConnectionTerminated" in exc_str
                    or "502" in exc_str
                    or "503" in exc_str
                    or "Bad gateway" in exc_str
                    or "Service Unavailable" in exc_str
                )

                if not is_transient:
                    raise

                delay = _RETRY_BASE_DELAY * (2 ** attempt)
                self.log.warning(
                    "Transient error at batch %d (attempt %d/%d): %s. "
                    "Retrying in %ds...",
                    batch_num, attempt + 1, _MAX_RETRIES,
                    exc_name, delay,
                )
                time.sleep(delay)
                reset_client()
                client = get_client()

        # Final attempt — let it raise if it fails
        return (
            client.table("raw_items")
            .upsert(rows, on_conflict="source_type,source_id")
            .execute()
        )

    # ── Summary ───────────────────────────────────────────────────────────

    def _write_summary(
        self, items: List[Dict[str, Any]], stored: int, dry_run: bool
    ) -> None:
        """Write a summary for GitHub Actions and logging."""
        mode = "DRY RUN" if dry_run else "LIVE"
        stats = {
            "Mode": mode,
            "Items fetched": len(items),
            "Items stored": stored,
            "Source type": self.source_type,
        }

        # Build preview rows (first 10 items)
        preview_rows = []
        for item in items[:10]:
            preview_rows.append({
                "source_id": self.source_id_for(item),
                "source_url": (self.source_url_for(item) or "")[:80],
            })

        write_summary(
            title=f"Pipeline: {self.scraper_name}",
            rows=preview_rows,
            stats=stats,
        )
