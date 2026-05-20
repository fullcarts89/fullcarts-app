-- 069_orphan_entity_trigger.sql
--
-- Phase A forward invariant. Belt-and-braces with the page-layer
-- notFound() guards in /products/[id] and /brands/[name].
--
-- When the last live event of an entity is retracted, retract the
-- parent entity in the same transaction. Reuses the
-- set_entity_retracted RPC from migration 062 so the cascade behavior
-- (retract attached published_changes, mark updated_at) stays in one
-- place.
--
-- Idempotent:
--   * Fires only on transitions FALSE -> TRUE on is_retracted.
--   * If the entity is already retracted, the inner set_entity_retracted
--     call is a soft no-op because of the `IS DISTINCT FROM` guard in
--     that function's published_changes update.
--
-- Safe with the Phase A cleanup script
-- (pipeline/scripts/retract_zero_event_entities.py):
--   * Cleanup targets ORPHAN entities (zero events) by calling
--     set_entity_retracted directly on the entity.
--   * The RPC's published_changes UPDATE matches zero rows on orphans
--     (there are no events), so this trigger doesn't fire during cleanup.
--   * For non-orphan entities, this trigger doesn't apply because
--     cleanup doesn't touch them.

CREATE OR REPLACE FUNCTION trg_retract_orphaned_entity()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
    IF NEW.is_retracted = true
       AND COALESCE(OLD.is_retracted, false) = false
       AND NEW.entity_id IS NOT NULL THEN
        IF NOT EXISTS (
            SELECT 1
              FROM published_changes
             WHERE entity_id = NEW.entity_id
               AND is_retracted = false
               AND id <> NEW.id
        ) THEN
            PERFORM set_entity_retracted(NEW.entity_id, true);
        END IF;
    END IF;
    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS published_changes_orphan_check ON published_changes;

CREATE TRIGGER published_changes_orphan_check
AFTER UPDATE OF is_retracted ON published_changes
FOR EACH ROW
EXECUTE FUNCTION trg_retract_orphaned_entity();

COMMENT ON FUNCTION trg_retract_orphaned_entity() IS
    'Phase A invariant: retract parent entity when its last live event '
    'is retracted. Belt-and-braces with the page-layer notFound() '
    'guards in /products/[id] and /brands/[name].';
