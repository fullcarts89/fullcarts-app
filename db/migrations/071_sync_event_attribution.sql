-- Migration 071: keep published_changes.brand + product_name in sync
-- with product_entities when entities are merged, reassigned, or
-- brand-rebranded.
--
-- BACKGROUND
--   published_changes carries a denormalized snapshot of (brand,
--   product_name) taken at promote_claims time. The denorm was
--   convenient at write time but became a correctness bug once the
--   admin tooling could mutate product_entities.brand and
--   product_entities.canonical_name. After a brand-merge or entity-
--   merge, /brands/[name] joins events by published_changes.brand and
--   so excluded entities whose denorm column had drifted away from the
--   canonical entity attribution.
--
--   This migration:
--     1. Updates merge_entities() RPC to sync brand/product_name on
--        every moved event row.
--     2. Updates reassign_events_by_size() RPC to do the same on every
--        moved event row.
--     3. Runs an idempotent ON-DEPLOY sync to fix any pre-existing
--        drift (already run once manually via the Management API on
--        2026-05-22 — re-running here is a no-op when there's no drift).

BEGIN;

-- ─── merge_entities: sync brand/product_name to target ──────────────
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
    v_target_brand TEXT;
    v_target_name  TEXT;
BEGIN
    IF p_source_id = p_target_id THEN
        RAISE EXCEPTION 'merge_entities: source and target are the same';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_source_id) THEN
        RAISE EXCEPTION 'merge_entities: source entity % not found', p_source_id;
    END IF;
    SELECT brand, canonical_name INTO v_target_brand, v_target_name
      FROM product_entities WHERE id = p_target_id;
    IF v_target_brand IS NULL THEN
        RAISE EXCEPTION 'merge_entities: target entity % not found', p_target_id;
    END IF;

    UPDATE claims
       SET previous_matched_entity_id = matched_entity_id,
           matched_entity_id          = p_target_id
     WHERE matched_entity_id = p_source_id;
    GET DIAGNOSTICS v_claims_moved = ROW_COUNT;

    UPDATE published_changes
       SET previous_entity_id = entity_id,
           entity_id          = p_target_id,
           brand              = v_target_brand,
           product_name       = v_target_name
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

-- ─── reassign_events_by_size: sync brand/product_name to target ─────
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
    v_target_brand    TEXT;
    v_target_name     TEXT;
BEGIN
    IF p_source_entity_id = p_target_entity_id THEN
        RAISE EXCEPTION 'reassign_events_by_size: source and target are the same';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM product_entities WHERE id = p_source_entity_id) THEN
        RAISE EXCEPTION 'reassign_events_by_size: source entity % not found', p_source_entity_id;
    END IF;
    SELECT brand, canonical_name INTO v_target_brand, v_target_name
      FROM product_entities WHERE id = p_target_entity_id;
    IF v_target_brand IS NULL THEN
        RAISE EXCEPTION 'reassign_events_by_size: target entity % not found', p_target_entity_id;
    END IF;

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

    UPDATE published_changes
       SET previous_entity_id = entity_id,
           entity_id          = p_target_entity_id,
           brand              = v_target_brand,
           product_name       = v_target_name
     WHERE id = ANY(v_event_ids);
    GET DIAGNOSTICS v_events_moved = ROW_COUNT;

    IF v_claim_ids IS NOT NULL AND cardinality(v_claim_ids) > 0 THEN
        UPDATE claims
           SET previous_matched_entity_id = matched_entity_id,
               matched_entity_id          = p_target_entity_id
         WHERE id = ANY(v_claim_ids)
           AND matched_entity_id = p_source_entity_id;
        GET DIAGNOSTICS v_claims_moved = ROW_COUNT;
    END IF;

    INSERT INTO event_reassign_log (event_id, from_entity_id, to_entity_id, moved_claim_ids, reassigned_by)
    SELECT eid, p_source_entity_id, p_target_entity_id, COALESCE(v_claim_ids, '{}'::uuid[]), p_reassigned_by
      FROM unnest(v_event_ids) AS eid;

    RETURN QUERY SELECT v_events_moved, v_claims_moved;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ─── one-time sync, idempotent on re-deploy ─────────────────────────
-- Already applied manually via Management API on 2026-05-22 (600 rows).
-- Keeping here so that if the migration is replayed from scratch on a
-- fresh DB the data ends up consistent.
UPDATE published_changes pc
   SET brand        = pe.brand,
       product_name = pe.canonical_name
  FROM product_entities pe
 WHERE pc.entity_id = pe.id
   AND (pc.brand <> pe.brand OR pc.product_name <> pe.canonical_name);

COMMIT;
