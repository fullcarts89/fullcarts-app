-- Add claim_index to support multiple claims per raw_item
-- Default 0 for single-claim extractions (Reddit)
-- Index 0, 1, 2... for multi-claim extractions (news articles mentioning multiple products)

ALTER TABLE claims ADD COLUMN IF NOT EXISTS claim_index integer NOT NULL DEFAULT 0;

-- Drop the old unique constraint and recreate with claim_index
ALTER TABLE claims DROP CONSTRAINT IF EXISTS claims_raw_item_id_extractor_version_key;
ALTER TABLE claims ADD CONSTRAINT claims_raw_item_id_extractor_version_idx_key
    UNIQUE (raw_item_id, extractor_version, claim_index);
