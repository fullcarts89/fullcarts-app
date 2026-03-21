"""Tests for catalog variance detection logic."""
import pytest

from pipeline.scripts.analyze_catalog_variance import detect_changes


def _obs(size, unit, date, source_type="off_catalog"):
    """Helper to build an observation dict."""
    return {
        "variant_id": "v-1",
        "observed_date": date,
        "size": size,
        "size_unit": unit,
        "source_type": source_type,
    }


class TestDetectChanges:
    """Tests for the detect_changes() pure function."""

    def test_no_change(self):
        """Same size across observations -> no change detected."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(16.0, "oz", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_size_decrease(self):
        """16oz -> 14oz is a 12.5% decrease."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        assert result["pct_change"] == -12.5
        assert result["old_size"] == 16.0
        assert result["new_size"] == 14.0
        assert result["old_date"] == "2025-01-15"
        assert result["new_date"] == "2025-03-15"

    def test_size_increase_not_flagged(self):
        """Increases are not flagged (only decreases >= threshold)."""
        obs = [
            _obs(14.0, "oz", "2025-01-15"),
            _obs(16.0, "oz", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_below_threshold(self):
        """1.25% decrease is below the 2% threshold."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(15.8, "oz", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_at_threshold(self):
        """Exactly 2% decrease -> flagged (threshold is <=)."""
        obs = [
            _obs(100.0, "g", "2025-01-15"),
            _obs(98.0, "g", "2025-03-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        assert result["pct_change"] == -2.0

    def test_just_below_threshold(self):
        """1.99% decrease -> not flagged."""
        obs = [
            _obs(100.0, "g", "2025-01-15"),
            _obs(98.01, "g", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_unit_conversion_lb_to_oz(self):
        """1 lb (=16 oz) -> 14 oz should detect a decrease."""
        obs = [
            _obs(1.0, "lb", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        assert result["pct_change"] == -12.5

    def test_incompatible_units(self):
        """oz vs ml -> cannot compare -> no change."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(400.0, "ml", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_three_observations_returns_latest(self):
        """Multiple decreases -> returns the most recent one."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
            _obs(12.0, "oz", "2025-06-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        # Should be the latest change (14->12)
        assert result["old_date"] == "2025-03-15"
        assert result["new_date"] == "2025-06-15"
        assert result["pct_change"] == pytest.approx(-14.29, abs=0.01)

    def test_zero_old_size_skipped(self):
        """Old size = 0 -> skip (avoid division by zero)."""
        obs = [
            _obs(0.0, "oz", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_none_size_skipped(self):
        """None size -> skip."""
        obs = [
            _obs(None, "oz", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
        ]
        assert detect_changes(obs) is None

    def test_single_observation(self):
        """Single observation -> no comparison possible."""
        obs = [_obs(16.0, "oz", "2025-01-15")]
        assert detect_changes(obs) is None

    def test_empty_observations(self):
        """Empty list -> None."""
        assert detect_changes([]) is None

    def test_source_type_preserved(self):
        """The source_type from the new observation is carried through."""
        obs = [
            _obs(16.0, "oz", "2025-01-15", source_type="kroger_catalog"),
            _obs(14.0, "oz", "2025-03-15", source_type="kroger_catalog"),
        ]
        result = detect_changes(obs)
        assert result is not None
        assert result["source_type"] == "kroger_catalog"

    def test_kg_to_g_conversion(self):
        """1 kg (=1000g) -> 900g is a 10% decrease."""
        obs = [
            _obs(1.0, "kg", "2025-01-15"),
            _obs(900.0, "g", "2025-03-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        assert result["pct_change"] == -10.0

    def test_decrease_then_no_change_returns_first(self):
        """16->14 then 14->14 -> returns the decrease."""
        obs = [
            _obs(16.0, "oz", "2025-01-15"),
            _obs(14.0, "oz", "2025-03-15"),
            _obs(14.0, "oz", "2025-06-15"),
        ]
        result = detect_changes(obs)
        assert result is not None
        # The latest qualifying change is the 16->14 one
        assert result["old_date"] == "2025-01-15"
        assert result["new_date"] == "2025-03-15"
        assert result["pct_change"] == -12.5
