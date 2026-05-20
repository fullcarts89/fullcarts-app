-- Migration 061: sanity guards on published_changes size fields
--
-- AI extraction occasionally returns nonsense size conversions — "1L -> 900L",
-- "1kg -> 1000kg" — which `promote_claims.py` happily wrote as upsizing events
-- because no constraint blocked them. 75 such corrupted rows are currently in
-- production. This migration:
--   1. Auto-retracts the existing violators using the in-place retraction
--      columns (`is_retracted` / `retracted_at` / `retraction_reason`). They
--      drop out of all public views automatically — every view that surfaces
--      published_changes already filters `WHERE NOT is_retracted`.
--   2. Installs a NOT VALID CHECK constraint so all future writes are
--      forced through the sanity bounds. NOT VALID lets the migration land
--      fast on a hot table; validate separately after a count confirms
--      no remaining non-retracted violators.
--
-- The companion change in `pipeline/scripts/promote_claims.py` enforces the
-- same bounds before insert, with a clear discarded-claim counter, so the
-- daily cron doesn't produce constraint violations that have to be cleaned
-- up after the fact.
--
-- Threshold choice: ratio in [0.05, 5.0]. That allows extreme but plausible
-- shrinks (a 95% shrink = ratio 0.05) and extreme but plausible upsizing
-- (a 5x family-pack would be ratio 5.0). Real-world shrinkflation events
-- cluster in [0.5, 1.0]; this gives a generous margin while still rejecting
-- the "1 -> 1000" unit-parse class of errors.

BEGIN;

-- 1. Backfill: retract existing violators.
UPDATE published_changes
   SET is_retracted = true,
       retracted_at = COALESCE(retracted_at, now()),
       retraction_reason = COALESCE(
           retraction_reason,
           'auto-retracted by migration 061: size_after/size_before ratio '
           || 'outside [0.05, 5.0] — suspected unit-parse error'
       )
 WHERE NOT is_retracted
   AND size_before IS NOT NULL
   AND size_after IS NOT NULL
   AND size_before > 0
   AND (size_after / size_before > 5.0 OR size_after / size_before < 0.05);

-- 2. Hard CHECK going forward.
-- Edge cases:
--   - is_retracted=true: allowed (retracted rows are the trash bin; the
--     point of the constraint is to keep new live rows clean, not to
--     re-judge already-retired data).
--   - NULL size_before or size_after: allowed (migration 055 made these
--     nullable for skimpflation events, which carry no size change).
--   - size_before = 0: rejected (division-by-zero; a legitimate product
--     never starts at zero size).
ALTER TABLE published_changes
    ADD CONSTRAINT published_changes_size_ratio_sane
    CHECK (
        is_retracted = true
        OR size_before IS NULL
        OR size_after IS NULL
        OR (size_before > 0 AND size_after / size_before BETWEEN 0.05 AND 5.0)
    ) NOT VALID;

COMMIT;

-- Verification queries (run after applying):
--   SELECT COUNT(*) FROM published_changes
--    WHERE retraction_reason LIKE 'auto-retracted by migration 061%';
--     Expected: ~75 (the known corrupted upsizing events).
--
--   SELECT id, brand, product_name, size_before, size_after, change_type
--     FROM published_changes
--    WHERE NOT is_retracted
--      AND size_before IS NOT NULL AND size_after IS NOT NULL
--      AND size_before > 0
--      AND (size_after / size_before > 5.0 OR size_after / size_before < 0.05);
--     Expected: empty result. (Retracted rows excluded by design — the
--     CHECK constraint exempts them.)
--
-- Once verified clean:
--   ALTER TABLE published_changes
--     VALIDATE CONSTRAINT published_changes_size_ratio_sane;
