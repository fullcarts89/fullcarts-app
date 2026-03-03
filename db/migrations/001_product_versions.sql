-- ============================================================
-- Migration 001: Add product_versions table
-- Enables longitudinal tracking of product size/price over time
-- ============================================================
-- Run in Supabase SQL Editor AFTER the base schema (supabase_seed.sql)

BEGIN;

-- Extend products table with fields needed for the v2 data model
ALTER TABLE products ADD COLUMN IF NOT EXISTS updated_at    timestamptz DEFAULT now();
ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url     text;
ALTER TABLE products ADD COLUMN IF NOT EXISTS description   text;
ALTER TABLE products ADD COLUMN IF NOT EXISTS upc_verified  boolean DEFAULT false;
ALTER TABLE products ADD COLUMN IF NOT EXISTS aliases       text[];  -- alternate names / spellings

-- ── PRODUCT VERSIONS ──────────────────────────────────────
-- Each row = one observed state of a product at a point in time.
-- A product with 3 size changes has 4 version rows.
CREATE TABLE IF NOT EXISTS product_versions (
  id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  product_upc     text NOT NULL REFERENCES products(upc) ON DELETE CASCADE,
  observed_date   date NOT NULL,

  -- Size / quantity
  size            numeric NOT NULL,
  unit            text    NOT NULL,

  -- Price (nullable — not all sources report price)
  price           numeric CHECK (price >= 0),
  retailer        text,

  -- Computed: price per unit (stored for fast queries)
  price_per_unit  numeric GENERATED ALWAYS AS (
    CASE WHEN size > 0 AND price IS NOT NULL
         THEN round(price / size, 4)
         ELSE NULL
    END
  ) STORED,

  -- Evidence & provenance
  evidence_url    text,
  source          text DEFAULT 'community',
  source_url      text,
  notes           text,

  -- Audit
  created_at      timestamptz DEFAULT now(),
  created_by      text,  -- 'admin', 'scraper', 'community', session_id

  -- Prevent duplicate observations of same product/date/source
  UNIQUE(product_upc, observed_date, source)
);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_pv_product_upc    ON product_versions(product_upc);
CREATE INDEX IF NOT EXISTS idx_pv_observed_date  ON product_versions(observed_date DESC);
CREATE INDEX IF NOT EXISTS idx_pv_product_date   ON product_versions(product_upc, observed_date DESC);
CREATE INDEX IF NOT EXISTS idx_pv_source         ON product_versions(source);

-- RLS
ALTER TABLE product_versions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read product_versions"
  ON product_versions FOR SELECT USING (true);
CREATE POLICY "Anon can insert product_versions"
  ON product_versions FOR INSERT WITH CHECK (true);
CREATE POLICY "Service role manages product_versions"
  ON product_versions FOR ALL USING (auth.role() = 'service_role');

COMMIT;
