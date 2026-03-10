-- Add 'usda_size_change' to the raw_items source_type CHECK constraint.
-- Required for the USDA variance analyzer which detects size changes
-- across historical USDA releases and writes findings back to raw_items.

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'community_tip', 'receipt', 'gdelt'
    ));
