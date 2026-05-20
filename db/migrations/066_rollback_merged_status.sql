-- Migration 066: roll back the `merged` claim status added by migration 060
--
-- Why: the user had a prior directive against adding new values to the
-- `claims_status_check` constraint. Migration 060 violated that by carving
-- out a `merged` bucket for PR-#63 fold-ins. This migration moves those
-- rows back to `evidence`, removes the value from the constraint, and
-- drops the merged-specific index. The original problem migration 060
-- aimed to fix (the /admin/claims Evidence tab showing fold-ins alongside
-- evidence-wall claims) is solved at the UI layer in the same PR by
-- filtering the Evidence tab on `evidence_tags IS NOT NULL` instead of
-- the literal `status='evidence'` predicate — see
-- web/src/app/admin/claims/page.tsx in this PR. (This is the path that
-- was originally sketched as Option A in issue #81.)
--
-- The soft `claims_match_required` invariant from 060 is kept but pared
-- back to only require `matched_entity_id` for `status='matched'`. The
-- fold-in case (now back in `evidence`) doesn't need the invariant since
-- evidence-wall tagged claims can legitimately have `matched_entity_id`
-- NULL (the admin can tag a still-pending row).

BEGIN;

-- 1. Drop the merged-specific partial index (the evidence partial index
--    from 060 stays — `status='evidence'` is still a real bucket).
DROP INDEX IF EXISTS idx_claims_status_merged;

-- 2. Migrate every merged row back to evidence. These are PR-#63 fold-ins
--    (matched_entity_id IS NOT NULL, evidence_tags empty) — same shape as
--    they had before migration 060's backfill. Going forward the UI tab
--    will filter them out via the evidence_tags predicate instead.
UPDATE claims SET status = 'evidence' WHERE status = 'merged';

-- 3. Remove 'merged' from the allowed status set. We keep the retired
--    'unmatched' / 'approved' values in the allowlist for safety, same as
--    migration 060 did.
ALTER TABLE claims DROP CONSTRAINT IF EXISTS claims_status_check;
ALTER TABLE claims ADD CONSTRAINT claims_status_check
    CHECK (status IN (
        'pending', 'matched', 'evidence', 'discarded',
        'unmatched', 'approved'  -- retired, kept for legacy rows
    ));

-- 4. Pare back the invariant added by 060.
--    Before: status IN (matched, merged) ⇒ matched_entity_id NOT NULL.
--    After:  status = matched           ⇒ matched_entity_id NOT NULL.
--    'evidence' isn't constrained because evidence-wall tagged claims can
--    legitimately have NULL matched_entity_id (admin tagged a row that's
--    still in the pending review queue).
ALTER TABLE claims DROP CONSTRAINT IF EXISTS claims_match_required;
ALTER TABLE claims ADD CONSTRAINT claims_match_required
    CHECK (status <> 'matched' OR matched_entity_id IS NOT NULL);

COMMIT;

-- Verification queries (run after applying):
--   SELECT status, COUNT(*) FROM claims GROUP BY status ORDER BY 2 DESC;
--     Expected: 'evidence' bucket ~doubled (back to evidence-wall + fold-ins);
--     'merged' absent.
--   SELECT COUNT(*) FROM claims WHERE status = 'matched' AND matched_entity_id IS NULL;
--     Expected: 0.
