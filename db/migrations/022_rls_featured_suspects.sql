-- FullCarts: RLS policies for featured_articles and suspects tables
-- Run AFTER 020 and 021

-- ============================================================
-- FEATURED ARTICLES
-- ============================================================

ALTER TABLE featured_articles ENABLE ROW LEVEL SECURITY;

-- Public reads featured articles only
CREATE POLICY "Public reads featured articles"
    ON featured_articles FOR SELECT
    USING (status = 'featured');

-- Reviewers and admins can read all articles
CREATE POLICY "Reviewers read all articles"
    ON featured_articles FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

-- Service role manages featured articles
CREATE POLICY "Service role manages featured articles"
    ON featured_articles FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');


-- ============================================================
-- SUSPECTS
-- ============================================================

ALTER TABLE suspects ENABLE ROW LEVEL SECURITY;

-- Public reads published suspects only
CREATE POLICY "Public reads published suspects"
    ON suspects FOR SELECT
    USING (status = 'published');

-- Reviewers and admins can read all suspects
CREATE POLICY "Reviewers read all suspects"
    ON suspects FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND public.user_role() IN ('reviewer', 'admin')
        )
    );

-- Service role manages suspects
CREATE POLICY "Service role manages suspects"
    ON suspects FOR ALL
    USING (auth.role() = 'service_role')
    WITH CHECK (auth.role() = 'service_role');
