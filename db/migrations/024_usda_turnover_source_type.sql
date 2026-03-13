-- Add 'usda_turnover_change' to the raw_items source_type CHECK constraint.
-- Required for the USDA turnover analyzer which detects product-turnover
-- shrinkflation: same brand+product appearing with different UPCs and
-- smaller sizes across USDA quarterly releases.

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'community_tip', 'receipt', 'gdelt'
    ));
