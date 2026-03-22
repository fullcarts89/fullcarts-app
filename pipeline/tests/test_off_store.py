"""Tests for OpenFoodFactsScraper.store() payload isolation."""
import pytest
from unittest.mock import patch, MagicMock
from datetime import date

from pipeline.scrapers.openfoodfacts import OpenFoodFactsScraper


class TestOffStoreRawPayload:
    """Verify that store() writes only the product dict as raw_payload,
    not the internal _upc/_found/_raw_product envelope."""

    @patch("pipeline.scrapers.openfoodfacts.get_client")
    def test_raw_payload_contains_only_product_dict(self, mock_get_client):
        """The raw_payload field should be the product dict, not the envelope."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock the upsert chain
        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_upsert = MagicMock()
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = MagicMock(data=[{"id": 1}])

        scraper = OpenFoodFactsScraper()
        scraper._today = "2026-03-22"

        items = [
            {
                "_upc": "012345678901",
                "_found": True,
                "_raw_product": {
                    "code": "012345678901",
                    "product_name": "Test Chips",
                    "brands": "TestBrand",
                },
            },
        ]

        # Call the internal _store_raw_items (which store() delegates to)
        scraper._store_raw_items(items)

        # Verify upsert was called
        mock_table.upsert.assert_called_once()
        rows = mock_table.upsert.call_args[0][0]
        assert len(rows) == 1

        payload = rows[0]["raw_payload"]
        # Should be the product dict, NOT the envelope
        assert "_upc" not in payload
        assert "_found" not in payload
        assert "_raw_product" not in payload
        assert payload["code"] == "012345678901"
        assert payload["product_name"] == "Test Chips"

    @patch("pipeline.scrapers.openfoodfacts.get_client")
    def test_not_found_item_stores_empty_payload(self, mock_get_client):
        """Items not found on OFF should store an empty dict as payload."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_upsert = MagicMock()
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = MagicMock(data=[{"id": 1}])

        scraper = OpenFoodFactsScraper()
        scraper._today = "2026-03-22"

        items = [
            {
                "_upc": "999999999999",
                "_found": False,
                "_raw_product": {},
            },
        ]

        scraper._store_raw_items(items)

        rows = mock_table.upsert.call_args[0][0]
        assert rows[0]["raw_payload"] == {}

    @patch("pipeline.scrapers.openfoodfacts.get_client")
    def test_source_id_uses_envelope_upc(self, mock_get_client):
        """source_id should be derived from the envelope _upc, not the payload."""
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        mock_table = MagicMock()
        mock_client.table.return_value = mock_table
        mock_upsert = MagicMock()
        mock_table.upsert.return_value = mock_upsert
        mock_upsert.execute.return_value = MagicMock(data=[])

        scraper = OpenFoodFactsScraper()
        scraper._today = "2026-03-22"

        items = [
            {
                "_upc": "012345678901",
                "_found": True,
                "_raw_product": {"code": "012345678901"},
            },
        ]

        scraper._store_raw_items(items)

        rows = mock_table.upsert.call_args[0][0]
        assert rows[0]["source_id"] == "012345678901_2026-03-22"
