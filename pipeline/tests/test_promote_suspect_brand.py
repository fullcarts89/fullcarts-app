"""is_suspect_brand catches AI extraction failures that would otherwise
land in product_entities as garbage rows ("Poor", "Unknown", empty string,
single letter, etc.). The data_quality_flags detector in promote_claims
relies on this predicate; tests lock the contract.
"""
import pytest

from pipeline.scripts.promote_claims import is_suspect_brand


class TestIsSuspectBrand:
    @pytest.mark.parametrize(
        "brand",
        [
            "Unknown", "Various", "Poor", "N/A", "Generic", "Misc",
        ],
    )
    def test_known_placeholders_flagged(self, brand):
        assert is_suspect_brand(brand) is True

    @pytest.mark.parametrize("brand", ["", " ", "a", "  a  "])
    def test_short_strings_flagged(self, brand):
        assert is_suspect_brand(brand) is True

    @pytest.mark.parametrize(
        "brand",
        [
            "Cadbury", "Mondelez International", "Nabisco",
            "M&S", "P&G", "abc",
            "3M",   # 2-char real brand (post-it, scotch tape parent)
            "AB",   # AB beer
        ],
    )
    def test_real_brands_pass(self, brand):
        assert is_suspect_brand(brand) is False

    def test_two_char_brand_passes(self):
        # Floor is at <2 chars; "ab" is on the boundary.
        assert is_suspect_brand("ab") is False

    def test_single_char_brand_flagged(self):
        # Single char is below the floor.
        assert is_suspect_brand("a") is True
