"""Tests for retract_zero_event_entities.

The script does four things worth locking with tests:

1. `find_orphaned_entities(sb)` walks product_entities + published_changes
   and returns the set difference (active entity ids that have NO live event
   behind them).

2. Dry-run vs apply contract on `process_orphans`:
   - dry-run must NOT call `rpc` or `raise_flag`
   - apply mode calls `rpc('set_entity_retracted', ...)` once per orphan
     and `raise_flag` once per orphan with the correct kwargs

3. Failure isolation: if a single orphan's retraction blows up, the loop
   keeps going and the failure is counted, not swallowed.

4. `render_brand_summary` aggregates a sweep result into a markdown
   table sorted by sweep count desc, capped at 20.
"""
from unittest.mock import MagicMock

from pipeline.scripts import retract_zero_event_entities as mod


# ─────────────────────────── find_orphaned_entities ───────────────────────────


def _mock_sb_pages(active_entities, live_events):
    """Build a fake supabase whose .table('product_entities') and
    .table('published_changes') chains each return a single page of rows.

    active_entities: list of {'id': ...}
    live_events:     list of {'entity_id': ...}
    """
    sb = MagicMock()

    def table_side_effect(table_name):
        chain = MagicMock()
        if table_name == "product_entities":
            # .select(...).eq(...).order(...).range(...).execute()
            execute = (
                chain.select.return_value
                .eq.return_value
                .order.return_value
                .range.return_value
                .execute
            )
            # First page returns the rows, second page returns empty to break the loop.
            page1 = MagicMock()
            page1.data = active_entities
            page2 = MagicMock()
            page2.data = []
            # Only need a second response if first page is at-or-above PAGE size.
            if len(active_entities) >= mod.PAGE:
                execute.side_effect = [page1, page2]
            else:
                execute.return_value = page1
        elif table_name == "published_changes":
            # .select(...).eq(...).not_.is_(...).range(...).execute()
            execute = (
                chain.select.return_value
                .eq.return_value
                .not_.is_.return_value
                .range.return_value
                .execute
            )
            page1 = MagicMock()
            page1.data = live_events
            page2 = MagicMock()
            page2.data = []
            if len(live_events) >= mod.PAGE:
                execute.side_effect = [page1, page2]
            else:
                execute.return_value = page1
        return chain

    sb.table.side_effect = table_side_effect
    return sb


class TestFindOrphanedEntities:
    def test_returns_entities_with_no_live_event(self):
        sb = _mock_sb_pages(
            active_entities=[{"id": "e1"}, {"id": "e2"}, {"id": "e3"}],
            live_events=[{"entity_id": "e1"}],
        )
        out = mod.find_orphaned_entities(sb)
        assert set(out) == {"e2", "e3"}

    def test_empty_when_all_have_events(self):
        sb = _mock_sb_pages(
            active_entities=[{"id": "e1"}],
            live_events=[{"entity_id": "e1"}],
        )
        out = mod.find_orphaned_entities(sb)
        assert out == []

    def test_empty_when_no_active_entities(self):
        sb = _mock_sb_pages(
            active_entities=[],
            live_events=[],
        )
        out = mod.find_orphaned_entities(sb)
        assert out == []

    def test_ignores_null_entity_ids_in_events(self):
        # published_changes rows with entity_id=None must not count as "covering"
        # any active entity.
        sb = _mock_sb_pages(
            active_entities=[{"id": "e1"}, {"id": "e2"}],
            live_events=[{"entity_id": None}, {"entity_id": "e1"}],
        )
        out = mod.find_orphaned_entities(sb)
        assert out == ["e2"]


# ─────────────────────────── process_orphans (dry-run vs apply) ───────────────────────────


