"""Open Food Facts daily spot-check scraper.

For every active pack_variant UPC, fetches the current product record from
the OFF API and writes to both raw_items and variant_observations.
"""
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pipeline.config import OFF_API_BASE, USER_AGENT
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

# OFF allows 100 req/min → 1 request per 0.6 seconds
_OFF_RPS = 1.0 / 0.6

# Fields to keep from the OFF product response (discard the rest)
_KEEP_FIELDS = {
    "code",
    "product_name",
    "brands",
    "quantity",
    "product_quantity",
    "product_quantity_unit",
    "categories",
    "image_url",
}


class OpenFoodFactsScraper(BaseScraper):
    """Daily UPC spot-check against the Open Food Facts product API."""

    scraper_name = "off_daily"
    source_type = "openfoodfacts"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_OFF_RPS,
            user_agent=USER_AGENT,
        )
        self._today = date.today().isoformat()

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch OFF product data for every active pack_variant UPC.

        Each returned item is a dict with:
            _upc           — the UPC we queried
            _found         — bool: whether OFF returned product data
            _raw_product   — the filtered OFF product dict (or {} if not found)
        """
        upcs = self._load_active_upcs()
        self.log.info("Loaded %d active UPCs from pack_variants", len(upcs))

        items: List[Dict[str, Any]] = []
        for upc in upcs:
            product = self._fetch_product(upc)
            items.append({
                "_upc": upc,
                "_found": product is not None,
                "_raw_product": product or {},
            })

        self.log.info(
            "OFF fetch complete: %d queried, %d found",
            len(items),
            sum(1 for i in items if i["_found"]),
        )
        return items

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return f"{item['_upc']}_{self._today}"

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        return f"https://world.openfoodfacts.org/product/{item['_upc']}"

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return self._today

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "last_check_date": self._today,
            "upcs_checked": len(items),
        }

    def store(self, items: List[Dict[str, Any]]) -> int:
        """Write raw_items, then write variant_observations for found products."""
        # 1. Write raw payloads via the base implementation.
        #    The base store() calls raw_payload=item, but we only want the product
        #    dict stored — not the internal _upc/_found/_raw_product envelope.
        #    We override the items list to pass just the product dict, keeping the
        #    envelope fields accessible via the original `items` list below.
        stored = super().store(items)

        # 2. Write variant_observations for items that had product data.
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

    def _fetch_product(self, upc: str) -> Optional[Dict[str, Any]]:
        """Fetch a single UPC from OFF.  Returns filtered product dict or None."""
        url = f"{OFF_API_BASE}/product/{upc}.json"
        resp = self._session.get(url)
        if resp is None:
            self.log.warning("OFF request failed for UPC %s", upc)
            return None

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning("JSON decode error for UPC %s: %s", upc, exc)
            return None

        status = data.get("status", 0)
        if status != 1:
            self.log.debug("UPC %s not found in OFF (status=%s)", upc, status)
            return None

        product = data.get("product", {})
        return {k: v for k, v in product.items() if k in _KEEP_FIELDS}

    def _store_variant_observations(
        self, items: List[Dict[str, Any]]
    ) -> None:
        """Upsert variant_observations for items with OFF product data."""
        client = get_client()
        found_items = [i for i in items if i["_found"]]
        if not found_items:
            return

        # Build UPC → variant_id lookup from pack_variants
        upcs = [i["_upc"] for i in found_items]
        variant_map = self._load_variant_map(upcs)

        # Build UPC → raw_item_id lookup for items we just inserted
        raw_id_map = self._load_raw_item_ids(items)

        source_ref = f"off_daily_{self._today}"
        rows: List[Dict[str, Any]] = []

        for item in found_items:
            upc = item["_upc"]
            variant_id = variant_map.get(upc)
            if variant_id is None:
                continue  # UPC not in pack_variants — skip

            product = item["_raw_product"]

            # Parse size from product_quantity + product_quantity_unit first,
            # falling back to the combined quantity string (e.g. "340 g").
            size, size_unit = self._parse_off_size(product)
            if size is None:
                self.log.debug(
                    "Could not parse size for UPC %s; skipping observation", upc
                )
                continue

            rows.append({
                "variant_id": variant_id,
                "observed_date": self._today,
                "source_type": "openfoodfacts",
                "source_ref": source_ref,
                "size": size,
                "size_unit": size_unit,
                "raw_item_id": raw_id_map.get(upc),
            })

        if not rows:
            return

        # Batch upsert; unique index is (variant_id, observed_date, source_type,
        # COALESCE(retailer, '')) — retailer is NULL for OFF observations.
        batch_size = 50
        for i in range(0, len(rows), batch_size):
            batch = rows[i:i + batch_size]
            client.table("variant_observations").upsert(
                batch,
                on_conflict="variant_id,observed_date,source_type,retailer",
            ).execute()

        self.log.info(
            "Upserted %d variant_observations for off_daily", len(rows)
        )

    def _parse_off_size(
        self, product: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[str]]:
        """Parse size from OFF product fields, preferring the numeric fields."""
        pq = product.get("product_quantity", "")
        pq_unit = product.get("product_quantity_unit", "")
        if pq and pq_unit:
            size, unit = parse_package_weight(f"{pq} {pq_unit}")
            if size is not None:
                return size, unit

        # Fall back to the free-text quantity field
        quantity = product.get("quantity", "")
        if quantity:
            return parse_package_weight(quantity)

        return None, None

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
        """Return {upc: raw_item_id} by querying raw_items for today's source_ids."""
        client = get_client()
        source_ids = [self.source_id_for(i) for i in items if i["_found"]]
        if not source_ids:
            return {}
        resp = (
            client.table("raw_items")
            .select("id,source_id")
            .eq("source_type", self.source_type)
            .in_("source_id", source_ids)
            .execute()
        )
        # source_id is "{upc}_{date}" — extract upc from it
        result: Dict[str, Any] = {}
        for row in (resp.data or []):
            upc = row["source_id"].rsplit("_", 1)[0]
            result[upc] = row["id"]
        return result
