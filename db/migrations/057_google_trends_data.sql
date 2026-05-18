-- Migration 057: google_trends_data table
--
-- Adds a fourth line to the /insights macro chart: Google search
-- interest for "shrinkflation" over time. Trends scores are normalised
-- 0-100 within the requested window, so we always store the full
-- series — re-runs overwrite the whole table rather than appending.
--
-- The actual fetch lives in `pipeline/scrapers/google_trends.py` and
-- runs monthly via `pipeline_google_trends.yml`.

CREATE TABLE IF NOT EXISTS google_trends_data (
    id                  BIGSERIAL PRIMARY KEY,
    -- Search keyword we're tracking. Same row shape supports multiple
    -- keywords if we expand the chart later (e.g. "skimpflation").
    keyword             TEXT NOT NULL,
    -- ISO month-start date (the Trends JSON ships month buckets).
    observation_date    DATE NOT NULL,
    -- Normalised 0-100 interest score for this month relative to the
    -- max value in the fetched window. Float (not int) so future
    -- daily/weekly buckets fit too.
    value               NUMERIC NOT NULL,
    -- Geographic scope ('' = worldwide, 'US' = United States, etc.)
    geo                 TEXT NOT NULL DEFAULT '',
    -- The window the scrape was made against. Trends normalises within
    -- this — kept for transparency, not for joins.
    timeframe           TEXT NOT NULL DEFAULT 'all',
    fetched_at          TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uq_google_trends_obs UNIQUE (keyword, geo, observation_date)
);

CREATE INDEX IF NOT EXISTS idx_google_trends_keyword
    ON google_trends_data (keyword, observation_date);

ALTER TABLE google_trends_data ENABLE ROW LEVEL SECURITY;

-- Public read (it's macro context, not personal data).
DROP POLICY IF EXISTS "Public read google_trends_data" ON google_trends_data;
CREATE POLICY "Public read google_trends_data"
    ON google_trends_data FOR SELECT
    USING (true);

-- Service role writes.
DROP POLICY IF EXISTS "Service role writes google_trends_data" ON google_trends_data;
CREATE POLICY "Service role writes google_trends_data"
    ON google_trends_data FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

COMMENT ON TABLE google_trends_data IS
    'Monthly search interest for shrinkflation-related terms. Powers '
    'the fourth line on the /insights chart. Refreshed monthly via '
    'pipeline_google_trends workflow. Added by migration 057.';
