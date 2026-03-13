-- Migration 026: Create usda_products lookup table
-- Denormalizes USDA branded_food.csv + food.csv data into a fast-query table
-- for product lookups during claim extraction and entity resolution.
--
-- This table is populated by pipeline/scripts/build_usda_products.py

CREATE TABLE IF NOT EXISTS usda_products (
    fdc_id      TEXT PRIMARY KEY,
    gtin_upc    TEXT,
    brand_owner TEXT,
    brand_name  TEXT,
    description TEXT,               -- from food.csv (actual product name)
    branded_food_category TEXT,
    package_weight TEXT,            -- raw string from USDA
    parsed_size NUMERIC,            -- parsed numeric value
    parsed_size_unit TEXT,          -- parsed unit (oz, g, ml, etc.)
    serving_size TEXT,
    serving_size_unit TEXT,
    ingredients TEXT,               -- full ingredients list
    release_date DATE NOT NULL,     -- which USDA release this came from
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Stored tsvector column for PostgREST-compatible full-text search.
-- PostgREST can't use expression-based GIN indexes, so we need a stored column.
ALTER TABLE usda_products ADD COLUMN IF NOT EXISTS search_vector tsvector
  GENERATED ALWAYS AS (
    to_tsvector('english',
      coalesce(description, '') || ' ' ||
      coalesce(brand_name, '') || ' ' ||
      coalesce(brand_owner, ''))
  ) STORED;

-- Fast UPC lookups (exact match)
CREATE INDEX idx_usda_products_upc
    ON usda_products (gtin_upc)
    WHERE gtin_upc IS NOT NULL;

-- Brand name searches — both lower() for SQL and plain for PostgREST eq/in
CREATE INDEX idx_usda_products_brand_name
    ON usda_products (lower(brand_name))
    WHERE brand_name IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_usda_products_brand_name_exact
    ON usda_products (brand_name);

-- Brand owner / parent company searches
CREATE INDEX idx_usda_products_brand_owner
    ON usda_products (lower(brand_owner))
    WHERE brand_owner IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_usda_products_brand_owner_exact
    ON usda_products (brand_owner);

-- Category filtering
CREATE INDEX idx_usda_products_category
    ON usda_products (branded_food_category)
    WHERE branded_food_category IS NOT NULL;

-- Full-text search GIN index on stored tsvector column
-- This is the key index for matching Reddit claims like "wheat thins" or "doritos nacho cheese"
CREATE INDEX IF NOT EXISTS idx_usda_products_search_gin
    ON usda_products USING GIN (search_vector);

-- Keep expression-based FTS index for direct SQL queries (not PostgREST)
CREATE INDEX idx_usda_products_fts
    ON usda_products USING GIN (
        to_tsvector('english',
            coalesce(description, '') || ' ' ||
            coalesce(brand_name, '') || ' ' ||
            coalesce(brand_owner, '')
        )
    );

-- Trigram indexes for fuzzy/ILIKE searches (e.g. brand_name ILIKE '%doritos%')
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX IF NOT EXISTS idx_usda_products_brand_name_trgm
    ON usda_products USING GIN (brand_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_usda_products_description_trgm
    ON usda_products USING GIN (description gin_trgm_ops);

-- Also add indexes on raw_items for Phase 2 claim extraction performance
-- These are partial indexes scoped to specific source_types for minimal overhead.

-- USDA brand name lookups on raw_items (for cross-referencing)
CREATE INDEX IF NOT EXISTS idx_raw_items_usda_brand_name
    ON raw_items (lower(raw_payload->>'brand_name'))
    WHERE source_type = 'usda';

-- Standalone source_id index for prefix searches
CREATE INDEX IF NOT EXISTS idx_raw_items_source_id
    ON raw_items (source_id);

-- Reddit full-text search on titles
CREATE INDEX IF NOT EXISTS idx_raw_items_reddit_title_fts
    ON raw_items USING GIN (
        to_tsvector('english', raw_payload->>'title')
    )
    WHERE source_type = 'reddit';
