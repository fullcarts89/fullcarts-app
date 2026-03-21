"""Open Food Facts category-based product discovery scraper.

Browses focused food categories on OFF and catalogs every US product
found into product_entities + pack_variants + variant_observations.
Runs alongside off_daily (which monitors known UPCs for price/size changes);
this scraper casts a wider net to build the product catalog.

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
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.catalog_base import CatalogScraper

_OFF_RPS = 1.0 / OFF_DELAY  # ~1.67 req/s
_PAGE_SIZE = 100
_MAX_PAGES_PER_CATEGORY = 50  # Safety cap: 5K products per category

_FIELDS = (
    "code,product_name,brands,quantity,product_quantity,"
    "product_quantity_unit,categories,image_url,countries_tags"
)


class OffDiscoveryScraper(CatalogScraper):
    """Discover US food products on Open Food Facts by category."""

    scraper_name = "off_discovery"
    source_type = "openfoodfacts"
    catalog_source = "off_catalog"

    def __init__(self):
        # type: () -> None
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_OFF_RPS,
            user_agent=USER_AGENT,
        )

    # ── CatalogScraper interface ────────────────────────────────────────────

    def extract_product(self, item):
        # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
        """Map OFF product dict to catalog fields."""
        brand = (item.get("brands") or "").strip()
        name = (item.get("product_name") or "").strip()
        if not brand or not name:
            return None

        # Parse size from OFF quantity fields
        size = None  # type: Optional[float]
        size_unit = None  # type: Optional[str]

        # Try numeric fields first
        pq = item.get("product_quantity")
        pqu = item.get("product_quantity_unit", "")
        if pq is not None:
            try:
                size = float(pq)
                size_unit = pqu or "g"
            except (ValueError, TypeError):
                pass

        # Fall back to free-text "quantity" field
        if size is None:
            qty_text = item.get("quantity", "")
            if qty_text:
                size, size_unit = parse_package_weight(qty_text)

        categories = item.get("categories", "")
        # Take first category as the main category
        category = None  # type: Optional[str]
        if categories:
            first = categories.split(",")[0].strip()
            if first:
                category = first

        return {
            "brand": brand,
            "name": name,
            "category": category,
            "upc": item.get("code", ""),
            "size": size,
            "size_unit": size_unit,
            "variant_name": name,
            "image_url": item.get("image_url"),
        }

    # ── BaseScraper interface ───────────────────────────────────────────────

    def fetch(
        self, cursor, dry_run=False
    ):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Browse OFF categories and collect product data.

        Returns a list of product dicts.  Resumes from cursor if interrupted.
        """
        category_index = int(cursor.get("category_index", 0))
        start_page = int(cursor.get("page", 1))
        items = []  # type: List[Dict[str, Any]]

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

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return "off_disc_{}".format(item["code"])

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        code = item.get("code", "")
        if code:
            return "https://world.openfoodfacts.org/product/{}".format(code)
        return None

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        from datetime import date
        return date.today().isoformat()

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        return {
            "category_index": 0,
            "page": 1,
            "last_run_products": len(items),
        }

    # ── Private helpers ─────────────────────────────────────────────────────

    def _fetch_page(self, category, page):
        # type: (str, int) -> List[Dict[str, Any]]
        """Fetch one page of products for a category.  Returns empty on error."""
        params = {
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
        }  # type: Dict[str, Any]

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
