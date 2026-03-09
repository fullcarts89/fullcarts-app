-- FullCarts Rebuild: Row-Level Security Policies
-- Run AFTER 001_foundation.sql

-- ============================================================
-- HELPER: user_role() function for JWT-based role checks
-- ============================================================

CREATE OR REPLACE FUNCTION public.user_role()
RETURNS TEXT AS $$
  SELECT COALESCE(
    current_setting('request.jwt.claims', true)::json->>'user_role',
    'public'
  );
$$ LANGUAGE sql STABLE;


-- ============================================================
-- PUBLIC-READABLE TABLES
-- ============================================================

-- product_entities: public read, service_role write
ALTER TABLE product_entities ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read products"
    ON product_entities FOR SELECT
    USING (true);

CREATE POLICY "Service role manages products"
    ON product_entities FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- pack_variants: public read, service_role write
ALTER TABLE pack_variants ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read variants"
    ON pack_variants FOR SELECT
    USING (true);

CREATE POLICY "Service role manages variants"
    ON pack_variants FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- variant_observations: public read, service_role write
ALTER TABLE variant_observations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read observations"
    ON variant_observations FOR SELECT
    USING (true);

CREATE POLICY "Service role manages observations"
    ON variant_observations FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- published_changes: public read (non-retracted), service_role write
ALTER TABLE published_changes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public reads non-retracted changes"
    ON published_changes FOR SELECT
    USING (NOT is_retracted);

CREATE POLICY "Service role manages published changes"
    ON published_changes FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- evidence_files: public read, service_role write
ALTER TABLE evidence_files ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read evidence files"
    ON evidence_files FOR SELECT
    USING (true);

CREATE POLICY "Service role manages evidence files"
    ON evidence_files FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ============================================================
-- REVIEWER-ONLY TABLES
-- ============================================================

-- raw_items: reviewers+ can read, service_role writes
ALTER TABLE raw_items ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Reviewers and admins can read raw items"
    ON raw_items FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

CREATE POLICY "Service role manages raw items"
    ON raw_items FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- claims: reviewers+ can read, service_role writes
ALTER TABLE claims ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Reviewers and admins can read claims"
    ON claims FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

CREATE POLICY "Service role manages claims"
    ON claims FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- change_candidates: reviewers+ can read, service_role writes
ALTER TABLE change_candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Reviewers and admins can read candidates"
    ON change_candidates FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

CREATE POLICY "Service role manages candidates"
    ON change_candidates FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- review_actions: admins can read, service_role writes
ALTER TABLE review_actions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can read audit log"
    ON review_actions FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() = 'admin'
        )
    );

CREATE POLICY "Service role manages review actions"
    ON review_actions FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ============================================================
-- COMMUNITY TABLES
-- ============================================================

-- tips: anyone can insert, reviewers+ can read all, service_role manages
ALTER TABLE tips ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can submit tips"
    ON tips FOR INSERT
    WITH CHECK (true);

CREATE POLICY "Reviewers can read all tips"
    ON tips FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

CREATE POLICY "Service role manages tips"
    ON tips FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ============================================================
-- INTERNAL TABLES
-- ============================================================

-- scraper_state: service_role only
ALTER TABLE scraper_state ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role manages scraper state"
    ON scraper_state FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Admins can read scraper state"
    ON scraper_state FOR SELECT
    USING (
        auth.role() = 'authenticated'
        AND public.user_role() = 'admin'
    );


-- api_usage: service_role writes, admins read
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Service role manages api usage"
    ON api_usage FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Admins can read api usage"
    ON api_usage FOR SELECT
    USING (
        auth.role() = 'authenticated'
        AND public.user_role() = 'admin'
    );


-- ============================================================
-- STORAGE BUCKET for evidence
-- ============================================================

-- Create the evidence bucket (run separately if needed)
-- INSERT INTO storage.buckets (id, name, public) VALUES ('evidence', 'evidence', true);

-- Storage policies
-- CREATE POLICY "Public can read evidence" ON storage.objects
--     FOR SELECT USING (bucket_id = 'evidence');
-- CREATE POLICY "Service role uploads evidence" ON storage.objects
--     FOR INSERT WITH CHECK (bucket_id = 'evidence' AND auth.role() = 'service_role');
