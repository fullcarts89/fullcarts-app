"""Base class for discovery scrapers that populate the product catalog.

Discovery scrapers find products from external sources (OFF, Kroger, Walmart)
and upsert them into product_entities + pack_variants + variant_observations,
rather than raw_items.  This keeps catalog data out of the claims pipeline.

Only actual size changes detected by analyze_catalog_variance.py generate
claims — discovery itself is purely catalog building.

Subclasses must implement extract_product() to map their source-specific
payload into a standardised CatalogProduct dict.
"""
from abc import abstractmethod
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from pipeline.lib.logging_setup import get_logger
from pipeline.lib.supabase_client import get_client, reset_client
from pipeline.lib.units import parse_package_weight
from pipeline.scrapers.base import BaseScraper

# Retry / batching constants (same as BaseScraper)
_BATCH_SIZE = 50
_RECYCLE_EVERY = 4000


class CatalogScraper(BaseScraper):
    """Base class for scrapers that populate the product catalog.

    Subclasses must define:
        scraper_name    — identifier stored in scraper_state
        source_type     — used as discovery_source in pack_variants
        catalog_source  — source_type written to variant_observations
    and implement:
        fetch()           — collect raw data (inherited from BaseScraper)
        source_id_for()   — unique ID per item (inherited)
        next_cursor()     — cursor logic (inherited)
        extract_product() — map raw payload to CatalogProduct fields
    """

    catalog_source = ""  # type: str  # e.g. "off_catalog", "kroger_catalog"

    @abstractmethod
    def extract_product(self, item):
        # type: (Dict[str, Any]) -> Optional[Dict[str, Any]]
        """Extract product catalog fields from a raw payload.

        Must return a dict with keys:
            brand          — str (required)
            name           — str (required)
            category       — str or None
            upc            — str or None
            size           — float or None
            size_unit      — str or None
            variant_name   — str (required)
            image_url      — str or None

        Return None to skip the item (e.g. missing required fields).
        """

    # ── Override store to write to catalog tables ──────────────────────────

    def store(self, items):
        # type: (List[Dict[str, Any]]) -> int
        """Upsert items into product_entities, pack_variants, and
        variant_observations instead of raw_items.

        Returns the count of new or updated pack_variants rows.
        """
        if not items:
            return 0

        client = get_client()
        today = date.today().isoformat()
        total = 0

        for i in range(0, len(items), _BATCH_SIZE):
            batch = items[i:i + _BATCH_SIZE]
            batch_num = i // _BATCH_SIZE

            if batch_num > 0 and batch_num % _RECYCLE_EVERY == 0:
                reset_client()
                client = get_client()
                self.log.info(
                    "Recycled connection at batch %d (%d items)",
                    batch_num, i,
                )

            for item in batch:
                product = self.extract_product(item)
                if product is None:
                    continue

                try:
                    stored = self._upsert_product(
                        client, product, self.source_id_for(item), today,
                    )
                    if stored:
                        total += 1
                except Exception as exc:
                    self.log.warning(
                        "Failed to catalog %s: %s",
                        self.source_id_for(item), str(exc)[:200],
                    )

        return total

    # ── Internal catalog upsert logic ──────────────────────────────────────

    def _upsert_product(self, client, product, discovery_id, today):
        # type: (Any, Dict[str, Any], str, str) -> bool
        """Find-or-create entity + variant, optionally add observation.

        Returns True if a pack_variant was created or updated.
        """
        brand = (product.get("brand") or "").strip()
        name = (product.get("name") or "").strip()
        if not brand or not name:
            return False

        # ── 1. Find or create product_entity ──────────────────────────
        entity_id = self._find_or_create_entity(
            client, brand, name,
            category=product.get("category"),
            image_url=product.get("image_url"),
        )
        if entity_id is None:
            return False

        # ── 2. Find or create pack_variant ────────────────────────────
        upc = (product.get("upc") or "").strip() or None
        variant_name = (product.get("variant_name") or name).strip()
        size = product.get("size")
        size_unit = product.get("size_unit")

        variant_id = self._find_or_create_variant(
            client, entity_id, upc, variant_name,
            size, size_unit, discovery_id,
        )
        if variant_id is None:
            return False

        # ── 3. Create observation if we have size data ────────────────
        if size is not None and size_unit:
            self._upsert_observation(
                client, variant_id, today, size, size_unit,
            )

        return True

    def _find_or_create_entity(self, client, brand, name, category=None, image_url=None):
        # type: (Any, str, str, Optional[str], Optional[str]) -> Optional[str]
        """Find entity by (brand, canonical_name) or create it. Returns UUID."""
        resp = (
            client.table("product_entities")
            .select("id")
            .eq("brand", brand)
            .eq("canonical_name", name)
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]

        row = {
            "brand": brand,
            "canonical_name": name,
        }  # type: Dict[str, Any]
        if category:
            row["category"] = category
        if image_url:
            row["image_url"] = image_url

        try:
            resp = (
                client.table("product_entities")
                .insert(row)
                .execute()
            )
            if resp.data:
                return resp.data[0]["id"]
        except Exception:
            # Race condition: another process created it — fetch
            resp = (
                client.table("product_entities")
                .select("id")
                .eq("brand", brand)
                .eq("canonical_name", name)
                .limit(1)
                .execute()
            )
            if resp.data:
                return resp.data[0]["id"]

        return None

    def _find_or_create_variant(
        self, client, entity_id, upc, variant_name,
        size, size_unit, discovery_id,
    ):
        # type: (Any, str, Optional[str], str, Optional[float], Optional[str], str) -> Optional[str]
        """Find variant by UPC or discovery key, or create it. Returns UUID."""
        # Try UPC first (globally unique)
        if upc:
            resp = (
                client.table("pack_variants")
                .select("id")
                .eq("upc", upc)
                .limit(1)
                .execute()
            )
            if resp.data:
                return resp.data[0]["id"]

        # Try discovery key
        resp = (
            client.table("pack_variants")
            .select("id")
            .eq("discovery_source", self.source_type)
            .eq("discovery_id", discovery_id)
            .limit(1)
            .execute()
        )
        if resp.data:
            return resp.data[0]["id"]

        # Create new variant
        row = {
            "entity_id": entity_id,
            "variant_name": variant_name,
            "discovery_source": self.source_type,
            "discovery_id": discovery_id,
            "is_active": True,
        }  # type: Dict[str, Any]
        if upc:
            row["upc"] = upc
        if size is not None:
            row["current_size"] = size
        if size_unit:
            row["size_unit"] = size_unit

        try:
            resp = (
                client.table("pack_variants")
                .insert(row)
                .execute()
            )
            if resp.data:
                return resp.data[0]["id"]
        except Exception:
            # Race: try UPC lookup again, then discovery key
            if upc:
                resp = (
                    client.table("pack_variants")
                    .select("id")
                    .eq("upc", upc)
                    .limit(1)
                    .execute()
                )
                if resp.data:
                    return resp.data[0]["id"]
            resp = (
                client.table("pack_variants")
                .select("id")
                .eq("discovery_source", self.source_type)
                .eq("discovery_id", discovery_id)
                .limit(1)
                .execute()
            )
            if resp.data:
                return resp.data[0]["id"]

        return None

    def _upsert_observation(self, client, variant_id, obs_date, size, size_unit):
        # type: (Any, str, str, float, str) -> None
        """Insert a variant_observation if one doesn't exist for this date+source.

        The unique index includes COALESCE(retailer, ''), so we check
        for an existing row first, then insert if missing.
        """
        try:
            existing = (
                client.table("variant_observations")
                .select("id")
                .eq("variant_id", variant_id)
                .eq("observed_date", obs_date)
                .eq("source_type", self.catalog_source)
                .is_("retailer", "null")
                .limit(1)
                .execute()
            )
            if existing.data:
                return

            client.table("variant_observations").insert({
                "variant_id": variant_id,
                "observed_date": obs_date,
                "source_type": self.catalog_source,
                "size": size,
                "size_unit": size_unit,
            }).execute()
        except Exception as exc:
            self.log.debug(
                "Observation insert failed for variant %s: %s",
                variant_id, str(exc)[:200],
            )
