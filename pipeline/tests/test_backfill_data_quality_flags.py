"""Unit tests for the backfill detector predicates.

Predicates are pure (synthetic dicts in, side-effect via raise_flag).
We mock raise_flag to capture calls instead of hitting Supabase.
"""
from unittest.mock import patch

import pytest

from pipeline.scripts.backfill_data_quality_flags import (
    EXTREME_SPREAD,
    SIZE_OUTLIER_MAX,
    SIZE_OUTLIER_MIN,
    WIDE_SPREAD,
    detect_fuzzy_brand_collision,
    detect_mixed_units,
    detect_short_brand,
    detect_size_outlier,
    detect_sku_mashup,
    is_suspect_brand,
    slugify,
)


def _ent(**kw):
    base = {
        "id": "ent-1",
        "brand": "Acme",
        "canonical_name": "Foo",
        "event_count": 0,
    }
    base.update(kw)
    return base


def _ev(**kw):
    base = {
        "id": "evt-1",
        "entity_id": "ent-1",
        "brand": "Acme",
        "product_name": "Foo",
        "size_before": 200,
        "size_after": 180,
        "size_unit": "g",
        "evidence_count": 1,
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
            ("", ""),
            ("---", ""),
        ],
    )
    def test(self, name, expected):
        assert slugify(name) == expected


class TestIsSuspectBrand:
    @pytest.mark.parametrize(
        "brand",
        ["Unknown", "Various", "Poor", "N/A", "Generic", "Misc"],
    )
    def test_placeholders(self, brand):
        assert is_suspect_brand(brand) is True

    @pytest.mark.parametrize("brand", ["a", "", " ", None])
    def test_too_short(self, brand):
        assert is_suspect_brand(brand) is True

    @pytest.mark.parametrize(
        "brand", ["Cadbury", "M&M's", "3M", "AB", "abc"]
    )
    def test_real(self, brand):
        assert is_suspect_brand(brand) is False


class TestDetectShortBrand:
    def test_flags_placeholder_brand(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"short_brand_matched": 0, "short_brand_inserted": 0, "short_brand_already_open": 0}
            detect_short_brand(
                sb=None,
                entities=[_ent(brand="Unknown")],
                dry_run=False,
                stats=stats,
            )
        assert stats["short_brand_matched"] == 1
        assert stats["short_brand_inserted"] == 1
        assert captured[0]["flag_kind"] == "short_brand"
        assert captured[0]["entity_id"] == "ent-1"

    def test_skips_real_brand(self):
        with patch("pipeline.scripts.backfill_data_quality_flags.raise_flag") as mock:
            stats = {"short_brand_matched": 0, "short_brand_inserted": 0, "short_brand_already_open": 0}
            detect_short_brand(
                sb=None,
                entities=[_ent(brand="Cadbury")],
                dry_run=False,
                stats=stats,
            )
        mock.assert_not_called()
        assert stats["short_brand_matched"] == 0

    def test_dry_run_no_writes(self):
        with patch("pipeline.scripts.backfill_data_quality_flags.raise_flag") as mock:
            stats = {"short_brand_matched": 0, "short_brand_inserted": 0, "short_brand_already_open": 0}
            detect_short_brand(
                sb=None,
                entities=[_ent(brand="Unknown")],
                dry_run=True,
                stats=stats,
            )
        mock.assert_not_called()
        assert stats["short_brand_matched"] == 1
        assert stats["short_brand_inserted"] == 0

    def test_counts_already_open(self):
        """raise_flag returns None when the partial unique index rejects
        a duplicate. The detector counts that separately."""
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            return_value=None,
        ):
            stats = {"short_brand_matched": 0, "short_brand_inserted": 0, "short_brand_already_open": 0}
            detect_short_brand(
                sb=None,
                entities=[_ent(brand="Poor")],
                dry_run=False,
                stats=stats,
            )
        assert stats["short_brand_matched"] == 1
        assert stats["short_brand_inserted"] == 0
        assert stats["short_brand_already_open"] == 1


class TestDetectFuzzyBrandCollision:
    def test_groups_by_brand_and_slug(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {
                "fuzzy_brand_collision_matched": 0,
                "fuzzy_brand_collision_inserted": 0,
                "fuzzy_brand_collision_already_open": 0,
            }
            detect_fuzzy_brand_collision(
                sb=None,
                entities=[
                    _ent(id="a", canonical_name="Wheat Thins", event_count=10),
                    _ent(id="b", canonical_name="wheat-thins", event_count=2),
                    _ent(id="c", canonical_name="WheatThins", event_count=0),
                ],
                dry_run=False,
                stats=stats,
            )
        assert stats["fuzzy_brand_collision_matched"] == 2
        # All sources should point at id=a (highest events).
        target_ids = {c["detail"]["target_id"] for c in captured}
        assert target_ids == {"a"}

    def test_different_brand_no_merge(self):
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag"
        ) as mock:
            stats = {
                "fuzzy_brand_collision_matched": 0,
                "fuzzy_brand_collision_inserted": 0,
                "fuzzy_brand_collision_already_open": 0,
            }
            detect_fuzzy_brand_collision(
                sb=None,
                entities=[
                    _ent(id="a", brand="Mondelez", canonical_name="Wheat Thins"),
                    _ent(id="b", brand="Nabisco", canonical_name="Wheat Thins"),
                ],
                dry_run=False,
                stats=stats,
            )
        mock.assert_not_called()


