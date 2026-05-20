"""Unit tests for the matched-claims profiler analysers.

The analyser functions are pure (lists/dicts in, lists of dicts out) so
the tests just feed in synthetic event/entity rows and check the right
rows surface.
"""
import pytest

from pipeline.scripts.profile_matched_claims import (
    EXTREME_SIZE_FLAG,
    SINGLE_EVENT_TIGHT_MAX,
    SINGLE_EVENT_TIGHT_MIN,
    WIDE_SIZE_FLAG,
    _slugify,
    analyse_duplicate_entities,
    analyse_mixed_units,
    analyse_outlier_events,
    analyse_wide_size_range,
)


def _ev(**kw):
    """Synthetic event with sensible defaults."""
    base = {
        "id": "evt-1",
        "entity_id": "ent-1",
        "brand": "Acme",
        "product_name": "Foo",
        "size_before": 200,
        "size_after": 180,
        "size_unit": "g",
        "size_delta_pct": -10.0,
        "evidence_count": 1,
        "observed_date": "2024-01-01",
    }
    base.update(kw)
    return base


def _ent(**kw):
    base = {
        "id": "ent-1",
        "brand": "Acme",
        "canonical_name": "Foo Bar",
        "event_count": 1,
    }
    base.update(kw)
    return base


class TestSlugify:
    @pytest.mark.parametrize(
        "name,expected",
        [
            ("Wheat Thins", "wheatthins"),
            ("Wheat-Thins Original", "wheatthinsoriginal"),
            ("  Wheat   Thins  ", "wheatthins"),
            ("Cadbury Dairy Milk (200g)", "cadburydairymilk200g"),
            ("M&M's Plain", "mmsplain"),
        ],
    )
    def test_normalises_variants_to_same_slug(self, name, expected):
        assert _slugify(name) == expected

    def test_empty_string(self):
        assert _slugify("") == ""

    def test_only_punctuation(self):
        assert _slugify("---") == ""


class TestOutlierEvents:
    def test_within_bounds_not_flagged(self):
        rows = analyse_outlier_events([_ev(size_before=200, size_after=180)])
        assert rows == []

    def test_extreme_shrink_flagged(self):
        # 12 oz -> 0.5 oz = ratio ~0.042, well below 0.5.
        rows = analyse_outlier_events([_ev(size_before=12, size_after=0.5)])
        assert len(rows) == 1
        assert rows[0]["ratio"] < SINGLE_EVENT_TIGHT_MIN

    def test_extreme_growth_flagged(self):
        rows = analyse_outlier_events([_ev(size_before=10, size_after=50)])
        assert len(rows) == 1
        assert rows[0]["ratio"] > SINGLE_EVENT_TIGHT_MAX

    def test_invalid_sizes_skipped(self):
        rows = analyse_outlier_events([
            _ev(size_before=0, size_after=10),
            _ev(size_before=10, size_after=0),
            _ev(size_before=None, size_after=10),
        ])
        assert rows == []

    def test_higher_evidence_first(self):
        rows = analyse_outlier_events([
            _ev(id="a", size_before=10, size_after=50, evidence_count=1),
            _ev(id="b", size_before=10, size_after=50, evidence_count=5),
        ])
        assert [r["event_id"] for r in rows] == ["b", "a"]


class TestMixedUnits:
    def test_single_unit_not_flagged(self):
        rows = analyse_mixed_units([_ev(size_unit="g"), _ev(size_unit="g")])
        assert rows == []

    def test_mixed_units_flagged_with_majority(self):
        rows = analyse_mixed_units([
            _ev(id="a", size_unit="g"),
            _ev(id="b", size_unit="g"),
            _ev(id="c", size_unit="oz"),
        ])
        assert len(rows) == 1
        assert rows[0]["majority_unit"] == "g"
        assert rows[0]["majority_count"] == 2
        assert rows[0]["minority_units"] == "oz"

    def test_case_and_whitespace_normalised(self):
        rows = analyse_mixed_units([
            _ev(id="a", size_unit="G"),
            _ev(id="b", size_unit=" g "),
        ])
        # Both normalise to 'g' — not flagged.
        assert rows == []

    def test_three_distinct_units(self):
        rows = analyse_mixed_units([
            _ev(id=str(i), size_unit=u)
            for i, u in enumerate(["g", "g", "oz", "ml"])
        ])
        assert rows[0]["unit_variants"] == 3


