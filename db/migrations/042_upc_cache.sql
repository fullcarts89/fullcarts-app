-- Migration 042: UPC/barcode resolution cache
--
-- Caching layer that resolves barcodes to product metadata using free public
-- APIs (UPCitemdb, Brocade.io, Open Food Facts). Results are stored so we
-- never look up the same barcode twice. Cache misses (not_found=true) are
-- also stored to avoid wasting API quota re-querying unknown barcodes.
--
-- Resolution chain (tried in order):
--   1. upcitemdb free tier  — 100 lookups/day, 6/minute rate limit
--   2. brocade.io           — free, no auth required
--   3. Open Food Facts      — free, already in our stack

CREATE TABLE IF NOT EXISTS upc_cache (
    barcode         TEXT        PRIMARY KEY,            -- UPC/EAN/GTIN barcode string
    product_name    TEXT,
    brand           TEXT,
    category        TEXT,
    description     TEXT,
    weight          TEXT,                               -- raw weight string ("16 oz", "1 lb", etc.)
    weight_oz       NUMERIC,                            -- normalized weight in ounces
    image_url       TEXT,
    source          TEXT,                               -- which API resolved it
    raw_response    JSONB,                              -- full API response for future extraction
    resolved_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    not_found       BOOLEAN     NOT NULL DEFAULT false  -- true = cached miss, don't re-query

    CONSTRAINT upc_cache_source_check CHECK (
        source IS NULL OR source IN ('upcitemdb', 'brocade', 'openfoodfacts')
    )
);

-- Fast lookups by brand (for brand-level analysis)
CREATE INDEX IF NOT EXISTS idx_upc_cache_brand
    ON upc_cache (brand)
    WHERE brand IS NOT NULL;

-- Fast lookups by category
CREATE INDEX IF NOT EXISTS idx_upc_cache_category
    ON upc_cache (category)
    WHERE category IS NOT NULL;

-- Filter out cached misses when joining to find resolvable barcodes
CREATE INDEX IF NOT EXISTS idx_upc_cache_not_found
    ON upc_cache (not_found)
    WHERE not_found = false;

-- ── Row Level Security ────────────────────────────────────────────────────────

ALTER TABLE upc_cache ENABLE ROW LEVEL SECURITY;

-- Anyone can read cached product data (public information)
CREATE POLICY "Public read upc_cache"
    ON upc_cache FOR SELECT
    USING (true);

-- Only the service role (pipeline) can write
CREATE POLICY "Service role write upc_cache"
    ON upc_cache FOR ALL
    USING (auth.role() = 'service_role');

-- ── Comment ───────────────────────────────────────────────────────────────────

COMMENT ON TABLE upc_cache IS
    'Barcode-to-product metadata cache. Resolved via UPCitemdb, Brocade.io, and '
    'Open Food Facts. Cache misses (not_found=true) are stored to avoid wasting '
    'API quota on barcodes that do not exist in any database.';

COMMENT ON COLUMN upc_cache.not_found IS
    'true = all APIs returned no result for this barcode. Cached to prevent '
    're-querying barcodes that are genuinely unknown.';

COMMENT ON COLUMN upc_cache.source IS
    'Which API first resolved this barcode: upcitemdb, brocade, or openfoodfacts.';

COMMENT ON COLUMN upc_cache.weight_oz IS
    'Package weight normalized to ounces. Parsed from the raw weight string. '
    'NULL if weight is not listed or could not be parsed.';
