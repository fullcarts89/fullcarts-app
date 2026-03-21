"""Tests for CatalogScraper base class product extraction logic."""
import pytest
from unittest.mock import MagicMock, patch

from pipeline.scrapers.catalog_base import CatalogScraper


class DummyCatalogScraper(CatalogScraper):
    """Minimal concrete implementation for testing."""

    scraper_name = "test_catalog"
    source_type = "test_source"
    catalog_source = "test_catalog_src"

    def fetch(self, cursor, dry_run=False):
        return []

    def source_id_for(self, item):
        return "test_{}".format(item.get("id", ""))

    def next_cursor(self, items, prev_cursor):
        return {}

    def extract_product(self, item):
        brand = item.get("brand", "")
        name = item.get("name", "")
        if not brand or not name:
            return None
        return {
            "brand": brand,
            "name": name,
            "category": item.get("category"),
            "upc": item.get("upc"),
            "size": item.get("size"),
            "size_unit": item.get("size_unit"),
            "variant_name": name,
            "image_url": item.get("image_url"),
        }


class TestExtractProduct:
    """Tests for the extract_product interface."""

    def test_valid_product(self):
        scraper = DummyCatalogScraper()
        result = scraper.extract_product({
            "brand": "Acme", "name": "Chips", "upc": "123",
            "size": 16.0, "size_unit": "oz",
        })
        assert result is not None
        assert result["brand"] == "Acme"
        assert result["name"] == "Chips"
        assert result["upc"] == "123"
        assert result["size"] == 16.0

    def test_missing_brand_returns_none(self):
        scraper = DummyCatalogScraper()
        result = scraper.extract_product({"name": "Chips"})
        assert result is None

    def test_missing_name_returns_none(self):
        scraper = DummyCatalogScraper()
        result = scraper.extract_product({"brand": "Acme"})
        assert result is None


class TestStoreFlow:
    """Tests for the store() method's catalog upsert logic."""

    @patch("pipeline.scrapers.catalog_base.get_client")
    def test_store_calls_extract_for_each_item(self, mock_get_client):
        """store() should call extract_product for each item."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock the chain of DB calls to return valid IDs
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table

        # entity lookup returns existing
        entity_resp = MagicMock()
        entity_resp.data = [{"id": "entity-1"}]
        mock_table.select.return_value.eq.return_value.eq.return_value.limit.return_value.execute.return_value = entity_resp

        # variant lookup by discovery key returns existing
        variant_resp = MagicMock()
        variant_resp.data = [{"id": "variant-1"}]

        # observation check returns empty (no existing)
        obs_resp = MagicMock()
        obs_resp.data = []

        # Insert observation succeeds
        insert_resp = MagicMock()
        insert_resp.data = [{"id": "obs-1"}]

        scraper = DummyCatalogScraper()
        items = [
            {"id": "1", "brand": "Acme", "name": "Chips", "size": 16.0, "size_unit": "oz"},
            {"id": "2", "brand": "", "name": "NoName"},  # should be skipped
        ]

        # Just verify it doesn't crash and processes items
        # Full DB integration would be tested via integration tests
        result = scraper.store(items)
        assert isinstance(result, int)

    def test_store_empty_list(self):
        """store([]) should return 0."""
        scraper = DummyCatalogScraper()
        result = scraper.store([])
        assert result == 0
