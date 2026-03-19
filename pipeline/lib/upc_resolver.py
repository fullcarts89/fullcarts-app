"""UPC/barcode resolution service with multi-source fallback and caching.

Resolution chain (tried in order, stops on first hit):
  1. upc_cache table          — local Supabase cache (free, instant)
  2. UPCitemdb free tier       — 100 lookups/day, 6/minute rate limit
  3. Brocade.io                — free, no auth, generous limits
  4. Open Food Facts           — free, already in our stack

Every result (including misses) is cached so we never query the same
barcode twice. Daily UPCitemdb usage is tracked via a scraper_state cursor
to avoid exceeding the 100-lookup/day free tier limit.

Python 3.9 compatible — uses typing module, no X | Y union syntax.
"""
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

from pipeline.config import (
    BROCADE_API_URL,
    OFF_API_BASE,
    UPCITEMDB_DAILY_LIMIT,
    UPCITEMDB_TRIAL_URL,
    UPC_RESOLUTION_DELAY,
    USER_AGENT,
)
from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client

log = get_logger("upc_resolver")

# ── Sentinel value for "not yet in cache" ─────────────────────────────────────
# We need to distinguish three cache states:
#   - Row exists, not_found=false  → return the product dict
#   - Row exists, not_found=true   → return None (cached miss, don't re-query)
#   - No row exists                → return _CACHE_MISS (resolve from APIs)
#
# _check_cache() returns _CACHE_MISS when no cache row exists so resolve()
# can distinguish "cached miss" from "not yet cached".
_CACHE_MISS = object()

# ── Weight normalization ───────────────────────────────────────────────────────

# Grams and millilitres (approximate: 1ml ≈ 1g for food/beverages) to oz
_G_PER_OZ = 28.3495
_ML_PER_OZ = 29.5735

# Patterns: (regex, multiplier_to_oz)
# Order matters — more specific patterns first
_WEIGHT_PATTERNS: List[Tuple[str, float]] = [
    # Pounds/lbs  →  oz
    (r"(\d+(?:\.\d+)?)\s*lbs?\b", 16.0),
    # Kilograms   →  oz
    (r"(\d+(?:\.\d+)?)\s*kg\b", 1000.0 / _G_PER_OZ),
    # Grams       →  oz
    (r"(\d+(?:\.\d+)?)\s*g\b(?!al)", 1.0 / _G_PER_OZ),
    # Fluid oz    →  oz (volume, treat 1 fl oz = 1 oz)
    (r"(\d+(?:\.\d+)?)\s*fl\.?\s*oz\b", 1.0),
    # Millilitres →  oz  (approximate)
    (r"(\d+(?:\.\d+)?)\s*ml\b", 1.0 / _ML_PER_OZ),
    # Litres      →  oz
    (r"(\d+(?:\.\d+)?)\s*l\b(?!b)", 1000.0 / _ML_PER_OZ),
    # Ounces (plain)
    (r"(\d+(?:\.\d+)?)\s*oz\b", 1.0),
]


def parse_weight_oz(weight_str: Optional[str]) -> Optional[float]:
    """Parse a raw weight string into normalized ounces.

    Handles formats like "16 oz", "1 lb", "1.5 lbs", "453g", "2 kg",
    "500 ml", "1 l", "12 fl oz".  Returns None if unparseable.
    """
    if not weight_str:
        return None

    text = weight_str.lower().strip()

    for pattern, multiplier in _WEIGHT_PATTERNS:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                value = float(m.group(1))
                return round(value * multiplier, 4)
            except ValueError:
                continue

    return None


# ── UPCitemdb daily-limit tracker ─────────────────────────────────────────────

_UPCITEMDB_STATE_KEY = "upc_resolver_upcitemdb"


def _load_upcitemdb_usage() -> Dict[str, Any]:
    """Load today's UPCitemdb usage count from scraper_state."""
    try:
        client = get_client()
        resp = (
            client.table("scraper_state")
            .select("last_cursor")
            .eq("scraper_name", _UPCITEMDB_STATE_KEY)
            .maybe_single()
            .execute()
        )
        if resp and resp.data:
            cursor = resp.data.get("last_cursor") or {}
            return cursor
    except Exception as exc:
        log.warning("Could not load UPCitemdb usage state: %s", exc)
    return {}


