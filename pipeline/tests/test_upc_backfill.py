"""Tests for UPC backfill scraper."""
import pytest
from unittest.mock import patch, MagicMock

from pipeline.scrapers.upc_backfill import UpcBackfillScraper


class TestUpcBackfillSourceId:
    """Verify source_id generation for backfill items."""

    def test_source_id_format(self):
        scraper = UpcBackfillScraper()
        scraper._today = "2026-03-22"
        item = {"_upc": "012345678901", "_found": True, "_raw_product": {}}
        assert scraper.source_id_for(item) == "off_backfill_012345678901_2026-03-22"

    def test_source_url(self):
        scraper = UpcBackfillScraper()
        item = {"_upc": "012345678901", "_found": True, "_raw_product": {}}
        assert scraper.source_url_for(item) == (
            "https://world.openfoodfacts.org/product/012345678901"
        )

    def test_source_date(self):
        scraper = UpcBackfillScraper()
        scraper._today = "2026-03-22"
        item = {"_upc": "012345678901", "_found": True, "_raw_product": {}}
        assert scraper.source_date_for(item) == "2026-03-22"


class TestUpcBackfillNextCursor:
    def test_next_cursor_counts(self):
        scraper = UpcBackfillScraper()
        scraper._today = "2026-03-22"
        items = [
            {"_upc": "111", "_found": True, "_raw_product": {"code": "111"}},
            {"_upc": "222", "_found": False, "_raw_product": {}},
            {"_upc": "333", "_found": True, "_raw_product": {"code": "333"}},
        ]
        cursor = scraper.next_cursor(items, {})
        assert cursor["last_backfill_date"] == "2026-03-22"
        assert cursor["upcs_checked"] == 3
        assert cursor["upcs_found"] == 2


class TestUpcBackfillParseOffSize:
    def test_numeric_fields(self):
        scraper = UpcBackfillScraper()
        product = {"product_quantity": "340", "product_quantity_unit": "g"}
        size, unit = scraper._parse_off_size(product)
        assert size == 340.0
        assert unit == "g"

    def test_freetext_quantity(self):
        scraper = UpcBackfillScraper()
        product = {"quantity": "12 oz"}
        size, unit = scraper._parse_off_size(product)
        assert size == 12.0
        assert unit == "oz"

    def test_empty_product(self):
        scraper = UpcBackfillScraper()
        size, unit = scraper._parse_off_size({})
        assert size is None
        assert unit is None


class TestUpcBackfillCliRegistration:
    """Verify the scraper is properly registered in cli.py."""

    def test_upc_backfill_in_scraper_map(self):
        from pipeline.cli import SCRAPER_MAP
        assert "upc_backfill" in SCRAPER_MAP
        assert SCRAPER_MAP["upc_backfill"] == (
            "pipeline.scrapers.upc_backfill:UpcBackfillScraper"
        )

    def test_can_import_scraper(self):
        """Verify the lazy import path resolves."""
        from pipeline.scrapers.upc_backfill import UpcBackfillScraper
        scraper = UpcBackfillScraper()
        assert scraper.scraper_name == "upc_backfill"
        assert scraper.source_type == "openfoodfacts"
