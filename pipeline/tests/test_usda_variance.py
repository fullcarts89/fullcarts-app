"""Tests for the USDA variance detection logic."""
import pytest

from pipeline.scrapers.usda_variance import detect_changes


def _obs(upc, size, unit, date, brand="TestBrand", desc="TestProduct"):
    """Helper to build an observation dict."""
    return {
        "gtin_upc": upc,
        "brand_owner": brand,
        "description": desc,
        "_size": size,
        "_size_unit": unit,
        "source_date": date,
    }


class TestDetectChanges:
    """Tests for the detect_changes() pure function."""

    def test_no_change(self):
        """Same size across releases → no changes detected."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 16.0, "oz", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_size_decrease(self):
        """16oz → 14oz is a 12.5% decrease (shrinkflation)."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["direction"] == "decrease"
        assert result[0]["pct_change"] == -12.5
        assert result[0]["old_size"] == 16.0
        assert result[0]["new_size"] == 14.0
        assert result[0]["old_date"] == "2022-10-28"
        assert result[0]["new_date"] == "2023-04-20"

    def test_size_increase(self):
        """14oz → 16oz is an increase."""
        obs = [
            _obs("123", 14.0, "oz", "2022-10-28"),
            _obs("123", 16.0, "oz", "2023-04-20"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["direction"] == "increase"
        assert result[0]["pct_change"] == pytest.approx(14.29, abs=0.01)

    def test_below_threshold(self):
        """1.25% change is below the 2% threshold → no detection."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 15.8, "oz", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_at_threshold(self):
        """Exactly 2% change → not flagged (threshold is >2%)."""
        obs = [
            _obs("123", 100.0, "g", "2022-10-28"),
            _obs("123", 98.0, "g", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_just_above_threshold(self):
        """2.1% change → flagged."""
        obs = [
            _obs("123", 100.0, "g", "2022-10-28"),
            _obs("123", 97.9, "g", "2023-04-20"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["direction"] == "decrease"

    def test_unit_conversion_lb_to_oz(self):
        """1 lb (=16 oz) → 14 oz should detect a decrease."""
        obs = [
            _obs("123", 1.0, "lb", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["direction"] == "decrease"
        assert result[0]["pct_change"] == -12.5

    def test_incompatible_units(self):
        """oz vs ml → cannot compare → no changes."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 400.0, "ml", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_three_releases(self):
        """Three releases: 16→14 (decrease) then 14→14 (no change)."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
            _obs("123", 14.0, "oz", "2023-10-26"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["old_date"] == "2022-10-28"
        assert result[0]["new_date"] == "2023-04-20"

    def test_three_releases_two_changes(self):
        """Three releases: 16→14 then 14→12 — two decreases."""
        obs = [
            _obs("123", 16.0, "oz", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
            _obs("123", 12.0, "oz", "2023-10-26"),
        ]
        result = detect_changes(obs)
        assert len(result) == 2
        assert result[0]["pct_change"] == -12.5
        assert result[1]["pct_change"] == pytest.approx(-14.29, abs=0.01)

    def test_zero_size(self):
        """Old size is 0 → skip (avoid division by zero)."""
        obs = [
            _obs("123", 0.0, "oz", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_single_observation(self):
        """Only one observation → no comparison possible."""
        obs = [_obs("123", 16.0, "oz", "2022-10-28")]
        assert detect_changes(obs) == []

    def test_empty_observations(self):
        """Empty list → no changes."""
        assert detect_changes([]) == []

    def test_none_size(self):
        """None size values → skip."""
        obs = [
            _obs("123", None, "oz", "2022-10-28"),
            _obs("123", 14.0, "oz", "2023-04-20"),
        ]
        assert detect_changes(obs) == []

    def test_preserves_metadata(self):
        """Detected changes carry brand/product/UPC metadata."""
        obs = [
            _obs("00012345", 16.0, "oz", "2022-10-28",
                 brand="Acme Corp", desc="Acme Chips"),
            _obs("00012345", 14.0, "oz", "2023-04-20",
                 brand="Acme Corp", desc="Acme Chips"),
        ]
        result = detect_changes(obs)
        assert result[0]["gtin_upc"] == "00012345"
        assert result[0]["brand_owner"] == "Acme Corp"
        assert result[0]["description"] == "Acme Chips"

    def test_kg_to_g_conversion(self):
        """1 kg (=1000g) → 900g is a 10% decrease."""
        obs = [
            _obs("123", 1.0, "kg", "2022-10-28"),
            _obs("123", 900.0, "g", "2023-04-20"),
        ]
        result = detect_changes(obs)
        assert len(result) == 1
        assert result[0]["direction"] == "decrease"
        assert result[0]["pct_change"] == -10.0
