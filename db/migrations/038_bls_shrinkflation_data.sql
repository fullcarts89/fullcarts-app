-- BLS R-CPI-SC (Research CPI excluding product size changes) data.
--
-- Stores downsizing/upsizing frequency counts and CPI index values from two
-- quarterly BLS Excel files:
--   - r-cpi-sc-counts.xlsx  — count of items that changed size, by food category
--   - r-cpi-sc-data.xlsx    — official CPI and R-CPI-SC indexes, by food category
--
-- Data updated quarterly (January, April, July, October).

CREATE TABLE IF NOT EXISTS bls_shrinkflation (
    id                BIGSERIAL PRIMARY KEY,
    series            TEXT        NOT NULL,     -- BLS food category/strata label
    period            DATE        NOT NULL,     -- First day of the month (e.g. 2015-01-01)
    downsizing_count  INTEGER,                  -- # items that decreased in size (counts file)
    upsizing_count    INTEGER,                  -- # items that increased in size (counts file)
    official_cpi      NUMERIC(10, 3),           -- Standard CPI index value (data file)
    rcpi_sc           NUMERIC(10, 3),           -- R-CPI-SC: CPI adjusted to remove size changes
    counts_url        TEXT,                     -- Source URL for counts file
    data_url          TEXT,                     -- Source URL for data file
    downloaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (series, period)
);

-- Enable RLS
ALTER TABLE bls_shrinkflation ENABLE ROW LEVEL SECURITY;

-- Public read
CREATE POLICY "public_read_bls_shrinkflation"
    ON bls_shrinkflation FOR SELECT
    TO anon
    USING (true);

-- Service role write
CREATE POLICY "service_write_bls_shrinkflation"
    ON bls_shrinkflation FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_bls_shrinkflation_period
    ON bls_shrinkflation (period DESC);

CREATE INDEX IF NOT EXISTS idx_bls_shrinkflation_series
    ON bls_shrinkflation (series);
