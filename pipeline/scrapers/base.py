"""Abstract base scraper — every concrete scraper inherits this.

The lifecycle is:
    load cursor → fetch → store → update cursor → write summary
"""
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import SCRAPER_VERSION
from pipeline.lib.cursor import load_cursor, save_cursor
from pipeline.lib.hashing import content_hash
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.lib.github_summary import write_summary


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

        Automatically recycles the Supabase HTTP/2 connection every
        _RECYCLE_EVERY batches to avoid stream-limit termination on
        large jobs (e.g. USDA backfill with 500K+ rows).
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

            try:
                resp = (
                    client.table("raw_items")
                    .upsert(rows, on_conflict="source_type,source_id")
                    .execute()
                )
            except Exception as exc:
                if "RemoteProtocolError" in type(exc).__name__ or \
                   "ConnectionTerminated" in str(exc):
                    self.log.warning(
                        "Connection terminated at batch %d; recycling and retrying",
                        batch_num,
                    )
                    reset_client()
                    client = get_client()
                    resp = (
                        client.table("raw_items")
                        .upsert(rows, on_conflict="source_type,source_id")
                        .execute()
                    )
                else:
                    raise

            # Count rows that were actually inserted (not conflict-skipped)
            if resp.data:
                total_new += len(resp.data)

            self.log.debug(
                "Batch %d-%d: upserted %d rows",
                i, i + len(batch),
                len(resp.data) if resp.data else 0,
            )

        return total_new

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
