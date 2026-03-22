"""UPC backfill scraper — enriches pack_variants missing OFF observations.

Finds active pack_variant UPCs that have never been checked against
Open Food Facts (no variant_observations with source_type='openfoodfacts'),
fetches product data from OFF, and writes raw_items + variant_observations.

Runs daily to catch newly discovered UPCs from Kroger/Walmart discovery
that haven't been through an off_daily cycle yet.
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


class UpcBackfillScraper(BaseScraper):
    """Backfill OFF data for pack_variants missing observations."""

    scraper_name = "upc_backfill"
    source_type = "openfoodfacts"

    def __init__(self):
        # type: () -> None
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_OFF_RPS,
            user_agent=USER_AGENT,
        )
        self._today = date.today().isoformat()

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor, dry_run=False
    ):
        # type: (Dict[str, Any], bool) -> List[Dict[str, Any]]
        """Fetch OFF product data for active UPCs missing OFF observations."""
        upcs = self._load_missing_upcs()
        self.log.info(
            "Found %d active UPCs without OFF observations", len(upcs)
        )

        items = []  # type: List[Dict[str, Any]]
        for upc in upcs:
            product = self._fetch_product(upc)
            items.append({
                "_upc": upc,
                "_found": product is not None,
                "_raw_product": product or {},
            })

        self.log.info(
            "UPC backfill fetch complete: %d queried, %d found",
            len(items),
            sum(1 for i in items if i["_found"]),
        )
        return items

    def source_id_for(self, item):
        # type: (Dict[str, Any]) -> str
        return "off_backfill_{}_{}".format(item["_upc"], self._today)

    def source_url_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return "https://world.openfoodfacts.org/product/{}".format(
            item["_upc"]
        )

    def source_date_for(self, item):
        # type: (Dict[str, Any]) -> Optional[str]
        return self._today

    def next_cursor(self, items, prev_cursor):
        # type: (List[Dict[str, Any]], Dict[str, Any]) -> Dict[str, Any]
        return {
            "last_backfill_date": self._today,
            "upcs_checked": len(items),
            "upcs_found": sum(1 for i in items if i["_found"]),
        }

    def store(self, items):
        # type: (List[Dict[str, Any]]) -> int
        """Write raw_items (product dict only), then variant_observations."""
        stored = self._store_raw_items(items)
        self._store_variant_observations(items)
        return stored

    def _store_raw_items(self, items):
        # type: (List[Dict[str, Any]]) -> int
        """Upsert raw_items with only the product dict as raw_payload."""
        from pipeline.config import SCRAPER_VERSION
        from pipeline.lib.hashing import content_hash

        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        total_new = 0
        batch_size = 50

        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            rows = []  # type: List[Dict[str, Any]]
            for item in batch:
                payload = item["_raw_product"] if item["_found"] else {}
                rows.append({
                    "source_type": self.source_type,
                    "source_id": self.source_id_for(item),
                    "source_url": self.source_url_for(item),
                    "captured_at": now,
                    "source_date": self.source_date_for(item),
                    "raw_payload": payload,
                    "content_hash": content_hash(payload),
                    "scraper_version": SCRAPER_VERSION,
                })

            resp = (
                client.table("raw_items")
                .upsert(rows, on_conflict="source_type,source_id")
                .execute()
            )
            if resp and resp.data:
                total_new += len(resp.data)

        return total_new

    # ── Private helpers ────────────────────────────────────────────────────

    def _load_missing_upcs(self):
        # type: () -> List[str]
        """Return active UPCs that have no OFF variant_observations."""
        client = get_client()

        # Get all active UPCs
        resp = (
            client.table("pack_variants")
            .select("upc")
            .eq("is_active", True)
            .execute()
        )
        all_upcs = [
            row["upc"] for row in (resp.data or []) if row.get("upc")
        ]
        if not all_upcs:
            return []

        # Get UPCs that already have OFF observations
        # Query variant_observations via pack_variants join
        resp2 = (
            client.table("variant_observations")
            .select("variant_id")
            .eq("source_type", "openfoodfacts")
            .execute()
        )
        observed_variant_ids = {
            row["variant_id"] for row in (resp2.data or [])
        }

        # Get variant_id → upc mapping
        resp3 = (
            client.table("pack_variants")
            .select("id,upc")
            .eq("is_active", True)
            .execute()
        )
        observed_upcs = set()  # type: set
        for row in (resp3.data or []):
            if row["id"] in observed_variant_ids:
                observed_upcs.add(row["upc"])

        missing = [u for u in all_upcs if u not in observed_upcs]
        self.log.info(
            "Active UPCs: %d total, %d with OFF obs, %d missing",
            len(all_upcs), len(observed_upcs), len(missing),
        )
        return missing

    def _fetch_product(self, upc):
        # type: (str) -> Optional[Dict[str, Any]]
        """Fetch a single UPC from OFF.  Returns filtered product dict or None."""
        url = "{}/product/{}.json".format(OFF_API_BASE, upc)
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

    def _store_variant_observations(self, items):
        # type: (List[Dict[str, Any]]) -> None
        """Upsert variant_observations for items with OFF product data."""
        client = get_client()
        found_items = [i for i in items if i["_found"]]
        if not found_items:
            return

        upcs = [i["_upc"] for i in found_items]
        variant_map = self._load_variant_map(upcs)

        source_ref = "off_backfill_{}".format(self._today)
        rows = []  # type: List[Dict[str, Any]]

        for item in found_items:
            upc = item["_upc"]
            variant_id = variant_map.get(upc)
            if variant_id is None:
                continue

            product = item["_raw_product"]
            size, size_unit = self._parse_off_size(product)
            if size is None:
                self.log.debug(
                    "Could not parse size for UPC %s; skipping observation",
                    upc,
                )
                continue

            rows.append({
                "variant_id": variant_id,
                "observed_date": self._today,
                "source_type": "openfoodfacts",
                "source_ref": source_ref,
                "size": size,
                "size_unit": size_unit,
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
            "Upserted %d variant_observations for upc_backfill", len(rows)
        )

    def _parse_off_size(self, product):
        # type: (Dict[str, Any]) -> Tuple[Optional[float], Optional[str]]
        """Parse size from OFF product fields."""
        pq = product.get("product_quantity", "")
        pq_unit = product.get("product_quantity_unit", "")
        if pq and pq_unit:
            size, unit = parse_package_weight("{} {}".format(pq, pq_unit))
            if size is not None:
                return size, unit

        quantity = product.get("quantity", "")
        if quantity:
            return parse_package_weight(quantity)

        return None, None

    def _load_variant_map(self, upcs):
        # type: (List[str]) -> Dict[str, Any]
        """Return {upc: variant_id} for the given UPCs."""
        client = get_client()
        resp = (
            client.table("pack_variants")
            .select("id,upc")
            .in_("upc", upcs)
            .execute()
        )
        return {row["upc"]: row["id"] for row in (resp.data or [])}
