-- FullCarts Rebuild: Foundation Migration
-- Phase 0 — creates all tables, indexes, views
-- Run in Supabase SQL Editor in order (dependencies respected)

-- ============================================================
-- 1. INDEPENDENT TABLES (no foreign keys)
-- ============================================================

-- Evidence files — stored in Supabase Storage
CREATE TABLE evidence_files (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    storage_path    TEXT NOT NULL,
    file_type       TEXT NOT NULL
        CHECK (file_type IN ('image', 'screenshot', 'receipt', 'document')),
    mime_type       TEXT NOT NULL,
    file_hash       TEXT NOT NULL,
    file_size_bytes INTEGER NOT NULL,
    caption         TEXT,
    uploaded_by     TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Raw items — immutable evidence locker
CREATE TABLE raw_items (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_type     TEXT NOT NULL
        CHECK (source_type IN (
            'reddit', 'news', 'openfoodfacts', 'kroger_api',
            'usda', 'community_tip', 'receipt', 'gdelt'
        )),
    source_id       TEXT NOT NULL,
    source_url      TEXT,
    captured_at     TIMESTAMPTZ DEFAULT now() NOT NULL,
    source_date     TIMESTAMPTZ,
    raw_payload     JSONB NOT NULL,
    content_hash    TEXT NOT NULL,
    scraper_version TEXT NOT NULL,

    UNIQUE (source_type, source_id)
);

CREATE INDEX idx_raw_items_source_type ON raw_items (source_type);
CREATE INDEX idx_raw_items_captured_at ON raw_items (captured_at);
CREATE INDEX idx_raw_items_content_hash ON raw_items (content_hash);

-- Product entities — canonical products
CREATE TABLE product_entities (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    canonical_name  TEXT NOT NULL,
    brand           TEXT NOT NULL,
    category        TEXT,
    manufacturer    TEXT,
    image_url       TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL,

    name_tokens     TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', canonical_name || ' ' || brand)
    ) STORED
);

CREATE INDEX idx_entities_brand ON product_entities (lower(brand));
CREATE INDEX idx_entities_name_search ON product_entities USING GIN (name_tokens);

-- Scraper state — cursor management
CREATE TABLE scraper_state (
    scraper_name    TEXT PRIMARY KEY,
    last_cursor     JSONB NOT NULL DEFAULT '{}',
    last_run_at     TIMESTAMPTZ,
    last_run_status TEXT
        CHECK (last_run_status IN ('success', 'partial', 'failed')),
    items_processed INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT now()
);

