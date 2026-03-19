-- Migration 040: FRED CPI time-series data
--
-- Stores monthly CPI observations from the Federal Reserve Economic Data (FRED)
-- API for major food categories. Used to contextualize shrinkflation claims with
-- macro price trends.
--
-- Data source: https://fred.stlouisfed.org
-- No API key required — uses public CSV endpoint.

CREATE TABLE IF NOT EXISTS fred_cpi_data (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    series_id         TEXT        NOT NULL,
    series_name       TEXT        NOT NULL,
    category          TEXT,                           -- food category slug
    observation_date  DATE        NOT NULL,
    value             NUMERIC,                        -- CPI index value (null = "." in FRED)
    source_url        TEXT,                           -- canonical FRED series URL
    captured_at       TIMESTAMPTZ NOT NULL DEFAULT now(),

    UNIQUE (series_id, observation_date)
);

-- Fast range queries per series
CREATE INDEX IF NOT EXISTS idx_fred_cpi_series_date
    ON fred_cpi_data (series_id, observation_date DESC);

-- Filter/group by food category
CREATE INDEX IF NOT EXISTS idx_fred_cpi_category_date
    ON fred_cpi_data (category, observation_date DESC)
    WHERE category IS NOT NULL;

-- ── Row Level Security ────────────────────────────────────────────────────────

ALTER TABLE fred_cpi_data ENABLE ROW LEVEL SECURITY;

-- Anyone can read CPI data (public information)
CREATE POLICY "Public read fred_cpi_data"
    ON fred_cpi_data FOR SELECT
    USING (true);

-- Only the service role (pipeline) can write
CREATE POLICY "Service role write fred_cpi_data"
    ON fred_cpi_data FOR ALL
    USING (auth.role() = 'service_role');

-- ── Comment ───────────────────────────────────────────────────────────────────

COMMENT ON TABLE fred_cpi_data IS
    'Monthly CPI index values from FRED (Federal Reserve Economic Data) for food categories. '
    'Updated monthly after BLS releases. Used to show macro price trends alongside product-level '
    'shrinkflation claims.';
