-- Migration 068: fix set_entity_retracted column-name ambiguity
--
-- The original definition (migration 062) declared
--   RETURNS TABLE (entity_id UUID, events_affected INTEGER)
-- and then ran
--   UPDATE published_changes ... WHERE entity_id = p_entity_id
-- inside the body. PostgreSQL treats the bare `entity_id` reference in the
-- UPDATE's WHERE as ambiguous: it could mean the output-column variable
-- `entity_id` declared in RETURNS TABLE, OR the `entity_id` column on the
-- target table. Result: error 42702 ("column reference ambiguous") on
-- every call.
--
-- This bug means every prior call to the RPC failed:
--   - The /admin/entities "Retract" button (since PR #75 deploy)
--   - The auto-triage script's retract_entity branch
--   - Any direct rpc('set_entity_retracted', ...) call
-- It went undetected because no admin had actually clicked the retract
-- button on a live entity since the migration landed; the auto-triage
-- script in this session is the first attempt that surfaced it.
--
-- Fix: qualify the WHERE-clause column reference as
-- `published_changes.entity_id = p_entity_id` so the parser knows it's
-- the table column, not the output variable. The first UPDATE on
-- `product_entities` is also qualified for consistency even though
-- `product_entities.id` (the column name there) didn't collide.

CREATE OR REPLACE FUNCTION set_entity_retracted(
    p_entity_id  UUID,
    p_retracted  BOOLEAN
)
RETURNS TABLE (entity_id UUID, events_affected INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_events_affected INTEGER;
BEGIN
    UPDATE product_entities pe
       SET is_retracted = p_retracted,
           updated_at   = now()
     WHERE pe.id = p_entity_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'entity % not found', p_entity_id;
    END IF;

    UPDATE published_changes pc
       SET is_retracted = p_retracted
     WHERE pc.entity_id = p_entity_id
       AND pc.is_retracted IS DISTINCT FROM p_retracted;

    GET DIAGNOSTICS v_events_affected = ROW_COUNT;

    RETURN QUERY SELECT p_entity_id, v_events_affected;
END;
$$;

-- Verification:
--   SELECT * FROM set_entity_retracted('<any test entity id>'::uuid, false);
--     Should return a row, no error. Re-running with the same args is a
--     no-op on the products table (FOUND=true on the first UPDATE since
--     a row exists, but events_affected will be 0 since nothing changes).
