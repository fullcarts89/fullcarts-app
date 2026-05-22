-- Migration 070: previous_entity_id tracking + event_reassign_log + reassign RPC
--
-- Adds the data plumbing for two related admin tools:
--   1. reassign_events_by_size — extracts events on a source entity matching
--      a specific (size_before, size_after, size_unit) and moves them
--      (together with their contributing claims) onto a target entity.
--      Use case: "Gatorade Sports Drink" has 20→16.9 fl oz events that are
--      really a different product; peel them off onto a new/other entity.
--   2. undo_merge (added later) — reverses an entry from entity_merge_log
--      using the new previous_entity_id columns populated by every future
--      merge.
--
-- All new columns are NULLABLE so existing rows are untouched. Pre-070
-- merges (the 10 in entity_merge_log today) will NOT have
-- previous_entity_id populated and therefore can't be undone via the new
-- RPC — those need manual cleanup via the per-event reassign UI.
--
-- Re-running this migration is safe: every ALTER and CREATE uses
-- IF NOT EXISTS / OR REPLACE.

BEGIN;

ALTER TABLE published_changes
    ADD COLUMN IF NOT EXISTS previous_entity_id UUID REFERENCES product_entities(id);

ALTER TABLE claims
    ADD COLUMN IF NOT EXISTS previous_matched_entity_id UUID REFERENCES product_entities(id);

ALTER TABLE pack_variants
    ADD COLUMN IF NOT EXISTS previous_entity_id UUID REFERENCES product_entities(id);

ALTER TABLE entity_merge_log
    ADD COLUMN IF NOT EXISTS undone_at TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS undone_by TEXT;

-- One row per event moved. Each call to reassign_events_by_size touching
-- N events writes N rows here, so the audit trail is per-event (matches
-- the granularity at which an undo would operate).
CREATE TABLE IF NOT EXISTS event_reassign_log (
    id              BIGSERIAL PRIMARY KEY,
    event_id        UUID NOT NULL REFERENCES published_changes(id),
    from_entity_id  UUID NOT NULL REFERENCES product_entities(id),
    to_entity_id    UUID NOT NULL REFERENCES product_entities(id),
    moved_claim_ids UUID[] DEFAULT '{}',
    reassigned_at   TIMESTAMPTZ DEFAULT now() NOT NULL,
    reassigned_by   TEXT NOT NULL,
    undone_at       TIMESTAMPTZ,
    undone_by       TEXT
);

CREATE INDEX IF NOT EXISTS idx_event_reassign_log_event
    ON event_reassign_log(event_id);
CREATE INDEX IF NOT EXISTS idx_event_reassign_log_open
    ON event_reassign_log(reassigned_at DESC)
 WHERE undone_at IS NULL;

-- ─── Updated merge_entities ─────────────────────────────────────────
-- Behavioural diff vs. the version in migration 065: every UPDATE now
-- sets previous_entity_id / previous_matched_entity_id before overwriting
-- entity_id / matched_entity_id. Net effect on the caller is zero; the
-- new columns just record the move so undo is trivial.

CREATE OR REPLACE FUNCTION merge_entities(
    p_source_id UUID,
    p_target_id UUID,
    p_merged_by TEXT DEFAULT NULL
) RETURNS TABLE (log_id BIGINT, claims_moved INT, events_moved INT, variants_moved INT) AS $$
DECLARE
    v_claims_moved INT := 0;
    v_events_moved INT := 0;
    v_variants_moved INT := 0;
    v_log_id BIGINT;
BEGIN
    IF p_source_id = p_target_id THEN
        RAISE EXCEPTION 'merge_entities: source and target are the same';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_source_id) THEN
        RAISE EXCEPTION 'merge_entities: source entity % not found', p_source_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_target_id) THEN
        RAISE EXCEPTION 'merge_entities: target entity % not found', p_target_id;
    END IF;

    UPDATE claims
       SET previous_matched_entity_id = matched_entity_id,
           matched_entity_id          = p_target_id
     WHERE matched_entity_id = p_source_id;
    GET DIAGNOSTICS v_claims_moved = ROW_COUNT;

    UPDATE published_changes
       SET previous_entity_id = entity_id,
           entity_id          = p_target_id
     WHERE entity_id = p_source_id;
    GET DIAGNOSTICS v_events_moved = ROW_COUNT;

    UPDATE pack_variants
       SET previous_entity_id = entity_id,
           entity_id          = p_target_id
     WHERE entity_id = p_source_id;
    GET DIAGNOSTICS v_variants_moved = ROW_COUNT;

    UPDATE product_entities
       SET is_retracted = true
     WHERE id = p_source_id;

    INSERT INTO entity_merge_log (
        source_id, target_id, merged_by,
        claims_moved, events_moved, variants_moved
    ) VALUES (
        p_source_id, p_target_id, p_merged_by,
        v_claims_moved, v_events_moved, v_variants_moved
    ) RETURNING id INTO v_log_id;

    RETURN QUERY SELECT v_log_id, v_claims_moved, v_events_moved, v_variants_moved;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION merge_entities IS
    'Phase 2D step 4 + migration 070. Moves all dependent rows from source '
    'to target, retracts source, logs the operation. Records previous '
    'entity ids for future undo support. All-or-nothing.';

