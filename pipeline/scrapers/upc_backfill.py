"""UPC backfill scraper.

Finds all barcodes in the pipeline database that haven't been resolved yet
and runs them through the UPC resolution chain (UPCitemdb → Brocade →
Open Food Facts), caching every result in ``upc_cache``.

Sources scanned for unresolved barcodes:
  - open_prices_data.product_code  (crowdsourced price scan data)
  - usda_products.gtin_upc         (USDA branded food database)

This is a one-time backfill plus weekly incremental run — barcodes don't
change once cached, so the weekly job only picks up genuinely new barcodes
not already in upc_cache.

Usage:
    python -m pipeline upc_backfill [--dry-run]

Python 3.9 compatible — uses typing module, no X | Y union syntax.
"""
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client
from pipeline.lib.upc_resolver import UpcResolver

log = get_logger("upc_backfill")

# Maximum barcodes to resolve per run (daily UPCitemdb limit is 100, but
# Brocade and OFF have no meaningful limit so we can resolve far more).
_MAX_BARCODES_PER_RUN = 5000

# Batch size for fetching unresolved barcodes from Supabase
_FETCH_BATCH_SIZE = 1000

# Batch size for resolve_batch calls (small to avoid long pauses)
_RESOLVE_BATCH_SIZE = 10


class UpcBackfillScraper:
    """Resolves and caches all unresolved barcodes found across pipeline tables.

    Not a BaseScraper subclass — it doesn't write to raw_items and has no
    meaningful cursor (it simply processes whatever isn't in upc_cache yet).
    The CLI interface (run method) matches what pipeline/cli.py expects.
    """

    scraper_name = "upc_backfill"

    def __init__(self) -> None:
        self.log = log

    # ── CLI entry point ───────────────────────────────────────────────────

    def run(self, dry_run: bool = False) -> None:
        """Find and resolve all uncached barcodes."""
        self.log.info("Starting upc_backfill (dry_run=%s)", dry_run)
        start = datetime.now(timezone.utc)

        barcodes = self._collect_unresolved_barcodes()
        self.log.info("Found %d unresolved barcodes", len(barcodes))

        if not barcodes:
            self.log.info("Nothing to do — all barcodes already cached.")
            return

        if len(barcodes) > _MAX_BARCODES_PER_RUN:
            self.log.info(
                "Capping at %d barcodes for this run (%d total unresolved)",
                _MAX_BARCODES_PER_RUN,
                len(barcodes),
            )
            barcodes = barcodes[:_MAX_BARCODES_PER_RUN]

        if dry_run:
            self.log.info(
                "Dry run — would resolve %d barcodes. First 10: %s",
                len(barcodes),
                barcodes[:10],
            )
            return

        resolver = UpcResolver()
        resolved = 0
        missed = 0
        errors = 0

        for i in range(0, len(barcodes), _RESOLVE_BATCH_SIZE):
            batch = barcodes[i : i + _RESOLVE_BATCH_SIZE]
            try:
                results = resolver.resolve_batch(batch)
                for barcode, product in results.items():
                    if product is not None:
                        resolved += 1
                        self.log.debug(
                            "Resolved %s → %s (%s)",
                            barcode,
                            product.get("product_name", "?"),
                            product.get("source", "?"),
                        )
                    else:
                        missed += 1
            except Exception as exc:
                self.log.warning(
                    "Batch resolve failed for %s: %s", batch, exc
                )
                errors += len(batch)

            progress_pct = min(
                100, int((i + len(batch)) / len(barcodes) * 100)
            )
            if (i // _RESOLVE_BATCH_SIZE) % 10 == 0:
                self.log.info(
                    "Progress: %d%% (%d/%d) — %d resolved, %d not found, %d errors",
                    progress_pct,
                    i + len(batch),
                    len(barcodes),
                    resolved,
                    missed,
                    errors,
                )

        elapsed = (datetime.now(timezone.utc) - start).total_seconds()
        self.log.info(
            "upc_backfill complete in %.1fs: %d resolved, %d not found, %d errors",
            elapsed,
            resolved,
            missed,
            errors,
        )

    # ── Barcode discovery ─────────────────────────────────────────────────

    def _collect_unresolved_barcodes(self) -> List[str]:
        """Gather all barcodes not yet in upc_cache, across all sources."""
        all_barcodes: set = set()

        open_prices = self._fetch_open_prices_barcodes()
        self.log.info(
            "open_prices_data: %d unresolved barcodes", len(open_prices)
        )
        all_barcodes.update(open_prices)

        usda = self._fetch_usda_barcodes()
        self.log.info("usda_products: %d unresolved barcodes", len(usda))
        all_barcodes.update(usda)

        return list(all_barcodes)

    def _fetch_open_prices_barcodes(self) -> List[str]:
        """Fetch distinct barcodes from open_prices_data not yet cached."""
        barcodes: List[str] = []
        try:
            client = get_client()
            # Fetch distinct product_codes from open_prices_data in batches,
            # then filter out those already in upc_cache client-side.
            # (PostgREST doesn't support NOT IN subqueries directly.)
            offset = 0
            seen: set = set()
            while True:
                resp = (
                    client.table("open_prices_data")
                    .select("product_code")
                    .not_.is_("product_code", "null")
                    .range(offset, offset + _FETCH_BATCH_SIZE - 1)
                    .execute()
                )
                if not resp or not resp.data:
                    break
                for row in resp.data:
                    code = row.get("product_code")
                    if code and code not in seen:
                        seen.add(code)
                        barcodes.append(code)
                if len(resp.data) < _FETCH_BATCH_SIZE:
                    break
                offset += _FETCH_BATCH_SIZE

            barcodes = self._filter_uncached(barcodes)
        except Exception as exc:
            self.log.warning(
                "Failed to fetch open_prices_data barcodes: %s", exc
            )
        return barcodes

    def _fetch_usda_barcodes(self) -> List[str]:
        """Fetch distinct barcodes from usda_products not yet cached."""
        barcodes: List[str] = []
        try:
            client = get_client()
            offset = 0
            seen: set = set()
            while True:
                resp = (
                    client.table("usda_products")
                    .select("gtin_upc")
                    .not_.is_("gtin_upc", "null")
                    .range(offset, offset + _FETCH_BATCH_SIZE - 1)
                    .execute()
                )
                if not resp or not resp.data:
                    break
                for row in resp.data:
                    upc = row.get("gtin_upc")
                    if upc and upc not in seen:
                        seen.add(upc)
                        barcodes.append(upc)
                if len(resp.data) < _FETCH_BATCH_SIZE:
                    break
                offset += _FETCH_BATCH_SIZE

            barcodes = self._filter_uncached(barcodes)
        except Exception as exc:
            self.log.warning("Failed to fetch usda_products barcodes: %s", exc)
        return barcodes

    def _filter_uncached(self, barcodes: List[str]) -> List[str]:
        """Remove barcodes that already have a upc_cache row (hit or miss)."""
        if not barcodes:
            return []

        cached: set = set()
        try:
            client = get_client()
            # Fetch in chunks of 500 (PostgREST IN clause limit)
            chunk_size = 500
            for i in range(0, len(barcodes), chunk_size):
                chunk = barcodes[i : i + chunk_size]
                resp = (
                    client.table("upc_cache")
                    .select("barcode")
                    .in_("barcode", chunk)
                    .execute()
                )
                if resp and resp.data:
                    for row in resp.data:
                        cached.add(row["barcode"])
        except Exception as exc:
            self.log.warning("Cache filter query failed: %s", exc)

        return [b for b in barcodes if b not in cached]