class TestDetectSizeOutlier:
    def test_in_band_skipped(self):
        with patch("pipeline.scripts.backfill_data_quality_flags.raise_flag") as mock:
            stats = {"size_outlier_matched": 0, "size_outlier_inserted": 0, "size_outlier_already_open": 0}
            detect_size_outlier(
                sb=None,
                events=[_ev(size_before=200, size_after=180)],  # 0.9 ratio
                dry_run=False,
                stats=stats,
            )
        mock.assert_not_called()

    def test_extreme_shrink_flagged_high_severity(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"size_outlier_matched": 0, "size_outlier_inserted": 0, "size_outlier_already_open": 0}
            detect_size_outlier(
                sb=None,
                events=[_ev(size_before=12, size_after=0.5)],  # ratio 0.042
                dry_run=False,
                stats=stats,
            )
        assert captured[0]["severity"] == "high"

    def test_moderate_outlier_med_severity(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"size_outlier_matched": 0, "size_outlier_inserted": 0, "size_outlier_already_open": 0}
            detect_size_outlier(
                sb=None,
                events=[_ev(size_before=200, size_after=80)],  # 0.4
                dry_run=False,
                stats=stats,
            )
        assert captured[0]["severity"] == "med"


class TestDetectSkuMashup:
    def test_wide_spread_flagged(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"sku_mashup_matched": 0, "sku_mashup_inserted": 0, "sku_mashup_already_open": 0}
            detect_sku_mashup(
                sb=None,
                events=[
                    _ev(id="a", size_before=100),
                    _ev(id="b", size_before=400),  # 4x spread
                ],
                dry_run=False,
                stats=stats,
            )
        assert captured[0]["severity"] == "med"

    def test_extreme_spread_high_severity(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"sku_mashup_matched": 0, "sku_mashup_inserted": 0, "sku_mashup_already_open": 0}
            detect_sku_mashup(
                sb=None,
                events=[
                    _ev(id="a", size_before=10),
                    _ev(id="b", size_before=500),  # 50x spread
                ],
                dry_run=False,
                stats=stats,
            )
        assert captured[0]["severity"] == "high"

    def test_single_event_not_flagged(self):
        with patch("pipeline.scripts.backfill_data_quality_flags.raise_flag") as mock:
            stats = {"sku_mashup_matched": 0, "sku_mashup_inserted": 0, "sku_mashup_already_open": 0}
            detect_sku_mashup(
                sb=None,
                events=[_ev()],
                dry_run=False,
                stats=stats,
            )
        mock.assert_not_called()


class TestDetectMixedUnits:
    def test_single_unit_not_flagged(self):
        with patch("pipeline.scripts.backfill_data_quality_flags.raise_flag") as mock:
            stats = {"mixed_units_matched": 0, "mixed_units_inserted": 0, "mixed_units_already_open": 0}
            detect_mixed_units(
                sb=None,
                events=[_ev(size_unit="g"), _ev(size_unit="g")],
                dry_run=False,
                stats=stats,
            )
        mock.assert_not_called()

    def test_two_units_flagged(self):
        captured = []
        with patch(
            "pipeline.scripts.backfill_data_quality_flags.raise_flag",
            side_effect=lambda *a, **kw: captured.append(kw) or "log-id",
        ):
            stats = {"mixed_units_matched": 0, "mixed_units_inserted": 0, "mixed_units_already_open": 0}
            detect_mixed_units(
                sb=None,
                events=[
                    _ev(id="a", size_unit="g"),
                    _ev(id="b", size_unit="g"),
                    _ev(id="c", size_unit="oz"),
                ],
                dry_run=False,
                stats=stats,
            )
        assert captured[0]["detail"]["majority_unit"] == "g"
        assert "oz" in captured[0]["detail"]["minority_units"]


class TestBoundsContract:
    """Tighten / loosen these and the queue size shifts wildly. Lock
    them so changes are intentional."""
    def test_size_bounds(self):
        assert SIZE_OUTLIER_MIN == 0.5
        assert SIZE_OUTLIER_MAX == 2.0

    def test_spread_bounds(self):
        assert WIDE_SPREAD == 3.0
        assert EXTREME_SPREAD == 10.0
        assert WIDE_SPREAD < EXTREME_SPREAD
