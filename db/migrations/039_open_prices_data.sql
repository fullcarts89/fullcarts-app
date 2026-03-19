-- Migration 039: Open Prices structured data table.
--
-- Open Prices (prices.openfoodfacts.org) is a crowdsourced database of
-- receipt-level grocery prices run by Open Food Facts.
--
-- Raw price objects land in raw_items (source_type = 'open_prices').
-- This table stores structured/queryable versions of those records.
--
-- 1. Add 'open_prices' to the raw_items source_type constraint.
-- 2. Create open_prices_data table for direct querying.
-- 3. Enable RLS: public read, service_role write.

-- ── 1. Extend raw_items source_type constraint ────────────────────────────────

ALTER TABLE raw_items DROP CONSTRAINT IF EXISTS raw_items_source_type_check;
ALTER TABLE raw_items ADD CONSTRAINT raw_items_source_type_check
    CHECK (source_type IN (
        'reddit', 'news', 'openfoodfacts', 'kroger_api',
        'usda', 'usda_size_change', 'usda_turnover_change',
        'usda_nutrition', 'community_tip', 'receipt', 'gdelt',
        'kroger_change', 'off_change', 'open_prices'
    ));

-- ── 2. Open Prices structured data table ─────────────────────────────────────

CREATE TABLE IF NOT EXISTS open_prices_data (
    -- Open Prices primary key (matches id in the API response)
    open_price_id       BIGINT PRIMARY KEY,

    -- Product identification
    product_code        TEXT,           -- Barcode / UPC / EAN
    product_name        TEXT,           -- Product name (may be NULL)

    -- Price data
    price               NUMERIC(12, 4),
    currency            TEXT,           -- ISO 4217 (e.g. "USD", "EUR")
    price_date          DATE,           -- Date price was observed (from receipt)
    price_per           TEXT,           -- Unit basis: "UNIT", "KG", "L", etc.
    price_is_discounted BOOLEAN DEFAULT FALSE,
    price_without_discount NUMERIC(12, 4),
    discount_type       TEXT,           -- "QUANTITY", "SALE", "SEASONAL", etc.

    -- Location / store info
    location_osm_id     BIGINT,
    location_osm_type   TEXT,           -- "NODE", "WAY", "RELATION"
    location_name       TEXT,           -- OSM name of the location
    location_city       TEXT,
    location_country    TEXT,           -- Full country name
    location_country_code TEXT,         -- ISO 3166-1 alpha-2 (e.g. "US")

    -- Source traceability
    source_url          TEXT,           -- https://prices.openfoodfacts.org/prices/{id}
    proof_type          TEXT,           -- "RECEIPT", "PRICE_TAG", etc.

    -- Full raw payload for future extraction
    raw_payload         JSONB,

    -- Timestamps
    price_submitted_at  TIMESTAMPTZ,    -- When price was submitted to Open Prices
    scraped_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_open_prices_product_code
    ON open_prices_data (product_code);

CREATE INDEX IF NOT EXISTS idx_open_prices_price_date
    ON open_prices_data (price_date DESC);

CREATE INDEX IF NOT EXISTS idx_open_prices_currency
    ON open_prices_data (currency);

CREATE INDEX IF NOT EXISTS idx_open_prices_country_code
    ON open_prices_data (location_country_code);

CREATE INDEX IF NOT EXISTS idx_open_prices_submitted_at
    ON open_prices_data (price_submitted_at DESC);

-- ── 3. Row Level Security ─────────────────────────────────────────────────────

ALTER TABLE open_prices_data ENABLE ROW LEVEL SECURITY;

-- Anyone can read prices (public consumer-facing data)
CREATE POLICY "open_prices_public_read"
    ON open_prices_data
    FOR SELECT
    USING (true);

-- Only the service role (pipeline) can write
CREATE POLICY "open_prices_service_write"
    ON open_prices_data
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
