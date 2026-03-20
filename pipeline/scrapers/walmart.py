"""Walmart Open API weekly price/size scraper.

For every active pack_variant UPC, looks up product data from the Walmart
Open API (formerly Affiliate API) and writes to raw_items.

Auth scheme (RSA-signed headers):
  WM_CONSUMER.ID             — consumer ID from developer portal
  WM_CONSUMER.intimestamp    — Unix timestamp in milliseconds
  WM_SEC.KEY_VERSION         — "1"
  WM_SEC.AUTH_SIGNATURE      — Base64(RSA-SHA256(consumerId + "\\n"
                                               + timestamp + "\\n"
                                               + keyVersion + "\\n"))

Credentials required (set env vars or skip gracefully):
  WALMART_CONSUMER_ID          — developer portal consumer ID
  WALMART_PRIVATE_KEY_PATH     — path to RSA private key PEM file
                                 (default: walmart_private_key.pem)

The scraper gracefully skips with a clear error message when credentials
are missing, so it can be registered without breaking other scrapers.
"""
import base64
import os
import time
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pipeline.config import USER_AGENT, WALMART_CONSUMER_ID, WALMART_PRIVATE_KEY_PATH
from pipeline.lib.http_client import RateLimitedSession
from pipeline.lib.supabase_client import get_client
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

# Walmart API rate limits: 5 req/s on free tier
_WALMART_RPS = 3.0

# Walmart Open API base URL
_API_BASE = "https://developer.api.walmart.com/api-proxy/service/affil/product/v2"

# RSA key version (always "1" for the current Walmart auth scheme)
_KEY_VERSION = "1"

# Maximum UPCs per request (Walmart items endpoint accepts comma-separated UPCs)
_BATCH_SIZE = 20


