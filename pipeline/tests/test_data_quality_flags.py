"""Tests for the data_quality_flags helper.

The helper does three things:
1. Validates exactly one target id is provided.
2. Translates Python kwargs into the insert payload.
3. Treats unique-violation as idempotent (returns None instead of raising).

We mock the Supabase client because the function is a thin wrapper —
the goal is to lock the contract, not test PostgREST.
"""
from unittest.mock import MagicMock

import pytest

from pipeline.lib.data_quality_flags import raise_flag


def _mock_sb_returning_id(returned_id):
    """Build a fake supabase client whose .table(..).insert(..).execute()
    returns a row with id=returned_id."""
    sb = MagicMock()
    resp = MagicMock()
    resp.data = [{"id": returned_id}]
    sb.table.return_value.insert.return_value.execute.return_value = resp
    return sb


def _mock_sb_raising(exc):
    sb = MagicMock()
    sb.table.return_value.insert.return_value.execute.side_effect = exc
    return sb


class TestRaiseFlag:
    def test_requires_one_target(self):
        sb = _mock_sb_returning_id("aaaa")
        with pytest.raises(ValueError):
            raise_flag(sb, flag_kind="x", severity="med", detected_by="t")

    def test_rejects_multiple_targets(self):
        sb = _mock_sb_returning_id("aaaa")
        with pytest.raises(ValueError):
            raise_flag(
                sb, flag_kind="x", severity="med", detected_by="t",
                claim_id="c", entity_id="e",
            )

    def test_returns_new_id_on_success(self):
        sb = _mock_sb_returning_id("new-flag-id")
        out = raise_flag(
            sb, flag_kind="short_brand", severity="med", detected_by="t",
            entity_id="entity-123",
        )
        assert out == "new-flag-id"

    def test_payload_includes_all_provided_fields(self):
        sb = _mock_sb_returning_id("x")
        raise_flag(
            sb, flag_kind="short_brand", severity="med",
            detected_by="promote_claims", entity_id="ent-1",
            detail={"brand": "Poor"},
        )
        # First positional arg to insert() is the payload dict.
        payload = sb.table.return_value.insert.call_args[0][0]
        assert payload["flag_kind"] == "short_brand"
        assert payload["severity"] == "med"
        assert payload["detected_by"] == "promote_claims"
        assert payload["entity_id"] == "ent-1"
        assert payload["detail"] == {"brand": "Poor"}
        # Null target fields must NOT be in the payload (would crash the
        # NOT NULL FK if we sent claim_id=None).
        assert "claim_id" not in payload
        assert "event_id" not in payload

    def test_default_detail_is_empty_dict(self):
        sb = _mock_sb_returning_id("x")
        raise_flag(sb, flag_kind="k", severity="low", detected_by="t", entity_id="e")
        payload = sb.table.return_value.insert.call_args[0][0]
        assert payload["detail"] == {}

    def test_duplicate_key_returns_none_not_raises(self):
        # PostgREST surfaces unique-violation as a Python exception
        # containing "23505" in the message.
        sb = _mock_sb_raising(Exception("duplicate key value violates 23505"))
        out = raise_flag(
            sb, flag_kind="x", severity="low", detected_by="t",
            entity_id="e",
        )
        assert out is None

    def test_other_exceptions_propagate(self):
        sb = _mock_sb_raising(RuntimeError("connection refused"))
        with pytest.raises(RuntimeError):
            raise_flag(
                sb, flag_kind="x", severity="low", detected_by="t",
                entity_id="e",
            )

    def test_claim_target_works(self):
        sb = _mock_sb_returning_id("x")
        raise_flag(
            sb, flag_kind="stuck_approved_claim", severity="med",
            detected_by="cleanup_stuck_matched", claim_id="claim-99",
        )
        payload = sb.table.return_value.insert.call_args[0][0]
        assert payload["claim_id"] == "claim-99"
        assert "entity_id" not in payload
        assert "event_id" not in payload

    def test_event_target_works(self):
        sb = _mock_sb_returning_id("x")
        raise_flag(
            sb, flag_kind="size_outlier", severity="high",
            detected_by="detector", event_id="event-7",
        )
        payload = sb.table.return_value.insert.call_args[0][0]
        assert payload["event_id"] == "event-7"
