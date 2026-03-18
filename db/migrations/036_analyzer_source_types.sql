-- Add 'kroger_change' and 'off_change' source_types for automated analyzers.
-- Kroger analyzer detects size/price changes from weekly variant_observations.
-- OFF analyzer detects size changes from daily Open Food Facts observations.

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt',
        'kroger_change', 'off_change'
    ));
