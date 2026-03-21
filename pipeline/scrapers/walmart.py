"""Walmart Affiliate API product discovery scraper.

Searches Walmart's product catalog by food categories, cataloging every
product found into product_entities + pack_variants + variant_observations.

Uses the Walmart Affiliate Product API v2 with RSA-SHA256 signature auth.

Usage:
    python -m pipeline walmart        # live run
    python -m pipeline walmart --dry-run
"""
from datetime import date
from typing import Any, Dict, List, Optional

from pipeline.config import (
    WALMART_API_BASE,
    WALMART_DISCOVERY_MAX_REQUESTS,
    WALMART_SEARCH_TERMS,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.units import parse_package_weight
from pipeline.lib.walmart_auth import get_auth_headers
from pipeline.scrapers.catalog_base import CatalogScraper

# Walmart Affiliate API rate limit: 5 calls/second for search
_WALMART_RPS = 4.0  # stay under the 5/s limit
_PAGE_SIZE = 25  # Walmart API max per page for search
_MAX_PAGES_PER_TERM = 10  # 250 products per search term max


class WalmartDiscoveryScraper(CatalogScraper):
    """Discover grocery products via Walmart Affiliate API search."""

    scraper_name = "walmart_discovery"
    source_type = "walmart"
    catalog_source = "walmart_catalog"

    def __init__(self):
        # type: () -> None
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_WALMART_RPS,
            user_agent=USER_AGENT,
        )
        self._today = date.today().isoformat()
        self._request_count = 0

    # ── CatalogScraper interface ────────────────────────────────────────────

    def extract_product(self, item):
        # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
        """Map Walmart product wrapper to catalog fields."""
        product = item.get("_product", {})
        name = (product.get("name") or "").strip()
        brand = (product.get("brandName") or "").strip()
        if not brand or not name:
            return None

        upc = (product.get("upc") or "").strip()

        # Parse size from product name or specific fields
        size = None  # type: Optional[float]
        size_unit = None  # type: Optional[str]
        size_text = product.get("size", "")
        if size_text:
            size, size_unit = parse_package_weight(size_text)
        if size is None:
            # Try parsing from product name as fallback
            size, size_unit = parse_package_weight(name)

        category = (product.get("categoryPath") or "").strip() or None
        image_url = product.get("largeImage") or product.get("mediumImage")

        return {
            "brand": brand,
            "name": name,
            "category": category,
            "upc": upc,
            "size": size,
            "size_unit": size_unit,
            "variant_name": name,
            "image_url": image_url,
        }

    # ── BaseScraper interface ───────────────────────────────────────────────

    def fetch(
        self, cursor, dry_run=False
    ):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Search Walmart by terms and collect product data.

        Resumes from cursor if interrupted mid-term.  Stops at the
        configured max request limit.
        """
        term_index = int(cursor.get("term_index", 0))
        items = []  # type: List[Dict[str, Any]]
        self._request_count = 0

        for t_idx in range(term_index, len(WALMART_SEARCH_TERMS)):
            term = WALMART_SEARCH_TERMS[t_idx]
            start = int(cursor.get("start", 1)) if t_idx == term_index else 1

            self.log.info(
                "Walmart discovery: searching '%s' (start %d)", term, start,
            )
            term_count = 0
            page = 0

            while page < _MAX_PAGES_PER_TERM:
                if self._request_count >= WALMART_DISCOVERY_MAX_REQUESTS:
                    self.log.info(
                        "Hit request limit (%d); stopping discovery",
                        WALMART_DISCOVERY_MAX_REQUESTS,
                    )
                    return items

                products, total = self._search_products(term, start)
                if not products:
                    break

                for product in products:
                    item_id = str(product.get("itemId", ""))
                    if not item_id:
                        continue
                    items.append({
                        "_item_id": item_id,
                        "_term": term,
                        "_product": product,
                    })
                    term_count += 1

                # Move to next page
                start += _PAGE_SIZE
                page += 1

                # Stop if we've fetched all results for this term
                if total and start > total:
                    break

            self.log.info(
                "Walmart discovery: '%s' yielded %d products", term, term_count,
            )

        self.log.info(
            "Collected %d total products (%d API requests)",
            len(items), self._request_count,
        )
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return "walmart_{}".format(item["_item_id"])

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        product = item.get("_product", {})
        return product.get("productTrackingUrl") or product.get("productUrl")

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return self._today

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        return {
            "term_index": 0,
            "start": 1,
            "last_run_products": len(items),
            "last_run_date": self._today,
        }

    # ── Private helpers ─────────────────────────────────────────────────────

    def _search_products(self, query, start):
        # type: (str, int) -> tuple
        """Search Walmart API for one page of products.

        Returns (products_list, total_results) or ([], 0) on error.
        """
        auth_headers = get_auth_headers()
        if auth_headers is None:
            self.log.error("Cannot generate Walmart auth headers")
            return [], 0

        url = "{}/items".format(WALMART_API_BASE)
        params = {
            "query": query,
            "start": start,
            "numItems": _PAGE_SIZE,
            "format": "json",
            "facet": "on",
            "facet.filter": "category:Food",
        }  # type: Dict[str, Any]

        headers = {"Accept": "application/json"}
        headers.update(auth_headers)

        resp = self._session.get(
            url,
            params=params,
            headers=headers,
            raise_for_status=False,
        )
        self._request_count += 1

        if resp is None or resp.status_code >= 400:
            status = resp.status_code if resp is not None else "None"
            self.log.warning(
                "Walmart search failed: query='%s' start=%d status=%s",
                query, start, status,
            )
            # On 403, auth may have expired (timestamp drift) — log extra detail
            if resp is not None and resp.status_code == 403:
                self.log.warning(
                    "403 response body: %s", resp.text[:500],
                )
            return [], 0

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning(
                "JSON decode error for query='%s': %s", query, exc,
            )
            return [], 0

        total = data.get("totalResults", 0)
        products = data.get("items", [])

        return products, total