class WalmartScraper(BaseScraper):
    """Weekly product/price poll from the Walmart Open API."""

    scraper_name = "walmart_weekly"
    source_type = "walmart_api"

    def __init__(self) -> None:
        super().__init__()
        self._session = RateLimitedSession(
            requests_per_second=_WALMART_RPS,
            user_agent=USER_AGENT,
        )
        self._today = date.today().isoformat()
        self._private_key = self._load_private_key()

    # ── BaseScraper interface ──────────────────────────────────────────────

    def fetch(
        self, cursor: Dict[str, Any], dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """Fetch Walmart product data for every active pack_variant UPC.

        Returns an empty list with a warning if credentials are not configured.
        Each returned item is a dict with:
            _upc       — the UPC queried
            _found     — bool: whether Walmart returned product data
            _product   — the Walmart product dict, or {}
        """
        if not WALMART_CONSUMER_ID:
            self.log.warning(
                "WALMART_CONSUMER_ID not set — skipping Walmart fetch. "
                "Set WALMART_CONSUMER_ID and WALMART_PRIVATE_KEY_PATH to enable."
            )
            return []

        if self._private_key is None:
            self.log.warning(
                "Walmart private key not loaded (checked: %s) — skipping fetch. "
                "Set WALMART_PRIVATE_KEY_PATH to the path of your RSA PEM file.",
                WALMART_PRIVATE_KEY_PATH,
            )
            return []

        upcs = self._load_active_upcs()
        self.log.info("Loaded %d active UPCs from pack_variants", len(upcs))

        if not upcs:
            self.log.info("No active UPCs to check — done")
            return []

        items: List[Dict[str, Any]] = []
        # Walmart items endpoint accepts up to 20 UPCs at once (comma-separated)
        for i in range(0, len(upcs), _BATCH_SIZE):
            batch = upcs[i:i + _BATCH_SIZE]
            batch_results = self._fetch_batch(batch)
            items.extend(batch_results)

        found_count = sum(1 for i in items if i["_found"])
        self.log.info(
            "Walmart fetch complete: %d queried, %d found",
            len(items), found_count,
        )
        return items

    def source_id_for(self, item: Dict[str, Any]) -> str:
        return f"walmart_{item['_upc']}_{self._today}"

    def source_url_for(self, item: Dict[str, Any]) -> Optional[str]:
        item_id = item.get("_product", {}).get("itemId")
        if item_id:
            return f"https://www.walmart.com/ip/{item_id}"
        return None

    def source_date_for(self, item: Dict[str, Any]) -> Optional[str]:
        return self._today

    def next_cursor(
        self, items: List[Dict[str, Any]], prev_cursor: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "last_check_date": self._today,
            "upcs_checked": len(items),
            "upcs_found": sum(1 for i in items if i["_found"]),
        }

    # ── Private helpers ────────────────────────────────────────────────────

    def _load_private_key(self) -> Optional[Any]:
        """Load RSA private key from PEM file. Returns None if not found."""
        key_path = WALMART_PRIVATE_KEY_PATH
        if not os.path.exists(key_path):
            # Not an error at construction time — credentials may not be configured
            return None
        try:
            from cryptography.hazmat.primitives import serialization
            with open(key_path, "rb") as f:
                key = serialization.load_pem_private_key(f.read(), password=None)
            self.log.info("Loaded Walmart private key from %s", key_path)
            return key
        except Exception as exc:
            self.log.error("Failed to load Walmart private key: %s", exc)
            return None

    def _sign_request(self) -> Dict[str, str]:
        """Build signed Walmart auth headers for the current timestamp."""
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding

        consumer_id = WALMART_CONSUMER_ID
        timestamp = str(int(time.time() * 1000))
        key_version = _KEY_VERSION

        # Message to sign: each field on its own line, trailing newline required
        message = f"{consumer_id}\n{timestamp}\n{key_version}\n"

        signature = self._private_key.sign(
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        auth_sig = base64.b64encode(signature).decode("utf-8")

        return {
            "WM_CONSUMER.ID": consumer_id,
            "WM_CONSUMER.intimestamp": timestamp,
            "WM_SEC.KEY_VERSION": key_version,
            "WM_SEC.AUTH_SIGNATURE": auth_sig,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }

    def _fetch_batch(self, upcs: List[str]) -> List[Dict[str, Any]]:
        """Fetch up to _BATCH_SIZE UPCs in one API call."""
        url = f"{_API_BASE}/items"
        params = {
            "ids": ",".join(upcs),
            "publishedStatus": "PUBLISHED",
        }
        try:
            headers = self._sign_request()
        except Exception as exc:
            self.log.error("Failed to sign Walmart request: %s", exc)
            return [{"_upc": u, "_found": False, "_product": {}} for u in upcs]

        resp = self._session.get(url, params=params, headers=headers, raise_for_status=False)
        if resp is None:
            self.log.warning("Walmart request failed for batch %s…", upcs[:3])
            return [{"_upc": u, "_found": False, "_product": {}} for u in upcs]

        if not resp.ok:
            self.log.warning(
                "Walmart API error %d for batch %s…: %s",
                resp.status_code, upcs[:3], resp.text[:200],
            )
            return [{"_upc": u, "_found": False, "_product": {}} for u in upcs]

        try:
            data = resp.json()
        except Exception as exc:
            self.log.warning("JSON decode error for batch: %s", exc)
            return [{"_upc": u, "_found": False, "_product": {}} for u in upcs]

        # Build UPC → product dict from response
        products_by_upc: Dict[str, Dict[str, Any]] = {}
        for item in data.get("items", []):
            upc = item.get("upc", "")
            if upc:
                products_by_upc[upc] = item
            # Also index by UPC without leading zeros
            upc_stripped = upc.lstrip("0")
            if upc_stripped:
                products_by_upc[upc_stripped] = item

        results = []
        for upc in upcs:
            product = products_by_upc.get(upc) or products_by_upc.get(upc.lstrip("0"))
            results.append({
                "_upc": upc,
                "_found": product is not None,
                "_product": product or {},
            })
        return results

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