class TestWideSizeRange:
    def test_single_event_not_flagged(self):
        rows = analyse_wide_size_range([_ev()])
        assert rows == []

    def test_narrow_spread_not_flagged(self):
        rows = analyse_wide_size_range([
            _ev(id="a", size_before=200),
            _ev(id="b", size_before=180),
        ])
        assert rows == []

    def test_3x_spread_flagged_wide(self):
        rows = analyse_wide_size_range([
            _ev(id="a", size_before=100),
            _ev(id="b", size_before=350),
        ])
        assert len(rows) == 1
        assert rows[0]["severity"] == "wide"

    def test_10x_spread_flagged_extreme(self):
        rows = analyse_wide_size_range([
            _ev(id="a", size_before=10),
            _ev(id="b", size_before=200),
        ])
        assert len(rows) == 1
        assert rows[0]["severity"] == "extreme"

    def test_sorted_by_spread_desc(self):
        rows = analyse_wide_size_range([
            _ev(id="a1", entity_id="ent-narrow", size_before=10),
            _ev(id="a2", entity_id="ent-narrow", size_before=40),  # 4x
            _ev(id="b1", entity_id="ent-wide", size_before=10),
            _ev(id="b2", entity_id="ent-wide", size_before=500),  # 50x
        ])
        assert [r["entity_id"] for r in rows] == ["ent-wide", "ent-narrow"]


class TestDuplicateEntities:
    def test_unique_not_flagged(self):
        rows = analyse_duplicate_entities([
            _ent(id="a", canonical_name="Foo"),
            _ent(id="b", canonical_name="Bar"),
        ])
        assert rows == []

    def test_exact_duplicate_flagged(self):
        rows = analyse_duplicate_entities([
            _ent(id="a", canonical_name="Wheat Thins", event_count=10),
            _ent(id="b", canonical_name="Wheat Thins", event_count=2),
        ])
        assert len(rows) == 1
        # Target should be the higher-event-count entity.
        assert rows[0]["target_id"] == "a"
        assert rows[0]["source_id"] == "b"

    def test_fuzzy_duplicate_flagged(self):
        rows = analyse_duplicate_entities([
            _ent(id="a", canonical_name="Wheat Thins", event_count=5),
            _ent(id="b", canonical_name="wheat-thins", event_count=1),
            _ent(id="c", canonical_name="WheatThins", event_count=0),
        ])
        # Three entities collapse to one group; two non-target rows.
        assert len(rows) == 2

    def test_different_brands_not_merged(self):
        # Same slug but different brand → no merge.
        rows = analyse_duplicate_entities([
            _ent(id="a", brand="Mondelez", canonical_name="Wheat Thins"),
            _ent(id="b", brand="Nabisco", canonical_name="Wheat Thins"),
        ])
        assert rows == []

    def test_suggested_action_contains_sql(self):
        rows = analyse_duplicate_entities([
            _ent(id="a", canonical_name="Foo", event_count=5),
            _ent(id="b", canonical_name="Foo", event_count=1),
        ])
        assert "merge_entities" in rows[0]["suggested_action"]
        assert rows[0]["source_id"] in rows[0]["suggested_action"]
        assert rows[0]["target_id"] in rows[0]["suggested_action"]


class TestBoundsContract:
    """If the bounds drift, downstream analysis breaks."""
    def test_tight_bounds_match_spec(self):
        assert SINGLE_EVENT_TIGHT_MIN == 0.5
        assert SINGLE_EVENT_TIGHT_MAX == 2.0

    def test_spread_thresholds_ordered(self):
        assert WIDE_SIZE_FLAG < EXTREME_SIZE_FLAG