-- ─── New: reassign_events_by_size ───────────────────────────────────
-- Move all events at a single (size_before, size_after, size_unit)
-- signature from source to target, together with their contributing
-- claims (originator via change_candidates.supporting_claims + fold-ins
-- via published_changes.evidence_summary[].claim_id). All-or-nothing.

CREATE OR REPLACE FUNCTION reassign_events_by_size(
    p_source_entity_id  UUID,
    p_target_entity_id  UUID,
    p_size_before       NUMERIC,
    p_size_after        NUMERIC,
    p_size_unit         TEXT,
    p_reassigned_by     TEXT
) RETURNS TABLE (events_moved INT, claims_moved INT) AS $$
DECLARE
    v_event_ids       UUID[];
    v_claim_ids       UUID[];
    v_claims_moved    INT := 0;
    v_events_moved    INT := 0;
BEGIN
    IF p_source_entity_id = p_target_entity_id THEN
        RAISE EXCEPTION 'reassign_events_by_size: source and target are the same';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_source_entity_id) THEN
        RAISE EXCEPTION 'reassign_events_by_size: source entity % not found', p_source_entity_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_target_entity_id) THEN
        RAISE EXCEPTION 'reassign_events_by_size: target entity % not found', p_target_entity_id;
    END IF;

    -- Identify live events on source that match the size signature.
    SELECT array_agg(id) INTO v_event_ids
      FROM published_changes
     WHERE entity_id = p_source_entity_id
       AND COALESCE(is_retracted, false) = false
       AND size_before = p_size_before
       AND size_after  = p_size_after
       AND COALESCE(size_unit, '') = COALESCE(p_size_unit, '');

    IF v_event_ids IS NULL OR cardinality(v_event_ids) = 0 THEN
        RAISE EXCEPTION
            'reassign_events_by_size: no matching events found on source % at %->% %',
            p_source_entity_id, p_size_before, p_size_after, p_size_unit;
    END IF;

    -- Collect all contributing claim ids — originator (via
    -- change_candidates.supporting_claims) UNION fold-ins (from
    -- evidence_summary jsonb). DISTINCT because the same claim could
    -- conceivably appear in both lists.
    WITH originator AS (
        SELECT unnest(cc.supporting_claims) AS claim_id
          FROM published_changes pc
          LEFT JOIN change_candidates cc ON cc.id = pc.candidate_id
         WHERE pc.id = ANY(v_event_ids)
           AND cc.supporting_claims IS NOT NULL
    ),
    folded AS (
        SELECT (evt->>'claim_id')::uuid AS claim_id
          FROM published_changes pc,
               jsonb_array_elements(COALESCE(pc.evidence_summary, '[]'::jsonb)) AS evt
         WHERE pc.id = ANY(v_event_ids)
           AND evt->>'claim_id' IS NOT NULL
    )
    SELECT array_agg(DISTINCT claim_id) INTO v_claim_ids
      FROM (
        SELECT claim_id FROM originator
        UNION
        SELECT claim_id FROM folded
      ) all_claims
     WHERE claim_id IS NOT NULL;

    -- Move events.
    UPDATE published_changes
       SET previous_entity_id = entity_id,
           entity_id          = p_target_entity_id
     WHERE id = ANY(v_event_ids);
    GET DIAGNOSTICS v_events_moved = ROW_COUNT;

    -- Move only those claims that currently point at the source.
    -- (A claim pointing somewhere else is "wrong" data we shouldn't
    -- silently re-home.)
    IF v_claim_ids IS NOT NULL AND cardinality(v_claim_ids) > 0 THEN
        UPDATE claims
           SET previous_matched_entity_id = matched_entity_id,
               matched_entity_id          = p_target_entity_id
         WHERE id = ANY(v_claim_ids)
           AND matched_entity_id = p_source_entity_id;
        GET DIAGNOSTICS v_claims_moved = ROW_COUNT;
    END IF;

    -- Log per-event so a future undo can target a specific row.
    INSERT INTO event_reassign_log (event_id, from_entity_id, to_entity_id, moved_claim_ids, reassigned_by)
    SELECT eid, p_source_entity_id, p_target_entity_id, COALESCE(v_claim_ids, '{}'::uuid[]), p_reassigned_by
      FROM unnest(v_event_ids) AS eid;

    RETURN QUERY SELECT v_events_moved, v_claims_moved;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION reassign_events_by_size IS
    'Migration 070. Moves all live events on the source entity matching '
    '(size_before, size_after, size_unit) onto the target entity, with '
    'their contributing claims. Per-event audit trail in event_reassign_log.';

COMMIT;

-- Smoke test (run manually in SQL editor after applying):
--   SELECT proname, pronargs FROM pg_proc
--    WHERE proname IN ('merge_entities', 'reassign_events_by_size');
--   -- Expect two rows.
