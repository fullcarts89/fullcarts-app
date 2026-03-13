"""Tests for the USDA turnover detection logic."""
import pytest

from pipeline.scrapers.usda_turnover import (
    detect_turnover_changes,
    normalize_brand,
    normalize_description,
    strip_size_from_description,
)


# ── normalize_brand tests ─────────────────────────────────────────────────


class TestNormalizeBrand:
    """Tests for brand name normalization."""

    def test_strip_inc(self):
        assert normalize_brand("FRITO-LAY, INC.") == "frito lay"

    def test_strip_llc(self):
        assert normalize_brand("Some Brand LLC") == "some brand"

    def test_strip_company(self):
        assert normalize_brand("Kellogg's Company") == "kelloggs"

    def test_strip_corp(self):
        assert normalize_brand("Mondelez Corp.") == "mondelez"

    def test_strip_corporation(self):
        assert normalize_brand("PepsiCo Corporation") == "pepsico"

    def test_strip_leading_the(self):
        assert normalize_brand("THE COCA-COLA COMPANY") == "coca cola"
        # Hyphen becomes space, "COMPANY" suffix stripped

    def test_strip_ltd(self):
        assert normalize_brand("Nestle Ltd.") == "nestle"

    def test_lowercase(self):
        assert normalize_brand("General Mills") == "general mills"

    def test_collapse_whitespace(self):
        assert normalize_brand("  Some   Brand  ") == "some brand"

    def test_strip_punctuation(self):
        assert normalize_brand("Ben & Jerry's, Inc.") == "ben jerrys"

    def test_empty_string(self):
        assert normalize_brand("") == ""

    def test_only_suffix(self):
        # Edge case: brand is just "Inc."
        assert normalize_brand("Inc.") == ""

    def test_multiple_suffixes(self):
        assert normalize_brand("Acme Foods Co., Inc.") == "acme foods"


# ── normalize_description tests ───────────────────────────────────────────


class TestNormalizeDescription:
    """Tests for product description/brand_name normalization."""

    def test_basic(self):
        assert normalize_description("LAY'S CLASSIC POTATO CHIPS") == "lays classic potato chips"

    def test_lowercase(self):
        assert normalize_description("HONEY NUT CHEERIOS") == "honey nut cheerios"

    def test_strip_punctuation(self):
        assert normalize_description("100% Whole Wheat Bread") == "100 whole wheat bread"

    def test_collapse_whitespace(self):
        assert normalize_description("  Honey-Nut  Cheerios  ") == "honey nut cheerios"

    def test_empty(self):
        assert normalize_description("") == ""

    def test_special_chars(self):
        assert normalize_description("Diet Coke(R)") == "diet coker"


# ── strip_size_from_description tests ─────────────────────────────────────


class TestStripSizeFromDescription:
    """Tests for stripping size/packaging info from food.csv descriptions."""

    def test_ounce_and_packaging(self):
        assert (
            strip_size_from_description(
                "Lay's Classic Potato Chips 10 Ounce Plastic Bag"
            )
            == "Lay's Classic Potato Chips"
        )

    def test_fraction_ounce(self):
        assert (
            strip_size_from_description(
                "Lay's Classic Potato Chips 13 3/4 Ounce  Party Size Bag"
            )
            == "Lay's Classic Potato Chips"
        )

    def test_decimal_ounce(self):
        assert (
            strip_size_from_description(
                "Lay's Classic Potato Chips 1.125 Ounce Plastic Bag"
            )
            == "Lay's Classic Potato Chips"
        )

    def test_fl_oz(self):
        assert (
            strip_size_from_description("WESSON Canola Oil 48 FL OZ")
            == "WESSON Canola Oil"
        )

    def test_count(self):
        assert (
            strip_size_from_description("Hershey's Soft Donut Bites 72 Count")
            == "Hershey's Soft Donut Bites"
        )

    def test_different_counts_same_result(self):
        a = strip_size_from_description("Hershey's Soft Donut Bites 72 Count")
        b = strip_size_from_description("Hershey's Soft Donut Bites 18 Count")
        assert a == b

    def test_n_pack(self):
        assert (
            strip_size_from_description(
                "Betty Crocker Hershey's Triple Chocolate Brownie Mix 4 Pack"
            )
            == "Betty Crocker Hershey's Triple Chocolate Brownie Mix"
        )

    def test_no_size_unchanged(self):
        assert (
            strip_size_from_description("CAMPBELL'S SOUP TOMATO")
            == "CAMPBELL'S SOUP TOMATO"
        )

    def test_standard_bar_preserved(self):
        """'STANDARD BAR' is product identity, not packaging."""
        assert (
            strip_size_from_description("HERSHEYS MILK CHOCOLATE STANDARD BAR")
            == "HERSHEYS MILK CHOCOLATE STANDARD BAR"
        )

    def test_party_size(self):
        assert (
            strip_size_from_description("DORITOS COOL RANCH Party Size")
            == "DORITOS COOL RANCH"
        )

    def test_family_size(self):
        assert (
            strip_size_from_description("CHEERIOS Family Size Box")
            == "CHEERIOS"
        )

    def test_empty(self):
        assert strip_size_from_description("") == ""

    def test_leading_number_preserved(self):
        """'100%' at start is not a size pattern."""
        assert (
            strip_size_from_description(
                "100% LEMON JUICE FROM CONCENTRATE, LEMON"
            )
            == "100% LEMON JUICE FROM CONCENTRATE, LEMON"
        )

    def test_grams(self):
        assert (
            strip_size_from_description("DARK CHOCOLATE BAR 100 grams")
            == "DARK CHOCOLATE BAR"
        )


