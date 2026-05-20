"""Unit tests for the auto-triage decision rules.

The decide() function is pure (in: flag dict + a couple of side-input
booleans/ints; out: action string + reason string), so tests don't need
a DB at all. Locking the rules in tests means any future change to the
thresholds or kind handling is intentional.
"""
import pytest

from pipeline.scripts.auto_triage_quality_flags import decide


def _flag(**kw):
    base = {
        "id": "flag-1",
        "claim_id": None,
        "entity_id": "ent-1",
        "event_id": None,
        "flag_kind": "short_brand",
        "severity": "med",
        "detail": {},
    }
    base.update(kw)
    return base


class TestFuzzyBrandCollision:
    def test_merges_when_both_active(self):
        action, _ = decide(
            _flag(flag_kind="fuzzy_brand_collision", detail={"target_id": "ent-2"}),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "merge"

    def test_skips_when_source_already_retracted(self):
        action, _ = decide(
            _flag(flag_kind="fuzzy_brand_collision", detail={"target_id": "ent-2"}),
            entity_event_count=0,
            source_retracted=True,
            target_retracted=False,
        )
        assert action == "skip_already_done"

    def test_skips_when_target_already_retracted(self):
        action, _ = decide(
            _flag(flag_kind="fuzzy_brand_collision", detail={"target_id": "ent-2"}),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=True,
        )
        assert action == "skip_already_done"


class TestSkuMashup:
    def test_high_severity_retracts(self):
        action, _ = decide(
            _flag(flag_kind="sku_mashup", severity="high"),
            entity_event_count=5,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "retract_entity"

    def test_med_severity_left_for_human(self):
        action, reason = decide(
            _flag(flag_kind="sku_mashup", severity="med"),
            entity_event_count=5,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"
        assert "pack-size" in reason

    def test_low_severity_left_for_human(self):
        action, _ = decide(
            _flag(flag_kind="sku_mashup", severity="low"),
            entity_event_count=5,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"


class TestSizeOutlier:
    def test_high_severity_retracts_event(self):
        action, _ = decide(
            _flag(flag_kind="size_outlier", severity="high"),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "retract_event"

    def test_med_severity_left_for_human(self):
        action, reason = decide(
            _flag(flag_kind="size_outlier", severity="med"),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"
        assert "legit" in reason


class TestShortBrand:
    def test_zero_events_retracts(self):
        action, _ = decide(
            _flag(flag_kind="short_brand"),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "retract_entity"

    def test_with_events_left_for_human(self):
        action, reason = decide(
            _flag(flag_kind="short_brand"),
            entity_event_count=3,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"
        assert "rename" in reason or "retract" in reason


class TestMixedUnits:
    def test_always_left_for_human(self):
        for sev in ("low", "med", "high"):
            action, _ = decide(
                _flag(flag_kind="mixed_units", severity=sev),
                entity_event_count=0,
                source_retracted=False,
                target_retracted=False,
            )
            assert action == "leave", f"mixed_units sev={sev} should be 'leave'"


class TestStuckClaim:
    def test_always_left_for_human(self):
        action, _ = decide(
            _flag(flag_kind="stuck_approved_claim", severity="med"),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"


class TestUnknownKind:
    def test_unknown_kind_left_for_human(self):
        action, reason = decide(
            _flag(flag_kind="new_kind_we_havent_implemented", severity="high"),
            entity_event_count=0,
            source_retracted=False,
            target_retracted=False,
        )
        assert action == "leave"
        assert "unknown" in reason.lower()


class TestReasonStringsAreInformative:
    """Smoke test — every decide() return must include a non-empty
    reason. The reason becomes the resolution_note on the resolved flag,
    so empty strings would be a documentation regression."""
    @pytest.mark.parametrize(
        "flag,extras",
        [
            (_flag(flag_kind="fuzzy_brand_collision", detail={"target_id": "x"}), {}),
            (_flag(flag_kind="sku_mashup", severity="high"), {}),
            (_flag(flag_kind="sku_mashup", severity="med"), {}),
            (_flag(flag_kind="size_outlier", severity="high"), {}),
            (_flag(flag_kind="short_brand"), {}),
            (_flag(flag_kind="short_brand"), {"entity_event_count": 5}),
            (_flag(flag_kind="mixed_units"), {}),
        ],
    )
    def test(self, flag, extras):
        defaults = {
            "entity_event_count": 0,
            "source_retracted": False,
            "target_retracted": False,
        }
        defaults.update(extras)
        _, reason = decide(flag, **defaults)
        assert reason and len(reason) > 5
