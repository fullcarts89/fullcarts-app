"""Tests for the package weight parser and unit normalization.

Run with:
    python -m pytest pipeline/tests/test_units.py -v
"""
import pytest
from pipeline.lib.units import (
    convert_to_base,
    normalize_unit,
    parse_package_weight,
)


# ── parse_package_weight ──────────────────────────────────────────────────────


class TestParsePackageWeight:
    """parse_package_weight should handle USDA, Kroger, OFF, and edge-case formats."""

    # Simple patterns
    def test_simple_oz(self):
        assert parse_package_weight("16 oz") == (16.0, "oz")

    def test_simple_g(self):
        assert parse_package_weight("340 g") == (340.0, "g")

    def test_no_space(self):
        assert parse_package_weight("340g") == (340.0, "g")

    def test_uppercase(self):
        assert parse_package_weight("16 OZ") == (16.0, "oz")

    def test_decimal(self):
        assert parse_package_weight("9.25 oz") == (9.25, "oz")

    def test_fl_oz(self):
        assert parse_package_weight("12 fl oz") == (12.0, "fl oz")

    def test_fl_dot_oz(self):
        assert parse_package_weight("12 fl. oz") == (12.0, "fl oz")

    def test_kg(self):
        assert parse_package_weight("2.5 kg") == (2.5, "kg")

    def test_ml(self):
        assert parse_package_weight("500 ml") == (500.0, "ml")

    def test_liter(self):
        assert parse_package_weight("1.5 l") == (1.5, "l")

    def test_ct(self):
        assert parse_package_weight("24 ct") == (24.0, "ct")

    def test_count(self):
        assert parse_package_weight("12 count") == (12.0, "ct")

    def test_sheets(self):
        assert parse_package_weight("200 sheets") == (200.0, "sheets")

    def test_rolls(self):
        assert parse_package_weight("6 rolls") == (6.0, "rolls")

    # Compound: "1 LB 4 OZ"
    def test_compound_lb_oz(self):
        assert parse_package_weight("1 LB 4 OZ") == (20.0, "oz")

    def test_compound_lb_oz_lowercase(self):
        assert parse_package_weight("2 lb 8 oz") == (40.0, "oz")

    def test_compound_pounds_ounces(self):
        assert parse_package_weight("1 pound 6 ounces") == (22.0, "oz")

    # Slash-separated: "6 oz/170 g" → take first (US) value
    def test_slash_us_first(self):
        val, unit = parse_package_weight("6 oz/170 g")
        assert val == 6.0
        assert unit == "oz"

    def test_slash_metric_first(self):
        val, unit = parse_package_weight("170 g/6 oz")
        assert val == 170.0
        assert unit == "g"

    # Parenthetical: "6 oz (170g)" → take value before parens
    def test_paren_us_first(self):
        val, unit = parse_package_weight("6 oz (170g)")
        assert val == 6.0
        assert unit == "oz"

    def test_paren_metric_first(self):
        val, unit = parse_package_weight("170 g (6 oz)")
        assert val == 170.0
        assert unit == "g"

    # USDA FDC ISO unit codes
    def test_usda_onz(self):
        assert parse_package_weight("1.55 ONZ") == (1.55, "oz")

    def test_usda_lbr(self):
        assert parse_package_weight("1.25 LBR") == (1.25, "lb")

    def test_usda_grm(self):
        assert parse_package_weight("340 GRM") == (340.0, "g")

    def test_usda_kgm(self):
        assert parse_package_weight("1 KGM") == (1.0, "kg")

    def test_usda_flo(self):
        assert parse_package_weight("8 FLO") == (8.0, "fl oz")

    def test_usda_mlt(self):
        assert parse_package_weight("500 MLT") == (500.0, "ml")

    def test_usda_ltr(self):
        assert parse_package_weight("2 LTR") == (2.0, "l")

    def test_usda_gll(self):
        assert parse_package_weight("1 GLL") == (1.0, "gal")

    # Edge cases — empty, garbage, N/A
    def test_empty_string(self):
        assert parse_package_weight("") == (None, None)

    def test_none_string(self):
        # Technically invalid but defensive
        assert parse_package_weight("N/A") == (None, None)

    def test_whitespace_only(self):
        assert parse_package_weight("   ") == (None, None)

    def test_no_unit(self):
        # Just a number with no recognizable unit
        assert parse_package_weight("340") == (None, None)

    def test_text_only(self):
        assert parse_package_weight("unknown") == (None, None)


# ── normalize_unit ────────────────────────────────────────────────────────────


class TestNormalizeUnit:
    def test_oz(self):
        assert normalize_unit("oz") == "oz"

    def test_ounce(self):
        assert normalize_unit("ounce") == "oz"

    def test_ounces(self):
        assert normalize_unit("ounces") == "oz"

    def test_fl_oz(self):
        assert normalize_unit("fl oz") == "fl oz"

    def test_lb(self):
        assert normalize_unit("lb") == "lb"

    def test_lbs(self):
        assert normalize_unit("lbs") == "lb"

    def test_gram(self):
        assert normalize_unit("gram") == "g"

    def test_kg(self):
        assert normalize_unit("kg") == "kg"

    def test_count(self):
        assert normalize_unit("count") == "ct"

    def test_empty_default(self):
        assert normalize_unit("") == "oz"

    def test_uppercase(self):
        assert normalize_unit("OZ") == "oz"

    # USDA FDC codes
    def test_usda_onz(self):
        assert normalize_unit("onz") == "oz"

    def test_usda_lbr(self):
        assert normalize_unit("lbr") == "lb"

    def test_usda_grm(self):
        assert normalize_unit("grm") == "g"

    def test_usda_flo(self):
        assert normalize_unit("flo") == "fl oz"

    def test_usda_gll(self):
        assert normalize_unit("gll") == "gal"

    def test_fl_dot_oz_no_space(self):
        assert normalize_unit("fl.oz") == "fl oz"

    def test_double_space(self):
        assert normalize_unit("fl  oz") == "fl oz"


# ── convert_to_base ──────────────────────────────────────────────────────────


class TestConvertToBase:
    def test_kg_to_g(self):
        assert convert_to_base(2.5, "kg") == (2500.0, "g")

    def test_lb_to_oz(self):
        assert convert_to_base(1.0, "lb") == (16.0, "oz")

    def test_l_to_ml(self):
        assert convert_to_base(1.5, "l") == (1500.0, "ml")

    def test_gal_to_fl_oz(self):
        assert convert_to_base(1.0, "gal") == (128.0, "fl oz")

    def test_oz_stays(self):
        assert convert_to_base(16.0, "oz") == (16.0, "oz")

    def test_g_stays(self):
        assert convert_to_base(340.0, "g") == (340.0, "g")
