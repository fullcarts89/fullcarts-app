-- Add 'usda_nutrition' to the raw_items source_type CHECK constraint.
-- Required for importing nutrition-based skimpflation results as claims.

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt'
    ));

-- Additional indexes on claims for extraction pipeline queries
CREATE INDEX IF NOT EXISTS idx_claims_extractor
    ON claims (extractor_version);

CREATE INDEX IF NOT EXISTS idx_claims_confidence_overall
    ON claims (((confidence->>'overall')::numeric))
    WHERE confidence->>'overall' IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_claims_extracted_at
    ON claims (extracted_at);
