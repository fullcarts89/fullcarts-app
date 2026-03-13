-- Migration 027: Create usda_product_history table
-- Per-release snapshots of every USDA branded food product.
-- Enables cross-release analysis of ingredient lists, weight changes,
-- and skimpflation detection (ingredient position changes over time).
--
-- Populated by: pipeline/scripts/build_usda_history.py
-- Key insight: FDA requires ingredients in descending order by weight.
-- If a key ingredient drops position between releases = skimpflation signal.

CREATE TABLE IF NOT EXISTS usda_product_history (
    id              BIGSERIAL PRIMARY KEY,
    gtin_upc        TEXT NOT NULL,
    fdc_id          TEXT NOT NULL,
    release_date    DATE NOT NULL,
    brand_owner     TEXT,
    brand_name      TEXT,
    description     TEXT,               -- from food.csv (actual product name)
    branded_food_category TEXT,
    ingredients     TEXT,               -- full FDA ingredient list (ordered by weight)
    package_weight  TEXT,               -- raw string from USDA
    parsed_size     NUMERIC,            -- parsed numeric value
    parsed_size_unit TEXT,              -- parsed unit (oz, g, ml, etc.)
    serving_size    TEXT,
    serving_size_unit TEXT,
    ingredients_hash TEXT,              -- MD5 hash for fast change detection
    created_at      TIMESTAMPTZ DEFAULT now(),

    -- One row per UPC per release
    CONSTRAINT uq_usda_history_upc_release UNIQUE (gtin_upc, release_date)
);

-- Fast UPC lookups across releases (the primary query pattern)
CREATE INDEX idx_usda_history_upc
    ON usda_product_history (gtin_upc);

-- Release date filtering
CREATE INDEX idx_usda_history_release
    ON usda_product_history (release_date);

-- Brand name lookups
CREATE INDEX idx_usda_history_brand_name
    ON usda_product_history (brand_name)
    WHERE brand_name IS NOT NULL;

-- Stored tsvector for full-text search (PostgREST-compatible)
ALTER TABLE usda_product_history ADD COLUMN IF NOT EXISTS search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english',
      coalesce(description, '') || ' ' ||
      coalesce(brand_name, '') || ' ' ||
      coalesce(brand_owner, ''))
  ) STORED;

CREATE INDEX idx_usda_history_search_gin
    ON usda_product_history USING GIN (search_vector);

-- Ingredient hash index for finding products whose ingredients changed
CREATE INDEX idx_usda_history_ingredients_hash
    ON usda_product_history (gtin_upc, ingredients_hash)
    WHERE ingredients_hash IS NOT NULL;

-- Category + release for filtered analysis
CREATE INDEX idx_usda_history_category_release
    ON usda_product_history (branded_food_category, release_date)
    WHERE branded_food_category IS NOT NULL;
