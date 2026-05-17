"""Tests for the v2 oscillation/stability guards in analyze_kroger_changes."""
from pipeline.scripts.analyze_kroger_changes import detect_changes


def _obs(date, size, unit="oz", ppu=None, store="store_A"):
    return {
        "observed_date": date,
        "size": size,
        "size_unit": unit,
        "price": None,
        "price_per_unit": ppu,
        "store_location": store,
    }


def test_clean_size_decrease_is_detected():
    """A one-way shrink with ≥3 stable prior obs and stable post obs fires."""
    obs = [
        _obs("2026-01-01", 200, "g"),
        _obs("2026-01-08", 200, "g"),
        _obs("2026-01-15", 200, "g"),
        _obs("2026-01-22", 180, "g"),
        _obs("2026-01-29", 180, "g"),
    ]
    changes = detect_changes(obs)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "size_decrease"
    assert changes[0]["old_size"] == 200
    assert changes[0]["new_size"] == 180


def test_oscillation_is_filtered():
    """Sizes that alternate week-to-week are Kroger API noise, not real."""
    obs = [
        _obs("2026-01-01", 14, "oz"),
        _obs("2026-01-08", 8, "oz"),
        _obs("2026-01-15", 14, "oz"),
        _obs("2026-01-22", 8, "oz"),
        _obs("2026-01-29", 14, "oz"),
        _obs("2026-02-05", 8, "oz"),
    ]
    assert detect_changes(obs) == []


def test_revert_after_change_is_filtered():
    """Shrinks that revert within the lookback are flapping, not real."""
    obs = [
        _obs("2026-01-01", 200, "g"),
        _obs("2026-01-08", 200, "g"),
        _obs("2026-01-15", 200, "g"),
        _obs("2026-01-22", 180, "g"),  # shrink
        _obs("2026-01-29", 180, "g"),
        _obs("2026-02-05", 200, "g"),  # revert
    ]
    assert detect_changes(obs) == []


def test_insufficient_prior_stability_is_filtered():
    """First observation is the new size — not enough history to trust."""
    obs = [
        _obs("2026-01-01", 200, "g"),
        _obs("2026-01-08", 180, "g"),
        _obs("2026-01-15", 180, "g"),
        _obs("2026-01-22", 180, "g"),
    ]
    assert detect_changes(obs) == []


def test_cross_unit_family_is_filtered():
    """oz → fl oz is a representation flip, not shrinkflation."""
    obs = [
        _obs("2026-01-01", 33.4, "oz"),
        _obs("2026-01-08", 33.4, "oz"),
        _obs("2026-01-15", 33.4, "oz"),
        _obs("2026-01-22", 12.0, "fl oz"),
        _obs("2026-01-29", 12.0, "fl oz"),
    ]
    assert detect_changes(obs) == []


def test_cross_unit_inside_same_family_is_allowed():
    """kg → g (same mass family) should still detect a real shrink."""
    obs = [
        _obs("2026-01-01", 1.0, "kg"),
        _obs("2026-01-08", 1.0, "kg"),
        _obs("2026-01-15", 1.0, "kg"),
        _obs("2026-01-22", 900, "g"),
        _obs("2026-01-29", 900, "g"),
    ]
    changes = detect_changes(obs)
    assert len(changes) == 1
    assert changes[0]["change_type"] == "size_decrease"


def test_new_size_seen_earlier_is_filtered():
    """If the post-change size already appeared before, this is oscillation."""
    obs = [
        _obs("2026-01-01", 14, "oz"),
        _obs("2026-01-08", 8, "oz"),   # 8 oz appears early
        _obs("2026-01-15", 14, "oz"),
        _obs("2026-01-22", 14, "oz"),
        _obs("2026-01-29", 14, "oz"),
        _obs("2026-02-05", 8, "oz"),   # "transition" to a size we've already seen
        _obs("2026-02-12", 8, "oz"),
    ]
    assert detect_changes(obs) == []


def test_unparseable_observation_doesnt_break_run():
    """Observations missing size or with unknown unit are ignored, not errored."""
    obs = [
        _obs("2026-01-01", 200, "g"),
        _obs("2026-01-08", None, "g"),  # missing size
        _obs("2026-01-15", 200, "g"),
        _obs("2026-01-22", 200, "g"),
        _obs("2026-01-29", 200, "g"),
        _obs("2026-02-05", 180, "g"),
        _obs("2026-02-12", 180, "g"),
    ]
    changes = detect_changes(obs)
    assert len(changes) == 1
    assert changes[0]["new_size"] == 180
