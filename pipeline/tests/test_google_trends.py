"""Aggregation tests for the Google Trends weekly→monthly collapse.

Pins the fix for the upsert-collision bug: Google's `today 5-y` window
sometimes serves weekly buckets, and snapping each to month-start without
aggregating duplicates the (keyword, geo, observation_date) key inside a
single upsert batch.
"""
from datetime import date, datetime, timezone

from pipeline.scrapers.google_trends import aggregate_timeline_to_monthly


def _ts(year, month, day):
    return str(int(datetime(year, month, day, tzinfo=timezone.utc).timestamp()))


def _row(year, month, day, value):
    return {"time": _ts(year, month, day), "value": [value]}


def test_weekly_points_collapse_to_one_row_per_month():
    """Four weekly points inside Jan 2026 must emit a single month-start row."""
    timeline = [
        _row(2026, 1, 4, 10),
        _row(2026, 1, 11, 20),
        _row(2026, 1, 18, 30),
        _row(2026, 1, 25, 40),
    ]
    out = aggregate_timeline_to_monthly(timeline)
    assert out == [(date(2026, 1, 1), 25.0)]


def test_monthly_points_pass_through_unchanged():
    """When Google already serves monthly buckets, values are not averaged away."""
    timeline = [
        _row(2026, 1, 1, 42),
        _row(2026, 2, 1, 50),
        _row(2026, 3, 1, 58),
    ]
    out = aggregate_timeline_to_monthly(timeline)
    assert out == [
        (date(2026, 1, 1), 42.0),
        (date(2026, 2, 1), 50.0),
        (date(2026, 3, 1), 58.0),
    ]


def test_output_is_sorted_and_deduped():
    """Out-of-order rows still yield strictly increasing, unique month-starts."""
    timeline = [
        _row(2026, 3, 7, 60),
        _row(2026, 1, 11, 20),
        _row(2026, 1, 4, 10),
        _row(2026, 2, 14, 40),
        _row(2026, 3, 21, 80),
        _row(2026, 2, 28, 50),
    ]
    out = aggregate_timeline_to_monthly(timeline)
    months = [m for m, _ in out]
    assert months == sorted(set(months))
    assert len(months) == 3
    by_month = dict(out)
    assert by_month[date(2026, 1, 1)] == 15.0
    assert by_month[date(2026, 2, 1)] == 45.0
    assert by_month[date(2026, 3, 1)] == 70.0


def test_skips_rows_missing_time_or_value():
    """Defensive: malformed rows are silently dropped, not raised on."""
    timeline = [
        {"time": None, "value": [99]},
        {"value": [99]},
        {"time": _ts(2026, 1, 4), "value": []},
        {"time": _ts(2026, 1, 11), "value": [40]},
    ]
    out = aggregate_timeline_to_monthly(timeline)
    assert out == [(date(2026, 1, 1), 20.0)]


def test_empty_timeline_returns_empty_list():
    assert aggregate_timeline_to_monthly([]) == []