def _save_upcitemdb_usage(cursor: Dict[str, Any]) -> None:
    """Persist today's UPCitemdb usage count to scraper_state."""
    try:
        client = get_client()
        now = datetime.now(timezone.utc).isoformat()
        client.table("scraper_state").upsert(
            {
                "scraper_name": _UPCITEMDB_STATE_KEY,
                "last_cursor": cursor,
                "last_run_at": now,
                "last_run_status": "ok",
                "items_processed": cursor.get("count_today", 0),
                "updated_at": now,
            },
            on_conflict="scraper_name",
        ).execute()
    except Exception as exc:
        log.warning("Could not save UPCitemdb usage state: %s", exc)


# ── Main resolver class ───────────────────────────────────────────────────────


class UpcResolver:
    """Resolves UPC barcodes to product metadata with multi-source fallback.

    Usage::

        resolver = UpcResolver()
        product = resolver.resolve("049000006124")
        if product:
            print(product["product_name"], product["brand"])

    The resolver caches every result (including misses) in the ``upc_cache``
    Supabase table so repeated lookups for the same barcode are instant.
    """

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": USER_AGENT})
        self._session.mount(
            "https://",
            requests.adapters.HTTPAdapter(
                max_retries=requests.adapters.Retry(
                    total=2,
                    backoff_factor=1,
                    status_forcelist=[429, 500, 502, 503, 504],
                    allowed_methods=["GET"],
                )
            ),
        )
        self._last_upcitemdb_request = 0.0
        self._upcitemdb_state = _load_upcitemdb_usage()

    # ── Public API ────────────────────────────────────────────────────────

    def resolve(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Resolve a single barcode to product metadata.

        Returns a dict with keys: product_name, brand, category, description,
        weight, weight_oz, image_url, source.  Returns None if not found in
        any source (but still caches the miss).
        """
        barcode = barcode.strip()
        if not barcode:
            return None

        # 1. Check cache
        cached = self._check_cache(barcode)
        if cached is not _CACHE_MISS:
            # Either a product dict (hit) or None (cached not-found) — either
            # way we have a definitive cached answer; don't hit the APIs.
            return cached

        # 2. Try each source in order
        result = None

        result = self._try_upcitemdb(barcode)

        if result is None:
            result = self._try_brocade(barcode)

        if result is None:
            result = self._try_openfoodfacts(barcode)

        # 3. Cache the result (or miss)
        self._write_cache(barcode, result)

        return result

    def resolve_batch(
        self, barcodes: List[str]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Resolve multiple barcodes, returning a dict keyed by barcode.

        Checks cache in bulk first, then resolves each cache miss individually
        to avoid redundant API calls.
        """
        barcodes = [b.strip() for b in barcodes if b.strip()]
        if not barcodes:
            return {}

        results: Dict[str, Optional[Dict[str, Any]]] = {}

        # Bulk cache check
        cached_map = self._check_cache_bulk(barcodes)
        to_resolve = []

        for barcode in barcodes:
            if barcode in cached_map:
                results[barcode] = cached_map[barcode]
            else:
                to_resolve.append(barcode)

        log.info(
            "resolve_batch: %d barcodes — %d cached, %d to resolve",
            len(barcodes),
            len(results),
            len(to_resolve),
        )

        for barcode in to_resolve:
            results[barcode] = self.resolve(barcode)

        return results

    # ── Cache layer ───────────────────────────────────────────────────────

    def _check_cache(self, barcode: str) -> Any:
        """Return cached result, or _CACHE_MISS sentinel if not in cache yet.

        Returns:
            dict         — cached hit (product found)
            None         — cached miss (not_found=true stored in DB)
            _CACHE_MISS  — no cache row exists yet; must query APIs
        """
        try:
            client = get_client()
            resp = (
                client.table("upc_cache")
                .select(
                    "barcode,product_name,brand,category,description,"
                    "weight,weight_oz,image_url,source,not_found"
                )
                .eq("barcode", barcode)
                .maybe_single()
                .execute()
            )
            if resp and resp.data:
                row = resp.data
                if row.get("not_found"):
                    log.debug("Cache miss (cached): %s", barcode)
                    return None  # cached miss — don't re-query
                log.debug("Cache hit: %s → %s", barcode, row.get("product_name"))
                return self._row_to_product(row)
        except Exception as exc:
            log.warning("Cache lookup failed for %s: %s", barcode, exc)

        return _CACHE_MISS

    def _check_cache_bulk(
        self, barcodes: List[str]
    ) -> Dict[str, Optional[Dict[str, Any]]]:
        """Bulk cache lookup. Returns dict of barcode → result for cached entries."""
        results: Dict[str, Optional[Dict[str, Any]]] = {}
        try:
            client = get_client()
            resp = (
                client.table("upc_cache")
                .select(
                    "barcode,product_name,brand,category,description,"
                    "weight,weight_oz,image_url,source,not_found"
                )
                .in_("barcode", barcodes)
                .execute()
            )
            if resp and resp.data:
                for row in resp.data:
                    bc = row["barcode"]
                    if row.get("not_found"):
                        results[bc] = None
                    else:
                        results[bc] = self._row_to_product(row)
        except Exception as exc:
            log.warning("Bulk cache lookup failed: %s", exc)
        return results

    def _write_cache(
        self, barcode: str, product: Optional[Dict[str, Any]]
    ) -> None:
        """Write a result (or miss) to upc_cache."""
        try:
            client = get_client()
            now = datetime.now(timezone.utc).isoformat()
            if product is None:
                row = {
                    "barcode": barcode,
                    "not_found": True,
                    "resolved_at": now,
                }
            else:
                row = {
                    "barcode": barcode,
                    "product_name": product.get("product_name"),
                    "brand": product.get("brand"),
                    "category": product.get("category"),
                    "description": product.get("description"),
                    "weight": product.get("weight"),
                    "weight_oz": product.get("weight_oz"),
                    "image_url": product.get("image_url"),
                    "source": product.get("source"),
                    "raw_response": product.get("raw_response"),
                    "not_found": False,
                    "resolved_at": now,
                }
            client.table("upc_cache").upsert(
                row, on_conflict="barcode"
            ).execute()
            log.debug(
                "Cached %s: %s",
                barcode,
                "miss" if product is None else product.get("source"),
            )
        except Exception as exc:
            log.warning("Failed to cache %s: %s", barcode, exc)

    @staticmethod
    def _row_to_product(row: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a upc_cache row to a product dict."""
        return {
            "product_name": row.get("product_name"),
            "brand": row.get("brand"),
            "category": row.get("category"),
            "description": row.get("description"),
            "weight": row.get("weight"),
            "weight_oz": row.get("weight_oz"),
            "image_url": row.get("image_url"),
            "source": row.get("source"),
        }

    # ── UPCitemdb ─────────────────────────────────────────────────────────

    def _upcitemdb_quota_ok(self) -> bool:
        """Return True if we have daily quota remaining for UPCitemdb."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        state_date = self._upcitemdb_state.get("date", "")
        if state_date != today:
            # New day — reset counter
            self._upcitemdb_state = {"date": today, "count_today": 0}
        count = self._upcitemdb_state.get("count_today", 0)
        return count < UPCITEMDB_DAILY_LIMIT

    def _upcitemdb_increment(self) -> None:
        """Increment today's UPCitemdb usage counter and persist it."""
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._upcitemdb_state.get("date") != today:
            self._upcitemdb_state = {"date": today, "count_today": 0}
        self._upcitemdb_state["count_today"] = (
            self._upcitemdb_state.get("count_today", 0) + 1
        )
        _save_upcitemdb_usage(self._upcitemdb_state)

    def _throttle_upcitemdb(self) -> None:
        """Enforce 10s minimum between UPCitemdb requests (free tier: 6/min)."""
        elapsed = time.monotonic() - self._last_upcitemdb_request
        wait = UPC_RESOLUTION_DELAY - elapsed
        if wait > 0:
            time.sleep(wait)
        self._last_upcitemdb_request = time.monotonic()

    def _try_upcitemdb(
        self, barcode: str
    ) -> Optional[Dict[str, Any]]:
        """Query UPCitemdb free trial endpoint."""
        if not self._upcitemdb_quota_ok():
            log.info(
                "UPCitemdb daily limit reached (%d/%d); skipping.",
                self._upcitemdb_state.get("count_today", 0),
                UPCITEMDB_DAILY_LIMIT,
            )
            return None

        self._throttle_upcitemdb()

        try:
            resp = self._session.get(
                UPCITEMDB_TRIAL_URL,
                params={"upc": barcode},
                timeout=15,
            )
        except requests.RequestException as exc:
            log.warning("UPCitemdb request failed for %s: %s", barcode, exc)
            return None

        self._upcitemdb_increment()

        if resp.status_code == 404:
            log.debug("UPCitemdb: not found — %s", barcode)
            return None

        if resp.status_code != 200:
            log.warning(
                "UPCitemdb returned %d for %s", resp.status_code, barcode
            )
            return None

        try:
            data = resp.json()
        except Exception as exc:
            log.warning("UPCitemdb JSON parse error for %s: %s", barcode, exc)
            return None

        items = data.get("items", [])
        if not items:
            log.debug("UPCitemdb: empty items list — %s", barcode)
            return None

        item = items[0]
        weight_str = item.get("size") or item.get("weight") or None
        return {
            "product_name": item.get("title") or item.get("description"),
            "brand": item.get("brand"),
            "category": item.get("category"),
            "description": item.get("description"),
            "weight": weight_str,
            "weight_oz": parse_weight_oz(weight_str),
            "image_url": (item.get("images") or [None])[0],
            "source": "upcitemdb",
            "raw_response": data,
        }

    # ── Brocade.io ────────────────────────────────────────────────────────

    def _try_brocade(self, barcode: str) -> Optional[Dict[str, Any]]:
        """Query Brocade.io (free, no auth required)."""
        try:
            resp = self._session.get(
                "{}/{}".format(BROCADE_API_URL, barcode),
                timeout=15,
            )
        except requests.RequestException as exc:
            log.warning("Brocade request failed for %s: %s", barcode, exc)
            return None

        if resp.status_code == 404:
            log.debug("Brocade: not found — %s", barcode)
            return None

        if resp.status_code != 200:
            log.warning(
                "Brocade returned %d for %s", resp.status_code, barcode
            )
            return None

        try:
            data = resp.json()
        except Exception as exc:
            log.warning("Brocade JSON parse error for %s: %s", barcode, exc)
            return None

        # Brocade returns a single item object (not a list)
        if not data or not data.get("name"):
            log.debug("Brocade: empty response — %s", barcode)
            return None

        weight_str = data.get("size") or data.get("net_weight") or None
        return {
            "product_name": data.get("name"),
            "brand": data.get("brand"),
            "category": data.get("category"),
            "description": data.get("description") or data.get("name"),
            "weight": weight_str,
            "weight_oz": parse_weight_oz(weight_str),
            "image_url": data.get("image_url") or data.get("thumbnail"),
            "source": "brocade",
            "raw_response": data,
        }

    # ── Open Food Facts ───────────────────────────────────────────────────

    def _try_openfoodfacts(
        self, barcode: str
    ) -> Optional[Dict[str, Any]]:
        """Query Open Food Facts API v2."""
        try:
            resp = self._session.get(
                "{}/product/{}".format(OFF_API_BASE, barcode),
                params={"fields": "product_name,brands,categories,quantity,image_url"},
                timeout=15,
            )
        except requests.RequestException as exc:
            log.warning(
                "Open Food Facts request failed for %s: %s", barcode, exc
            )
            return None

        if resp.status_code == 404:
            log.debug("Open Food Facts: not found — %s", barcode)
            return None

        if resp.status_code != 200:
            log.warning(
                "Open Food Facts returned %d for %s", resp.status_code, barcode
            )
            return None

        try:
            data = resp.json()
        except Exception as exc:
            log.warning(
                "Open Food Facts JSON parse error for %s: %s", barcode, exc
            )
            return None

        if data.get("status") != 1:
            log.debug("Open Food Facts: product not found — %s", barcode)
            return None

        product = data.get("product") or {}
        if not product:
            return None

        weight_str = product.get("quantity") or None
        # OFF categories are comma-separated, take the first
        raw_cats = product.get("categories", "")
        category = raw_cats.split(",")[0].strip() if raw_cats else None

        return {
            "product_name": product.get("product_name"),
            "brand": product.get("brands"),
            "category": category,
            "description": product.get("product_name"),
            "weight": weight_str,
            "weight_oz": parse_weight_oz(weight_str),
            "image_url": product.get("image_url"),
            "source": "openfoodfacts",
            "raw_response": data,
        }

