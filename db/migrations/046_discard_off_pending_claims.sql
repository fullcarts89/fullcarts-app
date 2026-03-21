-- Bulk-discard pending claims sourced from openfoodfacts raw_items.
-- These were created before the catalog refactor; OFF data now flows
-- through the product catalog + variance analysis pipeline instead.
-- Reversible: just UPDATE ... SET status = 'pending' WHERE ... if needed.

UPDATE claims
SET    status = 'discarded'
WHERE  status = 'pending'
AND    raw_item_id IN (
    SELECT id FROM raw_items WHERE source_type = 'openfoodfacts'
);
