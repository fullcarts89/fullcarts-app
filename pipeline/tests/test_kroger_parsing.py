"""Tests for Kroger source_id parsing in _load_raw_item_ids."""
import pytest


class TestKrogerSourceIdParsing:
    """Verify the rsplit-based source_id parsing logic."""

    @staticmethod
    def _parse_source_id(sid):
        """Replicate the parsing logic from KrogerScraper._load_raw_item_ids."""
        remainder = sid[len("kroger_"):]
        rest, store_id = remainder.rsplit("_", 1)
        upc, _date = rest.rsplit("_", 1)
        return upc, store_id

    def test_standard_upc(self):
        upc, store = self._parse_source_id(
            "kroger_012345678901_2026-03-22_01400376"
        )
        assert upc == "012345678901"
        assert store == "01400376"

    def test_short_upc(self):
        upc, store = self._parse_source_id(
            "kroger_12345_2026-03-22_01400376"
        )
        assert upc == "12345"
        assert store == "01400376"

    def test_different_store_id(self):
        upc, store = self._parse_source_id(
            "kroger_012345678901_2026-01-01_01400943"
        )
        assert upc == "012345678901"
        assert store == "01400943"

    def test_upc_with_underscore(self):
        """UPCs with underscores should still parse correctly."""
        upc, store = self._parse_source_id(
            "kroger_012_345_2026-03-22_01400376"
        )
        assert upc == "012_345"
        assert store == "01400376"

    def test_date_preserved_in_middle(self):
        """Date (YYYY-MM-DD) sits between UPC and store_id."""
        upc, store = self._parse_source_id(
            "kroger_9999999999999_2025-12-31_88888888"
        )
        assert upc == "9999999999999"
        assert store == "88888888"
