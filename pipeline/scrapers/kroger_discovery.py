"""Kroger API product discovery scraper.

Searches Kroger's product catalog by food categories and major brands,
cataloging every product found into product_entities + pack_variants +
variant_observations.  Runs alongside kroger.py (which monitors known
UPCs for price/size changes).

Search terms and brands are configured in pipeline.config.
"""
from datetime import date
from typing import Any, Dict, List, Optional

from pipeline.config import (
    KROGER_API_BASE,
    KROGER_BRANDS,
    KROGER_DISCOVERY_MAX_REQUESTS,
    KROGER_SEARCH_TERMS,
    KROGER_STORE_IDS,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.kroger_auth import KrogerAuth
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.catalog_base import CatalogScraper

_KROGER_RPS = 2.0
_PAGE_SIZE = 50
_MAX_PAGES_PER_TERM = 10  # 500 products per search term max


class KrogerDiscoveryScraper(CatalogScraper):
    """Discover grocery products via Kroger Product API search."""

    scraper_name = "kroger_discovery"
    source_type = "kroger_api"
    catalog_source = "kroger_catalog"

    def __init__(self):
        # type: () -> None
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_KROGER_RPS,
            user_agent=USER_AGENT,
        )
        self._auth = KrogerAuth(self._session)
        self._today = date.today().isoformat()
        self._request_count = 0

    # ── CatalogScraper interface ────────────────────────────────────────────

    def extract_product(self, item):
        # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
        """Map Kroger product wrapper to catalog fields."""
        product = item.get("_product", {})
        brand = (product.get("brand") or "").strip()
        desc = (product.get("description") or "").strip()
        if not brand or not desc:
            return None

        upc = (product.get("upc") or "").strip()

        # Extract size from the first item in the items array
        size = None  # type: Optional[float]
        size_unit = None  # type: Optional[str]
        items_list = product.get("items", [])
        if items_list:
            first_item = items_list[0]
            size_text = first_item.get("size", "")
            if size_text:
                size, size_unit = parse_package_weight(size_text)

        # Category from aisles
        category = None  # type: Optional[str]
        aisles = product.get("aisles", [])
        if aisles:
            aisle = aisles[0]
            cat = aisle.get("description", "")
            if cat:
                category = cat

        # Image URL
        image_url = None  # type: Optional[str]
        images_list = product.get("images", [])
        if images_list:
            first_img = images_list[0]
            sizes = first_img.get("sizes", [])
            if sizes:
                image_url = sizes[0].get("url")

        return {
            "brand": brand,
            "name": desc,
            "category": category,
            "upc": upc,
            "size": size,
            "size_unit": size_unit,
            "variant_name": desc,
            "image_url": image_url,
        }

    # ── BaseScraper interface ───────────────────────────────────────────────

    def fetch(
        self, cursor, dry_run=False
    ):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Search Kroger by terms + brands and collect product data.

        Resumes from cursor if interrupted mid-term.  Stops at the
        configured max request limit.
        """
        all_terms = KROGER_SEARCH_TERMS + KROGER_BRANDS
        term_index = int(cursor.get("term_index", 0))
        start_offset = int(cursor.get("offset", 0))
        store_id = KROGER_STORE_IDS[0] if KROGER_STORE_IDS else ""

        items = []  # type: List[Dict[str, Any]]
        self._request_count = 0

        for t_idx in range(term_index, len(all_terms)):
            term = all_terms[t_idx]
            offset = start_offset if t_idx == term_index else 0

            self.log.info(
                "Kroger discovery: searching '%s' (offset %d)", term, offset,
            )
            term_count = 0
            page = 0

            while page < _MAX_PAGES_PER_TERM:
                if self._request_count >= KROGER_DISCOVERY_MAX_REQUESTS:
                    self.log.info(
                        "Hit request limit (%d); stopping discovery",
                        KROGER_DISCOVERY_MAX_REQUESTS,
                    )
                    return items

                products = self._search_products(term, store_id, offset)
                if not products:
                    break

                for product in products:
                    product_id = product.get("productId", "")
                    if not product_id:
                        continue
                    items.append({
                        "_product_id": product_id,
                        "_store_id": store_id,
                        "_term": term,
                        "_product": product,
                    })
                    term_count += 1

                offset += _PAGE_SIZE
                page += 1

            self.log.info(
                "Kroger discovery: '%s' yielded %d products", term, term_count,
            )

        self.log.info(
            "Collected %d total products (%d API requests)",
            len(items), self._request_count,
        )
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return "kroger_disc_{}".format(item["_product_id"])

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return None

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return self._today

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        return {
            "term_index": 0,
            "offset": 0,
            "last_run_products": len(items),
            "last_run_date": self._today,
        }

    # ── Private helpers ─────────────────────────────────────────────────────

    def _search_products(self, term, store_id, offset):
        # type: (str, str, int) -> List[Dict[str, Any]]
        """Search Kroger API for one page of products.  Returns empty on error."""
        token = self._auth.get_token()
        if token is None:
            return []

        url = "{}/products".format(KROGER_API_BASE)
        params = {
            "filter.term": term,
            "filter.limit": _PAGE_SIZE,
            "filter.start": offset + 1,  # Kroger uses 1-based offset
        }  # type: Dict[str, Any]
        if store_id:
            params["filter.locationId"] = store_id

        resp = self._session.get(
            url,
            params=params,
            headers={"Authorization": "Bearer {}".format(token)},
            raise_for_status=False,
        )
        self._request_count += 1

        # Re-authenticate on 401
        if resp is not None and resp.status_code == 401:
            self.log.info("Got 401; refreshing Kroger token")
            self._auth.invalidate()
            token = self._auth.get_token()
            if token is None:
                return []
            resp = self._session.get(
                url,
                params=params,
                headers={"Authorization": "Bearer {}".format(token)},
            )
            self._request_count += 1

        if resp is None or resp.status_code >= 400:
            self.log.warning(
                "Kroger search failed: term='%s' offset=%d status=%s",
                term, offset,
                resp.status_code if resp is not None else "None",
            )
            return []

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning(
                "JSON decode error for term='%s': %s", term, exc,
            )
            return []

        return data.get("data", [])