-- API usage tracking — monetization prep
CREATE TABLE api_usage (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    api_key_id      UUID,
    endpoint        TEXT NOT NULL,
    method          TEXT NOT NULL,
    status_code     INTEGER NOT NULL,
    response_time_ms INTEGER,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_api_usage_endpoint ON api_usage (endpoint, created_at);


-- ============================================================
-- 2. TABLES WITH SINGLE DEPENDENCIES
-- ============================================================

-- Pack variants — specific SKUs for a product entity
CREATE TABLE pack_variants (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       UUID NOT NULL REFERENCES product_entities(id),
    upc             TEXT UNIQUE,
    variant_name    TEXT NOT NULL,
    current_size    NUMERIC,
    size_unit       TEXT,
    item_count      INTEGER,
    is_active       BOOLEAN DEFAULT true,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_variants_entity ON pack_variants (entity_id);
CREATE INDEX idx_variants_upc ON pack_variants (upc) WHERE upc IS NOT NULL;


-- ============================================================
-- 3. TABLES WITH MULTIPLE DEPENDENCIES
-- ============================================================

-- Variant observations — time-series snapshots
CREATE TABLE variant_observations (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    variant_id      UUID NOT NULL REFERENCES pack_variants(id),
    observed_date   DATE NOT NULL,
    source_type     TEXT NOT NULL,
    source_ref      TEXT,

    size            NUMERIC,
    size_unit       TEXT,
    price           NUMERIC,
    price_per_unit  NUMERIC GENERATED ALWAYS AS (
        CASE WHEN size > 0 THEN price / size ELSE NULL END
    ) STORED,
    retailer        TEXT,
    store_location  TEXT,

    evidence_url    TEXT,
    evidence_file_id UUID REFERENCES evidence_files(id),
    raw_item_id     UUID REFERENCES raw_items(id),

    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX idx_observations_unique
    ON variant_observations (variant_id, observed_date, source_type, COALESCE(retailer, ''));
CREATE INDEX idx_observations_variant ON variant_observations (variant_id);
CREATE INDEX idx_observations_date ON variant_observations (observed_date);

-- Claims — AI-extracted structured assertions
CREATE TABLE claims (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    raw_item_id         UUID NOT NULL REFERENCES raw_items(id),
    extractor_version   TEXT NOT NULL,
    extracted_at        TIMESTAMPTZ DEFAULT now() NOT NULL,

    brand               TEXT,
    product_name        TEXT,
    category            TEXT,
    old_size            NUMERIC,
    old_size_unit       TEXT,
    new_size            NUMERIC,
    new_size_unit       TEXT,
    old_price           NUMERIC,
    new_price           NUMERIC,
    retailer            TEXT,
    upc                 TEXT,
    observed_date       DATE,
    change_description  TEXT,

    confidence          JSONB NOT NULL DEFAULT '{}',

    status              TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'matched', 'unmatched', 'discarded')),

    matched_entity_id   UUID REFERENCES product_entities(id),
    matched_variant_id  UUID REFERENCES pack_variants(id),

    UNIQUE (raw_item_id, extractor_version)
);

CREATE INDEX idx_claims_raw_item ON claims (raw_item_id);
CREATE INDEX idx_claims_status ON claims (status);
CREATE INDEX idx_claims_brand ON claims (lower(brand));
CREATE INDEX idx_claims_upc ON claims (upc) WHERE upc IS NOT NULL;

-- Change candidates — detected changes pending review
CREATE TABLE change_candidates (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    variant_id          UUID NOT NULL REFERENCES pack_variants(id),
    observation_before  UUID NOT NULL REFERENCES variant_observations(id),
    observation_after   UUID NOT NULL REFERENCES variant_observations(id),

    size_before         NUMERIC NOT NULL,
    size_after          NUMERIC NOT NULL,
    size_delta_pct      NUMERIC NOT NULL,
    price_before        NUMERIC,
    price_after         NUMERIC,
    ppu_delta_pct       NUMERIC,

    change_type         TEXT NOT NULL
        CHECK (change_type IN (
            'shrinkflation', 'downsizing', 'upsizing',
            'price_hike', 'restoration'
        )),
    severity            TEXT NOT NULL
        CHECK (severity IN ('minor', 'moderate', 'major')),
    is_shrinkflation    BOOLEAN NOT NULL,

    status              TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'approved', 'rejected', 'false_positive')),
    reviewed_by         UUID REFERENCES auth.users(id),
    reviewed_at         TIMESTAMPTZ,
    review_notes        TEXT,

    supporting_claims   UUID[] DEFAULT '{}',
    evidence_count      INTEGER DEFAULT 0,

    created_at          TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (observation_before, observation_after)
);

CREATE INDEX idx_candidates_variant ON change_candidates (variant_id);
CREATE INDEX idx_candidates_status ON change_candidates (status);
CREATE INDEX idx_candidates_created ON change_candidates (created_at);

-- Published changes — the public record
CREATE TABLE published_changes (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID NOT NULL REFERENCES change_candidates(id) UNIQUE,
    variant_id          UUID NOT NULL REFERENCES pack_variants(id),
    entity_id           UUID NOT NULL REFERENCES product_entities(id),

    brand               TEXT NOT NULL,
    product_name        TEXT NOT NULL,
    size_before         NUMERIC NOT NULL,
    size_after          NUMERIC NOT NULL,
    size_unit           TEXT NOT NULL,
    size_delta_pct      NUMERIC NOT NULL,
    change_type         TEXT NOT NULL,
    severity            TEXT NOT NULL,
    observed_date       DATE NOT NULL,

    evidence_summary    JSONB NOT NULL DEFAULT '[]',

    is_retracted        BOOLEAN DEFAULT false,
    retracted_at        TIMESTAMPTZ,
    retracted_by        UUID REFERENCES auth.users(id),
    retraction_reason   TEXT,

    upvote_count        INTEGER DEFAULT 0,

    published_at        TIMESTAMPTZ DEFAULT now() NOT NULL,
    published_by        UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_published_entity ON published_changes (entity_id);
CREATE INDEX idx_published_brand ON published_changes (lower(brand));
CREATE INDEX idx_published_date ON published_changes (published_at);
CREATE INDEX idx_published_severity ON published_changes (severity);
CREATE INDEX idx_published_type ON published_changes (change_type);

-- Review actions — complete audit trail
CREATE TABLE review_actions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    target_type     TEXT NOT NULL
        CHECK (target_type IN (
            'claim', 'change_candidate', 'published_change', 'tip'
        )),
    target_id       UUID NOT NULL,
    action          TEXT NOT NULL
        CHECK (action IN (
            'approve', 'reject', 'edit', 'retract', 'escalate', 'reassign'
        )),
    reviewer_id     UUID NOT NULL REFERENCES auth.users(id),
    previous_state  JSONB,
    new_state       JSONB,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_review_actions_target ON review_actions (target_type, target_id);
CREATE INDEX idx_review_actions_reviewer ON review_actions (reviewer_id);
CREATE INDEX idx_review_actions_created ON review_actions (created_at);

-- Tips — community submissions
CREATE TABLE tips (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id      TEXT NOT NULL,
    brand           TEXT,
    product_name    TEXT,
    description     TEXT NOT NULL,
    evidence_url    TEXT,
    evidence_file_id UUID REFERENCES evidence_files(id),
    status          TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'converted', 'dismissed')),
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    ip_hash         TEXT
);


