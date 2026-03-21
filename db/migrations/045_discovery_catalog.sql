-- Route discovery scrapers to product catalog tables instead of raw_items.
--
-- Adds tracking columns to pack_variants so we know which discovery scraper
-- first cataloged a product, and adds 'catalog_size_change' source type
-- for the variance analyzer that detects actual size changes over time.

-- ── 1. Discovery tracking on pack_variants ───────────────────────────────────

ALTER TABLE pack_variants ADD COLUMN IF NOT EXISTS discovery_source TEXT;
ALTER TABLE pack_variants ADD COLUMN IF NOT EXISTS discovery_id    TEXT;

-- Same discovery scraper shouldn't catalog the same external ID twice.
-- NULLS NOT DISTINCT so rows without discovery fields don't conflict.
CREATE UNIQUE INDEX IF NOT EXISTS uq_pack_variants_discovery
    ON pack_variants (discovery_source, discovery_id)
    WHERE discovery_source IS NOT NULL AND discovery_id IS NOT NULL;

-- ── 2. Allow catalog_size_change in raw_items ────────────────────────────────

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt',
        'kroger_change', 'off_change', 'open_prices',
        'catalog_size_change'
    ));
