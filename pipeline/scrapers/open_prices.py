"""Open Prices scraper.

Fetches recent grocery price data from the Open Prices API
(prices.openfoodfacts.org) — a crowdsourced receipt-level price database
run by Open Food Facts.

Strategy:
  - Focus on USD prices (US market) of type PRODUCT (barcode-level, not
    category-level entries).
  - Paginate newest-first by created timestamp, stopping when we reach
    the previous cursor boundary.
  - On first run, backfill the last 30 days.
  - Cap at _MAX_PAGES per run (~5,000 items) to stay within rate limits.
  - Stores raw JSON in raw_items (BaseScraper default) AND upserts
    structured rows into open_prices_data for direct querying.
"""
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pipeline.config import (
    OPEN_PRICES_API_BASE,
    OPEN_PRICES_DELAY,
    OPEN_PRICES_PAGE_SIZE,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.supabase_client import get_client
from pipeline.scrapers.base import BaseScraper

_PRICES_URL = "{base}/prices"
_MAX_PAGES = 50  # 50 pages × 100 items = 5,000 items max per run


class OpenPricesScraper(BaseScraper):
    """Incrementally fetches US grocery price data from Open Prices.

    Cursor format: {"last_created": "<ISO 8601 timestamp>"}

    The cursor tracks the newest `created` timestamp seen on the previous
    run.  Each run fetches pages ordered by `-created` until it finds an
    item whose `created` value is at or before the cursor.
    """

    scraper_name = "open_prices"
    source_type = "open_prices"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=1.0 / OPEN_PRICES_DELAY,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch price records submitted after cursor["last_created"].

        Pages through the Open Prices API newest-first, collecting items
        until we hit an entry that is at or before the previous cursor
        boundary (or exhaust _MAX_PAGES pages).
        """
        # Default first-run boundary: 30 days ago
        default_start = (
            datetime.now(timezone.utc) - timedelta(days=30)
        ).isoformat()
        last_created: str = cursor.get("last_created", default_start)

        url = _PRICES_URL.format(base=OPEN_PRICES_API_BASE)
        collected: List[Dict[str, Any]] = []

        for page in range(1, _MAX_PAGES + 1):
            params: Dict[str, Any] = {
                "currency": "USD",
                "type": "PRODUCT",
                "order_by": "-created",
                "page": page,
                "size": OPEN_PRICES_PAGE_SIZE,
            }

            self.log.debug(
                "Open Prices page %d (last_created=%s)", page, last_created
            )

            resp = self._session.get(url, params=params)
            if resp is None:
                self.log.warning(
                    "Open Prices request failed on page %d; stopping.", page
                )
                break

            try:
                data = resp.json()
            except Exception as exc:
                self.log.warning("Open Prices JSON parse error: %s", exc)
                break

            items = data.get("items", [])
            if not items:
                self.log.info(
                    "Open Prices: no items on page %d; done.", page
                )
                break

            stop_paging = False
            for item in items:
                item_created = item.get("created", "")

                # Stop when we reach items we've already processed
                if item_created and item_created <= last_created:
                    self.log.info(
                        "Open Prices: reached cursor boundary "
                        "(%s <= %s); stopping.",
                        item_created, last_created,
                    )
                    stop_paging = True
                    break

                # Skip records without a barcode or price (category entries,
                # incomplete submissions, etc.)
                if not item.get("product_code") or item.get("price") is None:
                    continue

                collected.append(item)

            total_pages = data.get("pages", 1)
            if stop_paging or page >= total_pages:
                break

        self.log.info(
            "Open Prices: collected %d new price records", len(collected)
        )
        return collected

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return str(item["id"])

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        price_id = item.get("id")
        if not price_id:
            return None
        return "https://prices.openfoodfacts.org/prices/%s" % price_id

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return item.get("created")

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Advance cursor to the newest created timestamp seen this run."""
        if not items:
            return prev_cursor

        newest = max(
            (item.get("created", "") for item in items),
            default="",
        )
        if newest:
            return {"last_created": newest}
        return prev_cursor

    # ── Structured storage ─────────────────────────────────────────────────

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Store items in raw_items (via super) and open_prices_data."""
        stored = super().store(items)
        self._upsert_structured(items)
        return stored

    def _upsert_structured(self, items: List[Dict[str, Any]]) -> None:
        """Upsert structured rows into open_prices_data for direct querying.

        Extracts well-known fields from each raw price object so that
        downstream queries don't need to unpack JSONB.
        """
        if not items:
            return

        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        batch_size = 50
        total_upserted = 0

        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            rows = []
            for item in batch:
                location = item.get("location") or {}
                proof = item.get("proof") or {}
                row = {
                    "open_price_id": item["id"],
                    "product_code": item.get("product_code"),
                    "product_name": item.get("product_name"),
                    "price": item.get("price"),
                    "currency": item.get("currency"),
                    "price_date": item.get("date"),
                    "price_per": item.get("price_per"),
                    "price_is_discounted": item.get(
                        "price_is_discounted", False
                    ),
                    "price_without_discount": item.get(
                        "price_without_discount"
                    ),
                    "discount_type": item.get("discount_type"),
                    "location_osm_id": item.get("location_osm_id"),
                    "location_osm_type": item.get("location_osm_type"),
                    "location_name": location.get("osm_name"),
                    "location_city": location.get("osm_address_city"),
                    "location_country": location.get("osm_address_country"),
                    "location_country_code": location.get(
                        "osm_address_country_code"
                    ),
                    "source_url": self.source_url_for(item),
                    "proof_type": proof.get("type"),
                    "raw_payload": item,
                    "price_submitted_at": item.get("created"),
                    "scraped_at": now,
                }
                rows.append(row)

            try:
                resp = (
                    client.table("open_prices_data")
                    .upsert(rows, on_conflict="open_price_id")
                    .execute()
                )
                if resp and resp.data:
                    total_upserted += len(resp.data)
            except Exception as exc:
                self.log.warning(
                    "open_prices_data upsert failed for batch %d: %s",
                    i // batch_size,
                    exc,
                )

        self.log.info(
            "open_prices_data: upserted %d rows", total_upserted
        )