-- ============================================================
-- 4. VIEWS
-- ============================================================

-- Product timeline: full history for one product
CREATE VIEW product_timeline AS
SELECT
    pe.id AS entity_id,
    pe.canonical_name,
    pe.brand,
    pv.id AS variant_id,
    pv.variant_name,
    pv.upc,
    vo.observed_date,
    vo.size,
    vo.size_unit,
    vo.price,
    vo.price_per_unit,
    vo.source_type,
    vo.retailer
FROM product_entities pe
JOIN pack_variants pv ON pv.entity_id = pe.id
JOIN variant_observations vo ON vo.variant_id = pv.id
ORDER BY pe.id, pv.id, vo.observed_date;

-- Leaderboard: worst offenders by cumulative shrinkage
CREATE VIEW shrinkflation_leaderboard AS
SELECT
    pe.id AS entity_id,
    pe.canonical_name,
    pe.brand,
    COUNT(pc.id) AS shrinkflation_count,
    SUM(pc.size_delta_pct) AS total_shrinkage_pct,
    MIN(pc.observed_date) AS first_detected,
    MAX(pc.observed_date) AS last_detected
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE pc.is_retracted = false
  AND pc.change_type = 'shrinkflation'
GROUP BY pe.id, pe.canonical_name, pe.brand
ORDER BY total_shrinkage_pct ASC;

-- Brand scorecard: primary UI view
CREATE VIEW brand_scorecard AS
SELECT
    pe.brand,
    COUNT(DISTINCT pe.id) AS product_count,
    COUNT(pc.id) AS total_events,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrinkflation_events,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'restoration') AS restoration_events,
    SUM(pc.size_delta_pct) FILTER (WHERE pc.change_type = 'shrinkflation') AS total_shrinkage_pct,
    MIN(pc.observed_date) AS first_detected,
    MAX(pc.observed_date) AS last_detected
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE pc.is_retracted = false
GROUP BY pe.brand
ORDER BY shrinkflation_events DESC;

-- Restorations: brands that reversed shrinkflation
CREATE VIEW restorations AS
SELECT
    pc.id,
    pc.brand,
    pc.product_name,
    pc.size_before,
    pc.size_after,
    pc.size_unit,
    pc.observed_date,
    pc.evidence_summary,
    pc.published_at
FROM published_changes pc
WHERE pc.change_type = 'restoration'
  AND pc.is_retracted = false
ORDER BY pc.published_at DESC;

-- Dashboard stats
CREATE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM product_entities) AS total_products,
    (SELECT COUNT(*) FROM published_changes WHERE NOT is_retracted) AS total_changes,
    (SELECT COUNT(*) FROM published_changes
     WHERE NOT is_retracted AND change_type = 'shrinkflation') AS shrinkflation_events,
    (SELECT COUNT(*) FROM change_candidates WHERE status = 'pending') AS pending_review,
    (SELECT COUNT(*) FROM claims WHERE status = 'pending') AS pending_claims,
    (SELECT COUNT(*) FROM raw_items
     WHERE captured_at > now() - INTERVAL '7 days') AS items_ingested_7d;
