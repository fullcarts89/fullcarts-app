-- Migration 065: entity edit + merge audit logs (Phase 2D steps 2 + 4)
--
-- Phase 2D step 2 introduces inline edit on `/admin/entities` — admin can
-- change brand, canonical_name, category, manufacturer on a row. We log
-- every edit to `entity_edit_log` so the admin can later see "what changed
-- and when" without having to scrape published_changes diffs.
--
-- Phase 2D step 4 introduces "merge entity B into entity A" — moves every
-- claim / variant / published_change off B onto A, then retracts B. We log
-- the merge to `entity_merge_log` with counts so reversibility is possible
-- in principle (the merge function returns the row id and the row holds
-- enough state to write a manual unmerge if it's ever needed). The function
-- itself is committed in a separate transaction within the migration so
-- partial-merge state can't escape on failure.

BEGIN;

-- ── entity_edit_log ──────────────────────────────────────────────
-- Append-only. One row per field changed; an "edit name + category" UI
-- action lands as two rows. Simpler to query than a JSONB diff column.

CREATE TABLE entity_edit_log (
    id          BIGSERIAL PRIMARY KEY,
    entity_id   UUID NOT NULL REFERENCES product_entities(id) ON DELETE CASCADE,
    field       TEXT NOT NULL
        CHECK (field IN ('brand', 'canonical_name', 'category', 'manufacturer')),
    old_value   TEXT,
    new_value   TEXT,
    edited_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    edited_by   TEXT
);

COMMENT ON TABLE entity_edit_log IS
    'Append-only audit trail of /admin/entities inline-edit actions. '
    'One row per field changed; the application writes via the '
    'set_entity_field() RPC which guarantees the log row and the table '
    'update land in the same transaction.';

CREATE INDEX idx_entity_edit_log_entity
    ON entity_edit_log (entity_id, edited_at DESC);
CREATE INDEX idx_entity_edit_log_recent
    ON entity_edit_log (edited_at DESC);

-- RPC: set one field on an entity and record the change in entity_edit_log.
-- Wraps both ops in a transaction so the log can't drift from reality.
-- Returns the new row id from entity_edit_log so the caller can confirm.
CREATE OR REPLACE FUNCTION set_entity_field(
    p_entity_id UUID,
    p_field     TEXT,
    p_value     TEXT,
    p_edited_by TEXT DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_old TEXT;
    v_log_id BIGINT;
BEGIN
    IF p_field NOT IN ('brand', 'canonical_name', 'category', 'manufacturer') THEN
        RAISE EXCEPTION 'set_entity_field: unsupported field %', p_field
            USING HINT = 'Allowed: brand, canonical_name, category, manufacturer';
    END IF;

    -- Fetch current value into a text bucket regardless of underlying type
    -- so the log row stores a stable representation. category + manufacturer
    -- are already TEXT; brand + canonical_name are NOT NULL TEXT.
    EXECUTE format('SELECT %I FROM product_entities WHERE id = $1', p_field)
        INTO v_old USING p_entity_id;

    -- No-op when value didn't change. Skip the log too.
    IF v_old IS NOT DISTINCT FROM p_value THEN
        RETURN NULL;
    END IF;

    EXECUTE format('UPDATE product_entities SET %I = $1 WHERE id = $2', p_field)
        USING p_value, p_entity_id;

    INSERT INTO entity_edit_log (entity_id, field, old_value, new_value, edited_by)
    VALUES (p_entity_id, p_field, v_old, p_value, p_edited_by)
    RETURNING id INTO v_log_id;

    RETURN v_log_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION set_entity_field IS
    'Single-field update + log in one transaction. NULL return means '
    'the new value matched the existing one (no-op).';


-- ── entity_merge_log ─────────────────────────────────────────────
-- One row per successful merge. Reversibility requires both source and
-- target ids + counts so a manual unmerge can be reconstructed.

CREATE TABLE entity_merge_log (
    id              BIGSERIAL PRIMARY KEY,
    source_id       UUID NOT NULL REFERENCES product_entities(id) ON DELETE RESTRICT,
    target_id       UUID NOT NULL REFERENCES product_entities(id) ON DELETE RESTRICT,
    merged_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    merged_by       TEXT,
    claims_moved    INTEGER NOT NULL DEFAULT 0,
    events_moved    INTEGER NOT NULL DEFAULT 0,
    variants_moved  INTEGER NOT NULL DEFAULT 0,

    CHECK (source_id <> target_id)
);

COMMENT ON TABLE entity_merge_log IS
    'Append-only audit of entity merges (Phase 2D step 4). The source '
    'entity is retracted post-merge; this log preserves the linkage for '
    'reversibility and historical reporting.';

CREATE INDEX idx_entity_merge_log_source ON entity_merge_log (source_id);
CREATE INDEX idx_entity_merge_log_target ON entity_merge_log (target_id);
CREATE INDEX idx_entity_merge_log_recent ON entity_merge_log (merged_at DESC);

-- RPC: merge source entity into target. Moves every dependent row,
-- retracts the source, and logs the operation.
-- All-or-nothing — wrapped in a single transaction.
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

    -- Sanity: both must exist.
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_source_id) THEN
        RAISE EXCEPTION 'merge_entities: source entity % not found', p_source_id;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_target_id) THEN
        RAISE EXCEPTION 'merge_entities: target entity % not found', p_target_id;
    END IF;

    -- 1. Move claims.
    UPDATE claims SET matched_entity_id = p_target_id
     WHERE matched_entity_id = p_source_id;
    GET DIAGNOSTICS v_claims_moved = ROW_COUNT;

    -- 2. Move published_changes.
    UPDATE published_changes SET entity_id = p_target_id
     WHERE entity_id = p_source_id;
    GET DIAGNOSTICS v_events_moved = ROW_COUNT;

    -- 3. Move pack_variants.
    UPDATE pack_variants SET entity_id = p_target_id
     WHERE entity_id = p_source_id;
    GET DIAGNOSTICS v_variants_moved = ROW_COUNT;

    -- 4. Retract the source so it stops surfacing publicly.
    UPDATE product_entities
       SET is_retracted = true
     WHERE id = p_source_id;

    -- 5. Log it.
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
    'Phase 2D step 4. Moves all dependent rows from source to target, '
    'retracts source, logs the operation. All-or-nothing.';

COMMIT;

-- Verification:
--   SELECT proname FROM pg_proc
--    WHERE proname IN ('set_entity_field', 'merge_entities');
--     Expected: both functions exist.
--
--   SELECT COUNT(*) FROM entity_edit_log;   -- 0 until first edit
--   SELECT COUNT(*) FROM entity_merge_log;  -- 0 until first merge
