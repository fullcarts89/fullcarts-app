"""Sanity-bound guard for promote_claims.

The guard mirrors the CHECK constraint added by migration 061 — every input
that the constraint would reject must also be rejected by the Python guard
so the daily cron stays green.
"""
import pytest

from pipeline.scripts.promote_claims import (
    SIZE_RATIO_MAX,
    SIZE_RATIO_MIN,
    sane_size_ratio,
)


class TestSaneSize:
    """Bounds match migration 061: [0.05, 5.0]."""

    @pytest.mark.parametrize(
        "old,new",
        [
            (200, 180),        # ordinary 10% shrink
            (1000, 950),       # 5% shrink
            (200, 50),         # 75% shrink — extreme but plausible
            (200, 10),         # ratio = 0.05 (lower bound, inclusive)
            (200, 1000),       # ratio = 5.0 (upper bound, inclusive)
            (16.0, 32.0),      # value-pack doubling — legitimate
        ],
    )
    def test_accepts_plausible(self, old, new):
        assert sane_size_ratio(old, new) is True

    @pytest.mark.parametrize(
        "old,new",
        [
            (1, 900),          # 1L -> 900L: classic unit-parse error
            (1, 1000),         # 1kg -> 1000kg
            (200, 1001),       # just past the ratio=5 upper bound
            (200, 9),          # just under the ratio=0.05 lower bound
            (200, 0.001),      # massive shrink, almost certainly bad
        ],
    )
    def test_rejects_implausible(self, old, new):
        assert sane_size_ratio(old, new) is False

    @pytest.mark.parametrize(
        "old,new",
        [
            (None, None),      # skimpflation event, no size
            (200, None),       # before only
            (None, 180),       # after only
        ],
    )
    def test_passes_when_either_side_null(self, old, new):
        assert sane_size_ratio(old, new) is True

    @pytest.mark.parametrize("old", [0, -1, -100.5])
    def test_rejects_nonpositive_old_size(self, old):
        assert sane_size_ratio(old, 100) is False

    def test_bounds_are_inclusive(self):
        # Hardcoded to lock the contract: anyone widening the bounds in
        # promote_claims must also update migration 061.
        assert SIZE_RATIO_MIN == 0.05
        assert SIZE_RATIO_MAX == 5.0
