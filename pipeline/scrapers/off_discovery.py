"""Open Food Facts category-based product discovery scraper.

Browses focused food categories on OFF and stores every US product
found into raw_items for later extraction.  Runs alongside off_daily
(which monitors known UPCs); this scraper casts a wider net.

Categories are configured in pipeline.config.OFF_CATEGORIES.
"""
from typing import Any, Dict, List, Optional

from pipeline.config import (
    OFF_CATEGORIES,
    OFF_DELAY,
    OFF_SEARCH_URL,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.logging_setup import get_logger
from pipeline.scrapers.base import BaseScraper

_OFF_RPS = 1.0 / OFF_DELAY  # ~1.67 req/s
_PAGE_SIZE = 100
_MAX_PAGES_PER_CATEGORY = 50  # Safety cap: 5K products per category

_FIELDS = (
    "code,product_name,brands,quantity,product_quantity,"
    "product_quantity_unit,categories,image_url,countries_tags"
)


class OffDiscoveryScraper(BaseScraper):
    """Discover US food products on Open Food Facts by category."""

    scraper_name = "off_discovery"
    source_type = "openfoodfacts"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_OFF_RPS,
            user_agent=USER_AGENT,
        )

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Browse OFF categories and collect product data.

        Returns a list of product dicts.  Resumes from cursor if interrupted.
        """
        category_index = int(cursor.get("category_index", 0))
        start_page = int(cursor.get("page", 1))
        items: List[Dict[str, Any]] = []

        for cat_idx in range(category_index, len(OFF_CATEGORIES)):
            category = OFF_CATEGORIES[cat_idx]
            page = start_page if cat_idx == category_index else 1

            self.log.info(
                "OFF discovery: browsing category '%s' (starting page %d)",
                category, page,
            )
            cat_count = 0

            while page <= _MAX_PAGES_PER_CATEGORY:
                products = self._fetch_page(category, page)
                if not products:
                    break

                # Filter out products without barcodes
                valid = [
                    p for p in products
                    if p.get("code") and p["code"] not in ("", "0")
                ]
                items.extend(valid)
                cat_count += len(valid)
                page += 1

            self.log.info(
                "OFF discovery: category '%s' yielded %d products",
                category, cat_count,
            )

        self.log.info(
            "Collected %d total products across %d categories",
            len(items),
            len(OFF_CATEGORIES) - category_index,
        )
        return items

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return "off_disc_{}".format(item["code"])

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        code = item.get("code", "")
        if code:
            return "https://world.openfoodfacts.org/product/{}".format(code)
        return None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        from datetime import date
        return date.today().isoformat()

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Reset to beginning so the next run re-crawls all categories
        # (products are deduped by source_id on upsert, so re-crawling
        # is safe and catches new/updated products)
        return {
            "category_index": 0,
            "page": 1,
            "last_run_products": len(items),
        }

    # ── Private helpers ────────────────────────────────────────────────────

    def _fetch_page(
        self, category: str, page: int
    ) -> List[Dict[str, Any]]:
        """Fetch one page of products for a category.  Returns empty on error."""
        params: Dict[str, Any] = {
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": _PAGE_SIZE,
            "page": page,
            "tagtype_0": "categories",
            "tag_contains_0": "contains",
            "tag_0": category,
            "tagtype_1": "countries",
            "tag_contains_1": "contains",
            "tag_1": "United States",
            "fields": _FIELDS,
        }

        resp = self._session.get(OFF_SEARCH_URL, params=params)
        if resp is None:
            return []

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning(
                "OFF search JSON decode error for category=%s page=%d: %s",
                category, page, exc,
            )
            return []

        return data.get("products", [])
