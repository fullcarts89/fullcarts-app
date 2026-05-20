-- Migration 060: claim status discipline
--
-- Splits the overloaded `status='evidence'` value into two distinct meanings:
--   evidence  — claim was tagged for an evidence-wall channel
--               (Skimpflation / So Smol / Slack Fill / Stretchflation /
--                Spot the Difference / Paper Thin / Not as Advertised).
--               Recognisable by a non-empty `evidence_tags` array.
--   merged    — claim was folded into an existing published_changes event
--               during dedup (PR #63 behaviour). Recognisable by
--               `matched_entity_id IS NOT NULL` and empty `evidence_tags`.
--
-- The two meanings were collapsed onto the same status by PR #63, which made
-- the `/admin/claims` Evidence tab count ~4,600 fold-ins alongside a few
-- hundred genuine tagged-evidence claims. CLAUDE.md flagged this as a
-- "Known gotcha"; this migration removes it.
--
-- Order of operations matters because Python writers and web readers ship in
-- the same PR:
--   1. APPLY this migration to Supabase first (adds 'merged' to the CHECK
--      constraint, backfills rows that should be 'merged').
--   2. Then merge the code PR (promote_claims + cleanup_stuck_matched start
--      writing 'merged'; admin UI gains a Merged tab).
-- Reversing this order makes promote_claims fail the CHECK on its next run.

BEGIN;

-- 1. Expand the CHECK constraint.
-- We KEEP 'unmatched' and 'approved' in the allowed set for now. Both are
-- retired (PR fd01dea retired 'unmatched'; auto_approve_claims.py was
-- removed in PR #70) but legacy rows may still exist; a follow-up migration
-- can drop them after a `SELECT status, COUNT(*) FROM claims GROUP BY status`
-- confirms zero residue.
ALTER TABLE claims DROP CONSTRAINT IF EXISTS claims_status_check;
ALTER TABLE claims ADD CONSTRAINT claims_status_check
    CHECK (status IN (
        'pending', 'matched', 'merged', 'evidence', 'discarded',
        'unmatched', 'approved'  -- retired, kept for legacy rows
    ));

-- 2. Backfill: fold-ins → 'merged'.
-- Discriminator:
--   matched_entity_id IS NOT NULL  → promote_claims has touched this row
--   AND (evidence_tags IS NULL
--        OR array_length(evidence_tags, 1) IS NULL)
--                                  → admin has NOT tagged it for evidence wall
-- This leaves evidence-wall tagged claims in 'evidence' (their original
-- meaning) and routes the PR #63 fold-ins to 'merged'.
UPDATE claims
   SET status = 'merged'
 WHERE status = 'evidence'
   AND matched_entity_id IS NOT NULL
   AND (evidence_tags IS NULL OR array_length(evidence_tags, 1) IS NULL);

-- 3. Soft status⇒column invariant.
-- 'matched' (event originator) and 'merged' (fold-in) both require
-- `matched_entity_id` to be set. Without this invariant the cleanup_stuck_
-- matched bug could mutate a claim's status without leaving any trace.
-- Marked NOT VALID so the migration lands fast on a hot table; validate
-- separately once we've confirmed no historic violations:
--     ALTER TABLE claims VALIDATE CONSTRAINT claims_match_required;
ALTER TABLE claims
    ADD CONSTRAINT claims_match_required
    CHECK (
        status NOT IN ('matched', 'merged')
        OR matched_entity_id IS NOT NULL
    ) NOT VALID;

-- 4. Index supporting the admin Evidence-tab query.
-- After the backfill, status='evidence' is a small bucket (hundreds, not
-- thousands). A partial index keeps `WHERE status = 'evidence'` cheap as
-- the table grows.
CREATE INDEX IF NOT EXISTS idx_claims_status_evidence
    ON claims (id)
    WHERE status = 'evidence';

CREATE INDEX IF NOT EXISTS idx_claims_status_merged
    ON claims (id)
    WHERE status = 'merged';

COMMIT;

-- Verification queries (run after applying):
--   SELECT status, COUNT(*) FROM claims GROUP BY status ORDER BY 2 DESC;
--     Expected: 'pending', 'matched' (~2,800), 'merged' (~4,600),
--               'evidence' (hundreds), 'discarded' (large).
--   SELECT COUNT(*) FROM claims
--    WHERE status IN ('matched', 'merged') AND matched_entity_id IS NULL;
--     Expected: 0. If non-zero, investigate before VALIDATE CONSTRAINT.
