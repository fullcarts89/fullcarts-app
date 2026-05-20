-- Migration 064: claim status audit log trigger
--
-- Records every UPDATE that changes `claims.status` into `claim_status_log`,
-- including the originating session identity when one is available
-- (PostgREST sets app.role/app.name for service-role calls).
--
-- Motivation: the cleanup_stuck_matched bug (PR #80) silently moved
-- ~2,700 originator claims from 'matched' → 'evidence' over two days
-- without leaving any trace. Recovery required reverse-engineering
-- the original status from `change_candidates.supporting_claims[]`,
-- which only works because that array is immutable post-create. Future
-- bugs in other scripts wouldn't necessarily have that escape hatch.
--
-- With this trigger, any future status drift produces an audit trail
-- the admin can grep, group, and roll back.
--
-- Design notes:
--   - INSERT-only — never updated or deleted. The trigger doesn't fire on
--     itself (the log is a different table) so there's no recursion risk.
--   - Only fires when status ACTUALLY changes (NEW.status IS DISTINCT FROM
--     OLD.status). Other UPDATEs to claims (filling matched_entity_id,
--     evidence_tags, etc.) don't log.
--   - changed_by captures the postgres `current_user` plus any
--     application-supplied session label via `current_setting('app.label',
--     true)`. Pipeline scripts can set this with `SELECT set_config(
--     'app.label', 'promote_claims_v3', false);` if they want their
--     entries tagged.

BEGIN;

CREATE TABLE claim_status_log (
    id          BIGSERIAL PRIMARY KEY,
    claim_id    UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    old_status  TEXT,
    new_status  TEXT NOT NULL,
    changed_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    changed_by  TEXT
);

COMMENT ON TABLE claim_status_log IS
    'Append-only audit trail of claim.status transitions. Populated by '
    'the trg_claim_status_log AFTER UPDATE trigger. Use for detecting '
    'silent bulk-status drifts (regression-of-PR-#80-class bugs).';

CREATE INDEX idx_claim_status_log_claim
    ON claim_status_log (claim_id, changed_at DESC);
CREATE INDEX idx_claim_status_log_recent
    ON claim_status_log (changed_at DESC);
CREATE INDEX idx_claim_status_log_transition
    ON claim_status_log (old_status, new_status);

CREATE OR REPLACE FUNCTION fn_claim_status_log() RETURNS TRIGGER AS $$
BEGIN
    -- IS DISTINCT FROM handles NULL transitions cleanly (NULL vs NULL is
    -- "same"; NULL vs 'pending' is "different").
    IF NEW.status IS DISTINCT FROM OLD.status THEN
        INSERT INTO claim_status_log (
            claim_id, old_status, new_status, changed_by
        ) VALUES (
            NEW.id,
            OLD.status,
            NEW.status,
            current_user || COALESCE(
                ' / ' || NULLIF(current_setting('app.label', true), ''),
                ''
            )
        );
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_claim_status_log
    AFTER UPDATE OF status ON claims
    FOR EACH ROW
    EXECUTE FUNCTION fn_claim_status_log();

COMMIT;

-- Verification:
--   SELECT trigger_name, action_timing, event_manipulation
--     FROM information_schema.triggers
--    WHERE event_object_table = 'claims';
--     Expected: trg_claim_status_log / AFTER / UPDATE.
--
-- Sample admin queries the log makes possible:
--   -- Find any bulk-flip events
--   SELECT date_trunc('hour', changed_at) AS hr,
--          old_status, new_status, COUNT(*) AS n,
--          array_agg(DISTINCT changed_by) AS actors
--     FROM claim_status_log
--    WHERE changed_at > now() - interval '48 hours'
--    GROUP BY 1, 2, 3
--    HAVING COUNT(*) > 100
--    ORDER BY hr DESC;
--
--   -- Per-claim history for a suspect row
--   SELECT old_status, new_status, changed_at, changed_by
--     FROM claim_status_log
--    WHERE claim_id = $1
--    ORDER BY changed_at;
