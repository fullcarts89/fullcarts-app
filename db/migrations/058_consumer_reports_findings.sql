-- Migration 058: consumer_reports_findings table
--
-- Consumer Reports publishes an annual "Shrinkflation" round-up plus
-- occasional standalone investigations. This table stores each finding
-- as a structured row so we can cross-reference their named products
-- against our own catalog and surface a "Consumer Reports says X about
-- this product" badge on /products/[id] (and a co-citation rate on
-- /insights).
--
-- Source ingestion:
--   pipeline/scrapers/consumer_reports.py runs monthly (idempotent
--   upsert on source_url). It scrapes the public CR shrinkflation
--   index pages — no paywall content; we only store the public bits
--   anyone can read on consumerreports.org.

CREATE TABLE IF NOT EXISTS consumer_reports_findings (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- The CR article URL we extracted the finding from (unique).
    source_url          TEXT NOT NULL UNIQUE,
    -- Headline / publication date / author from the article.
    title               TEXT NOT NULL,
    published_at        DATE,
    -- Free-form excerpt — the sentence(s) referencing this product.
    excerpt             TEXT,
    -- Structured product reference. brand + product_name match our
    -- product_entities; UPC is optional.
    brand               TEXT,
    product_name        TEXT,
    upc                 TEXT,
    -- Detected size/recipe shift if CR reports one. Optional —
    -- some findings are qualitative.
    size_before         NUMERIC,
    size_after          NUMERIC,
    size_unit           TEXT,
    -- Resolved entity_id once a backfill matches the row to our catalog.
    -- Null until the matching script (run periodically) succeeds.
    entity_id           UUID REFERENCES product_entities(id),
    matched_at          TIMESTAMPTZ,
    -- Bookkeeping
    fetched_at          TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_cr_brand
    ON consumer_reports_findings (lower(brand))
    WHERE brand IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cr_entity
    ON consumer_reports_findings (entity_id)
    WHERE entity_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_cr_published
    ON consumer_reports_findings (published_at DESC);

ALTER TABLE consumer_reports_findings ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Public read consumer_reports_findings"
    ON consumer_reports_findings;
CREATE POLICY "Public read consumer_reports_findings"
    ON consumer_reports_findings FOR SELECT
    USING (true);

DROP POLICY IF EXISTS "Service role writes consumer_reports_findings"
    ON consumer_reports_findings;
CREATE POLICY "Service role writes consumer_reports_findings"
    ON consumer_reports_findings FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

COMMENT ON TABLE consumer_reports_findings IS
    'Structured Consumer Reports shrinkflation findings, scraped from '
    'CR''s public shrinkflation index pages. entity_id is null until '
    'the brand+product matcher resolves it to our catalog. Added by '
    'migration 058.';
