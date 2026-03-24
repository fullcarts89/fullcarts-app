-- Add 'wayback' to the raw_items source_type CHECK constraint.
-- Required for the Wayback Machine historical product analysis scraper
-- which fetches archived product pages to build size/weight timelines.

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt',
        'open_prices', 'bls', 'fred', 'walmart', 'wayback'
    ));
