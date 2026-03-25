-- Bulk-discard pending Open Food Facts claims that lack variance analysis.
-- These are historical backfill claims (circa 2026-03-10) where no old/new
-- size comparison exists — they add noise to the review queue.
-- Reversible: UPDATE ... SET status = 'pending' WHERE ... if needed.

UPDATE claims
SET    status = 'discarded'
WHERE  status = 'pending'
AND    raw_item_id IN (
    SELECT id FROM raw_items
    WHERE source_type IN ('openfoodfacts', 'off_change')
)
AND    (old_size IS NULL OR new_size IS NULL);