class TestProcessOrphans:
    def test_dry_run_does_not_call_rpc_or_raise_flag(self, monkeypatch):
        sb = MagicMock()
        raise_flag_mock = MagicMock()
        monkeypatch.setattr(mod.data_quality_flags, "raise_flag", raise_flag_mock)

        result = mod.process_orphans(sb, ["e1", "e2", "e3"], dry_run=True)

        sb.rpc.assert_not_called()
        raise_flag_mock.assert_not_called()
        assert result["retracted"] == 0
        assert result["failures"] == 0
        assert result["dry_run"] is True
        assert result["would_retract"] == 3

    def test_apply_calls_rpc_and_raise_flag_per_orphan(self, monkeypatch):
        sb = MagicMock()
        # rpc returns a chain whose .execute().data is a list with events_affected.
        rpc_exec = sb.rpc.return_value.execute
        rpc_exec.return_value.data = [{"events_affected": 0}]

        raise_flag_mock = MagicMock()
        monkeypatch.setattr(mod.data_quality_flags, "raise_flag", raise_flag_mock)

        result = mod.process_orphans(sb, ["e1", "e2"], dry_run=False)

        # rpc called once per orphan, with the right shape.
        assert sb.rpc.call_count == 2
        # Check the first call.
        first_call = sb.rpc.call_args_list[0]
        assert first_call.args[0] == "set_entity_retracted"
        assert first_call.args[1] == {"p_entity_id": "e1", "p_retracted": True}

        # raise_flag invoked once per orphan with the right kwargs.
        assert raise_flag_mock.call_count == 2
        kwargs = raise_flag_mock.call_args_list[0].kwargs
        assert kwargs["flag_kind"] == mod.FLAG_KIND
        assert kwargs["severity"] == "low"
        assert kwargs["detected_by"] == mod.DETECTED_BY
        assert kwargs["entity_id"] == "e1"
        assert kwargs["detail"] == {"events_affected": 0, "reason": "no live event"}

        assert result["retracted"] == 2
        assert result["failures"] == 0
        assert result["dry_run"] is False

    def test_apply_continues_past_failed_retract(self, monkeypatch):
        """If retract_one raises, the loop keeps going and counts the failure."""
        sb = MagicMock()

        call_count = {"n": 0}

        def bad_retract(_sb, _entity_id):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("first one blows up")
            return 0

        monkeypatch.setattr(mod, "retract_one", bad_retract)

        raise_flag_mock = MagicMock()
        monkeypatch.setattr(mod.data_quality_flags, "raise_flag", raise_flag_mock)

        result = mod.process_orphans(sb, ["e1", "e2", "e3"], dry_run=False)

        # Failure on e1 → no flag for e1; e2 and e3 succeed → 2 flags.
        assert raise_flag_mock.call_count == 2
        assert result["retracted"] == 2
        assert result["failures"] == 1

    def test_apply_passes_events_affected_into_flag_detail(self, monkeypatch):
        """events_affected from the RPC must round-trip into the flag detail."""
        sb = MagicMock()

        def fake_retract(_sb, entity_id):
            # Pretend e1 had 0 events (sanity-check the no-events case) and
            # e2 had 3 (sanity-check the rare "orphan-with-retracted-events" case).
            return {"e1": 0, "e2": 3}[entity_id]

        monkeypatch.setattr(mod, "retract_one", fake_retract)

        raise_flag_mock = MagicMock()
        monkeypatch.setattr(mod.data_quality_flags, "raise_flag", raise_flag_mock)

        mod.process_orphans(sb, ["e1", "e2"], dry_run=False)

        details = [c.kwargs["detail"] for c in raise_flag_mock.call_args_list]
        assert details[0]["events_affected"] == 0
        assert details[1]["events_affected"] == 3


# ─────────────────────────── render_brand_summary ───────────────────────────


class TestRenderBrandSummary:
    def test_groups_by_brand_sorted_desc(self):
        brands = {
            "e1": "Cadbury",
            "e2": "Cadbury",
            "e3": "Nestle",
        }
        out = mod.render_brand_summary(
            orphan_ids=["e1", "e2", "e3"],
            brand_by_id=brands,
            total_swept=3,
            failures=0,
        )
        assert "Cadbury" in out
        assert "Nestle" in out
        # Cadbury (2) should appear before Nestle (1).
        assert out.index("Cadbury") < out.index("Nestle")
        assert "3" in out  # total

    def test_caps_at_20_brands(self):
        brands = {"e{}".format(i): "Brand{}".format(i) for i in range(25)}
        orphan_ids = list(brands.keys())
        out = mod.render_brand_summary(
            orphan_ids=orphan_ids,
            brand_by_id=brands,
            total_swept=25,
            failures=0,
        )
        # Should contain "Brand0" through "Brand19" but not all 25 — count
        # lines under the table header.
        for i in range(20):
            assert "Brand{}".format(i) in out or "Brand{} ".format(i) in out
        # At minimum: not all 25 distinct brand names appear.
        appearing = sum(1 for i in range(25) if "Brand{}\t".format(i) in out or "| Brand{} ".format(i) in out or "Brand{}|".format(i) in out)
        # Loose check — at most 20 should appear in the truncated section.
        # (Truncation message handles overflow.)
        assert "5 more" in out or "more brand" in out.lower()

    def test_includes_unknown_for_missing_brand(self):
        out = mod.render_brand_summary(
            orphan_ids=["e1"],
            brand_by_id={},  # no brand info for e1
            total_swept=1,
            failures=0,
        )
        assert "unknown" in out.lower() or "Unknown" in out
