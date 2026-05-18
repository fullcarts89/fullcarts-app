"""Unit tests for backfill_entity_images helpers.

The DB-touching paths can't be exercised without a Supabase instance,
so we test only the pure helpers — currently just the EAN-13
normalizer that feeds the OFF live fallback.
"""
import pytest

from pipeline.scripts.backfill_entity_images import _normalize_to_ean13


class TestNormalizeToEan13:
    def test_ean13_passes_through(self):
        assert _normalize_to_ean13("7622210000095") == "7622210000095"

    def test_upca_12digit_gets_zero_prefix(self):
        # US-issued UPC-A codes are 12 digits — OFF expects 13.
        assert _normalize_to_ean13("050000000017") == "0050000000017"

    def test_none_input(self):
        assert _normalize_to_ean13(None) is None

    def test_empty_string(self):
        assert _normalize_to_ean13("") is None

    def test_whitespace_trimmed(self):
        assert _normalize_to_ean13("  7622210000095  ") == "7622210000095"

    def test_synthetic_claim_key_rejected(self):
        # promote_claims.py creates synthetic UPCs like "CLAIM-abc123"
        # when no real barcode is known — these must not trigger
        # OFF API calls.
        assert _normalize_to_ean13("CLAIM-abc123") is None
        assert _normalize_to_ean13("REDDIT-xyz") is None

    def test_short_numeric_rejected(self):
        # EAN-8 codes exist but US food products almost never use them;
        # short numeric strings are usually parsing noise.
        assert _normalize_to_ean13("12345678") is None
        assert _normalize_to_ean13("123") is None

    def test_long_numeric_rejected(self):
        # 14+ digits — likely garbage (GTIN-14 isn't OFF's primary key).
        assert _normalize_to_ean13("12345678901234") is None

    def test_non_numeric_in_otherwise_valid_length_rejected(self):
        # 13 chars but with letters — rejected, not silently passed.
        assert _normalize_to_ean13("76222100000aa") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