# ── detect_turnover_changes tests ─────────────────────────────────────────


def _entry(upc, release_date, size, unit="oz", brand_owner="TestBrand",
           brand_name="TestProduct", fdc_id="1"):
    """Helper to build an entry dict."""
    return {
        "upc": upc,
        "release_date": release_date,
        "size": size,
        "unit": unit,
        "brand_owner": brand_owner,
        "brand_name": brand_name,
        "fdc_id": fdc_id,
    }


def _group(entries, norm_brand="testbrand", norm_name="testproduct",
           base_unit="oz", category="Snacks"):
    """Helper to build a product group dict."""
    return {
        "brand_owner": entries[0]["brand_owner"] if entries else "TestBrand",
        "brand_name": entries[0]["brand_name"] if entries else "TestProduct",
        "category": category,
        "norm_brand": norm_brand,
        "norm_name": norm_name,
        "base_unit": base_unit,
        "entries": entries,
    }


class TestDetectTurnoverChanges:
    """Tests for the detect_turnover_changes() pure function."""

    def test_empty_entries(self):
        """No entries -> no changes."""
        g = _group([])
        assert detect_turnover_changes(g) == []

    def test_single_entry(self):
        """One entry -> no comparison possible."""
        g = _group([_entry("UPC1", "2022-10-28", 16.0)])
        assert detect_turnover_changes(g) == []

    def test_same_upc_across_releases(self):
        """Same UPC in both releases -> not turnover, no detection."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC1", "2023-04-20", 14.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_upc_turnover_with_decrease(self):
        """UPC1 disappears, UPC2 appears with smaller size -> detected."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC2", "2023-04-20", 14.0),
        ])
        result = detect_turnover_changes(g)
        assert len(result) == 1
        assert result[0]["old_upc"] == "UPC1"
        assert result[0]["new_upc"] == "UPC2"
        assert result[0]["old_size"] == 16.0
        assert result[0]["new_size"] == 14.0
        assert result[0]["pct_change"] == -12.5
        assert result[0]["old_date"] == "2022-10-28"
        assert result[0]["new_date"] == "2023-04-20"
        assert result[0]["category"] == "Snacks"

    def test_upc_turnover_with_increase_ignored(self):
        """UPC turnover where new product is BIGGER -> not shrinkflation."""
        g = _group([
            _entry("UPC1", "2022-10-28", 14.0),
            _entry("UPC2", "2023-04-20", 16.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_below_min_threshold_ignored(self):
        """2% decrease is below 3% min threshold -> no detection."""
        g = _group([
            _entry("UPC1", "2022-10-28", 100.0, "g"),
            _entry("UPC2", "2023-04-20", 98.0, "g"),
        ], base_unit="g")
        assert detect_turnover_changes(g) == []

    def test_above_max_threshold_ignored(self):
        """50% decrease is above 40% max threshold -> likely data error."""
        g = _group([
            _entry("UPC1", "2022-10-28", 100.0, "g"),
            _entry("UPC2", "2023-04-20", 50.0, "g"),
        ], base_unit="g")
        assert detect_turnover_changes(g) == []

    def test_just_above_min_threshold(self):
        """3.1% decrease -> detected."""
        g = _group([
            _entry("UPC1", "2022-10-28", 100.0, "g"),
            _entry("UPC2", "2023-04-20", 96.9, "g"),
        ], base_unit="g")
        result = detect_turnover_changes(g)
        assert len(result) == 1

    def test_at_max_threshold_edge(self):
        """40% decrease -> detected (boundary)."""
        g = _group([
            _entry("UPC1", "2022-10-28", 100.0, "g"),
            _entry("UPC2", "2023-04-20", 60.0, "g"),
        ], base_unit="g")
        result = detect_turnover_changes(g)
        assert len(result) == 1

    def test_unit_conversion(self):
        """1 lb old -> 14 oz new -> 12.5% decrease detected."""
        g = _group([
            _entry("UPC1", "2022-10-28", 1.0, "lb"),
            _entry("UPC2", "2023-04-20", 14.0, "oz"),
        ], base_unit="oz")
        result = detect_turnover_changes(g)
        assert len(result) == 1
        assert result[0]["pct_change"] == -12.5

    def test_incompatible_units_ignored(self):
        """oz vs ml -> can't compare -> no detection."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0, "oz"),
            _entry("UPC2", "2023-04-20", 400.0, "ml"),
        ])
        assert detect_turnover_changes(g) == []

    def test_three_releases_middle_stays(self):
        """UPC1 in R1+R2, UPC2 in R3 -> turnover in R2->R3 only."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC1", "2023-04-20", 16.0),
            _entry("UPC2", "2023-10-26", 14.0),
        ])
        result = detect_turnover_changes(g)
        assert len(result) == 1
        assert result[0]["old_date"] == "2023-04-20"
        assert result[0]["new_date"] == "2023-10-26"

    def test_overlapping_upcs_no_turnover(self):
        """Both UPCs present in same release -> not turnover."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC2", "2022-10-28", 14.0),
            _entry("UPC1", "2023-04-20", 16.0),
            _entry("UPC2", "2023-04-20", 14.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_multiple_arrivals_for_one_departure(self):
        """One UPC leaves, two arrive -> flags each decrease in range."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC2", "2023-04-20", 14.0),
            _entry("UPC3", "2023-04-20", 12.0),
        ])
        result = detect_turnover_changes(g)
        # UPC2 (14oz, -12.5%) and UPC3 (12oz, -25%) are both in range
        assert len(result) == 2
        sizes = sorted([r["new_size"] for r in result])
        assert sizes == [12.0, 14.0]

    def test_zero_old_size_skipped(self):
        """Old size is 0 -> skip to avoid div by zero."""
        g = _group([
            _entry("UPC1", "2022-10-28", 0.0),
            _entry("UPC2", "2023-04-20", 14.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_preserves_metadata(self):
        """Change records carry brand, name, category, FDC IDs."""
        g = _group([
            _entry("UPC_OLD", "2022-10-28", 16.0,
                   brand_owner="Acme Corp", brand_name="Acme Chips",
                   fdc_id="111"),
            _entry("UPC_NEW", "2023-04-20", 14.0,
                   brand_owner="Acme Corp", brand_name="Acme Chips",
                   fdc_id="222"),
        ], norm_brand="acme", norm_name="acme chips", category="Snacks")
        result = detect_turnover_changes(g)
        assert len(result) == 1
        r = result[0]
        assert r["brand_owner"] == "Acme Corp"
        assert r["brand_name"] == "Acme Chips"
        assert r["category"] == "Snacks"
        assert r["old_fdc_id"] == "111"
        assert r["new_fdc_id"] == "222"
        assert r["norm_brand"] == "acme"
        assert r["norm_name"] == "acme chips"

    def test_gradual_turnover_across_four_releases(self):
        """UPC1(R1) -> UPC2(R2) -> UPC3(R3) -> UPC4(R4), each smaller."""
        g = _group([
            _entry("UPC1", "2022-10-28", 20.0),
            _entry("UPC2", "2023-04-20", 18.0),
            _entry("UPC3", "2023-10-26", 16.0),
            _entry("UPC4", "2024-04-18", 14.0),
        ])
        result = detect_turnover_changes(g)
        assert len(result) == 3
        dates = [(r["old_date"], r["new_date"]) for r in result]
        assert ("2022-10-28", "2023-04-20") in dates
        assert ("2023-04-20", "2023-10-26") in dates
        assert ("2023-10-26", "2024-04-18") in dates

    def test_partial_overlap(self):
        """UPC1 in R1+R2, UPC2 in R2+R3.  Overlap in R2 -> no turnover."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC1", "2023-04-20", 16.0),
            _entry("UPC2", "2023-04-20", 14.0),
            _entry("UPC2", "2023-10-26", 14.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_single_release_multiple_upcs(self):
        """All UPCs in same release -> no turnover."""
        g = _group([
            _entry("UPC1", "2022-10-28", 16.0),
            _entry("UPC2", "2022-10-28", 14.0),
        ])
        assert detect_turnover_changes(g) == []

    def test_custom_thresholds(self):
        """Can override min/max thresholds."""
        g = _group([
            _entry("UPC1", "2022-10-28", 100.0, "g"),
            _entry("UPC2", "2023-04-20", 98.0, "g"),
        ], base_unit="g")
        # Default min_pct=3.0 would skip 2% change
        assert detect_turnover_changes(g) == []
        # But with min_pct=1.0, it's detected
        result = detect_turnover_changes(g, min_pct=1.0)
        assert len(result) == 1
