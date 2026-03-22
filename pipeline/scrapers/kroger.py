"""Kroger API weekly price/size scraper.

For every active pack_variant UPC and each configured store location, fetches
product data from the Kroger Product API using OAuth2 client credentials.
Writes to raw_items and variant_observations.
"""
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pipeline.config import (
    KROGER_API_BASE,
    KROGER_STORE_IDS,
    USER_AGENT,
)
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.kroger_auth import KrogerAuth
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

# Kroger rate limits: 10,000 req/day on free tier.
# We poll (UPCs × stores); stay conservative at 2 req/s.
_KROGER_RPS = 2.0


class KrogerScraper(BaseScraper):
    """Weekly product/price poll from the Kroger Product API."""

    scraper_name = "kroger_weekly"
    source_type = "kroger_api"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_KROGER_RPS,
            user_agent=USER_AGENT,
        )
        self._today = date.today().isoformat()
        self._auth = KrogerAuth(self._session)

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch product data for every active UPC × configured store.

        Each returned item is a dict with:
            _upc         — the UPC queried
            _store_id    — the Kroger store location ID
            _found       — bool: whether Kroger returned any products
            _product     — the Kroger product dict (first match), or {}
        """
        upcs = self._load_active_upcs()
        store_ids = [s.strip() for s in KROGER_STORE_IDS if s.strip()]
        self.log.info(
            "Kroger fetch: %d UPCs × %d stores", len(upcs), len(store_ids)
        )

        items: List[Dict[str, Any]] = []
        for upc in upcs:
            for store_id in store_ids:
                product = self._fetch_product(upc, store_id)
                items.append({
                    "_upc": upc,
                    "_store_id": store_id,
                    "_found": product is not None,
                    "_product": product or {},
                })

        found_count = sum(1 for i in items if i["_found"])
        self.log.info(
            "Kroger fetch complete: %d requests, %d products found",
            len(items), found_count,
        )
        return items

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return f"kroger_{item['_upc']}_{self._today}_{item['_store_id']}"

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return None  # No public Kroger product URL

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return self._today

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        # Count distinct UPCs (not UPC×store pairs)
        upcs_polled = len({i["_upc"] for i in items})
        return {
            "last_poll_date": self._today,
            "upcs_polled": upcs_polled,
        }

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Write raw_items, then write variant_observations for found products."""
        stored = super().store(items)
        self._store_variant_observations(items)
        return stored

    # ── Private helpers ────────────────────────────────────────────────────

    def _load_active_upcs(self) -> List[str]:
        """Return all UPCs from pack_variants where is_active = true."""
        client = get_client()
        resp = (
            client.table("pack_variants")
            .select("upc")
            .eq("is_active", True)
            .execute()
        )
        return [row["upc"] for row in (resp.data or []) if row.get("upc")]

    def _fetch_product(
        self, upc: str, store_id: str
    ) -> Optional[Dict[str, Any]]:
        """Fetch one UPC from one store.  Returns the first product dict or None."""
        token = self._auth.get_token()
        if token is None:
            return None

        url = f"{KROGER_API_BASE}/products"
        params: Dict[str, Any] = {
            "filter.term": upc,
            "filter.locationId": store_id,
        }
        resp = self._session.get(
            url,
            params=params,
            headers={"Authorization": f"Bearer {token}"},
            raise_for_status=False,
        )

        # Re-authenticate on 401 and retry once
        if resp is not None and resp.status_code == 401:
            self.log.info("Got 401; refreshing Kroger token")
            self._auth.invalidate()
            token = self._auth.get_token()
            if token is None:
                return None
            resp = self._session.get(
                url,
                params=params,
                headers={"Authorization": f"Bearer {token}"},
            )

        if resp is None or resp.status_code >= 400:
            self.log.warning(
                "Kroger request failed: UPC=%s store=%s", upc, store_id
            )
            return None

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning(
                "JSON decode error for UPC=%s store=%s: %s", upc, store_id, exc
            )
            return None

        products = data.get("data", [])
        if not products:
            self.log.debug(
                "No Kroger product for UPC=%s store=%s", upc, store_id
            )
            return None

        return products[0]  # Take first matching product

    def _store_variant_observations(
        self, items: List[Dict[str, Any]]
    ) -> None:
        """Upsert variant_observations for items with Kroger product data."""
        client = get_client()
        found_items = [i for i in items if i["_found"]]
        if not found_items:
            return

        upcs = list({i["_upc"] for i in found_items})
        variant_map = self._load_variant_map(upcs)
        raw_id_map = self._load_raw_item_ids(items)

        rows: List[Dict[str, Any]] = []
        for item in found_items:
            upc = item["_upc"]
            store_id = item["_store_id"]
            variant_id = variant_map.get(upc)
            if variant_id is None:
                continue

            product = item["_product"]
            size, size_unit, price = self._parse_kroger_product(product)
            if size is None:
                self.log.debug(
                    "Could not parse size for UPC=%s store=%s; skipping",
                    upc, store_id,
                )
                continue

            rows.append({
                "variant_id": variant_id,
                "observed_date": self._today,
                "source_type": "kroger_api",
                "source_ref": f"kroger_{self._today}_{store_id}",
                "size": size,
                "size_unit": size_unit,
                "price": price,
                "retailer": "Kroger",
                "store_location": store_id,
                "raw_item_id": raw_id_map.get(f"{upc}_{store_id}"),
            })

        if not rows:
            return

        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            client.table("variant_observations").upsert(
                batch,
                on_conflict="variant_id,observed_date,source_type,retailer",
            ).execute()

        self.log.info(
            "Upserted %d variant_observations for kroger_weekly", len(rows)
        )

    def _parse_kroger_product(
        self, product: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[str], Optional[float]]:
        """Extract (size, size_unit, price) from a Kroger product dict."""
        items_list = product.get("items", [])
        first_item: Dict[str, Any] = items_list[0] if items_list else {}

        size_text = first_item.get("size", "")
        size, size_unit = parse_package_weight(size_text) if size_text else (None, None)

        price_info = first_item.get("price", {})
        price: Optional[float] = None
        if price_info:
            regular = price_info.get("regular")
            if regular is not None:
                try:
                    price = float(regular)
                except (ValueError, TypeError):
                    pass

        return size, size_unit, price

    def _load_variant_map(self, upcs: List[str]) -> Dict[str, Any]:
        """Return {upc: variant_id} for the given UPCs."""
        client = get_client()
        resp = (
            client.table("pack_variants")
            .select("id,upc")
            .in_("upc", upcs)
            .execute()
        )
        return {row["upc"]: row["id"] for row in (resp.data or [])}

    def _load_raw_item_ids(
        self, items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Return {"upc_storeid": raw_item_id} for found items."""
        client = get_client()
        source_ids = [
            self.source_id_for(i) for i in items if i["_found"]
        ]
        if not source_ids:
            return {}
        resp = (
            client.table("raw_items")
            .select("id,source_id")
            .eq("source_type", self.source_type)
            .in_("source_id", source_ids)
            .execute()
        )
        # source_id is "kroger_{upc}_{date}_{store_id}"
        # Key we need for the variant obs lookup is "{upc}_{store_id}"
        result: Dict[str, Any] = {}
        for row in (resp.data or []):
            sid = row["source_id"]
            # Strip "kroger_" prefix, then split from the right on "_" to
            # isolate store_id and date, leaving the UPC intact even if it
            # contains underscores.
            remainder = sid[len("kroger_"):]  # "{upc}_{date}_{store_id}"
            # store_id is the last segment
            rest, store_id = remainder.rsplit("_", 1)
            # date (YYYY-MM-DD) is the last segment of what remains
            upc, _date = rest.rsplit("_", 1)
            result[f"{upc}_{store_id}"] = row["id"]
        return result
