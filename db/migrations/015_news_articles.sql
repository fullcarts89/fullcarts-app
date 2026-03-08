-- ============================================================
-- Migration 015: News articles table, article-product linking,
--                and updated views for news feed + evidence citations
-- ============================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════
-- 1. NEWS_ARTICLES: proper home for scraped news articles
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS news_articles (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  url              text UNIQUE NOT NULL,           -- Canonical article URL
  title            text NOT NULL,
  outlet           text,                           -- Publisher name (CNN, BBC, etc.)
  author           text,
  published_at     timestamptz,                    -- Article publication date
  summary          text,                           -- Short description / lede
  article_type     text DEFAULT 'shrinkflation',   -- shrinkflation, skimpflation, downsizing, count-cut, price-hike, general
  tags             text[],                         -- Free-form tags (Policy, Consumer, Investigation, etc.)

  -- Provenance: how did we find this article?
  staging_id       uuid,                           -- FK to reddit_staging row it was promoted from (nullable)
  source_query     text,                           -- Google News query that surfaced it

  -- Extraction metadata
  products_extracted integer DEFAULT 0,            -- How many products were extracted from this article
  status           text DEFAULT 'active',          -- active, hidden, retracted

  created_at       timestamptz DEFAULT now(),
  updated_at       timestamptz DEFAULT now()
);

COMMENT ON TABLE news_articles IS
  'Stores news articles that cover shrinkflation. Populated when google_news staging entries are approved.';

-- Index for feed queries
CREATE INDEX IF NOT EXISTS idx_news_articles_published
  ON news_articles (published_at DESC NULLS LAST);

CREATE INDEX IF NOT EXISTS idx_news_articles_outlet
  ON news_articles (outlet);


-- ═══════════════════════════════════════════════════════════════
-- 2. ARTICLE_PRODUCT_LINKS: join table linking articles to products
--    This powers "cited by" on product cards and "products mentioned"
--    on article cards.
-- ═══════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS article_product_links (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  article_id       uuid NOT NULL REFERENCES news_articles(id) ON DELETE CASCADE,
  product_upc      text NOT NULL REFERENCES products(upc) ON DELETE CASCADE,
  context          text,                           -- Snippet or note about the mention
  created_at       timestamptz DEFAULT now(),
  UNIQUE(article_id, product_upc)
);

COMMENT ON TABLE article_product_links IS
  'Many-to-many join: which news articles mention which products. Powers evidence citations.';

CREATE INDEX IF NOT EXISTS idx_article_product_links_product
  ON article_product_links (product_upc);

CREATE INDEX IF NOT EXISTS idx_article_product_links_article
  ON article_product_links (article_id);


-- ═══════════════════════════════════════════════════════════════
-- 3. ADD source_type COLUMN TO reddit_staging
--    Distinguishes reddit posts from news articles in the staging queue
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS source_type text DEFAULT 'reddit';

COMMENT ON COLUMN reddit_staging.source_type IS
  'Origin type: reddit, news, community, openfoodfacts. Used to route approved entries to the correct table.';


-- ═══════════════════════════════════════════════════════════════
-- 4. VIEW: news_feed — powers the public news tab
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE VIEW news_feed AS
SELECT
  na.id,
  na.url,
  na.title,
  na.outlet,
  na.published_at,
  na.summary,
  na.article_type,
  na.tags,
  na.products_extracted,
  na.status,
  na.created_at,
  -- Count of linked products
  (SELECT count(*) FROM article_product_links apl WHERE apl.article_id = na.id)
    AS linked_products_count
FROM news_articles na
WHERE na.status = 'active'
ORDER BY na.published_at DESC NULLS LAST, na.created_at DESC;


-- ═══════════════════════════════════════════════════════════════
-- 5. VIEW: product_news — articles citing a specific product
--    Used on product detail cards for evidence citations.
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE VIEW product_news AS
SELECT
  apl.product_upc,
  na.id         AS article_id,
  na.url        AS article_url,
  na.title      AS article_title,
  na.outlet,
  na.published_at,
  na.summary    AS article_summary,
  na.article_type,
  apl.context   AS mention_context,
  apl.created_at AS linked_at
FROM article_product_links apl
JOIN news_articles na ON na.id = apl.article_id
WHERE na.status = 'active'
ORDER BY na.published_at DESC NULLS LAST;


-- ═══════════════════════════════════════════════════════════════
-- 6. RLS POLICIES
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE news_articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE article_product_links ENABLE ROW LEVEL SECURITY;

-- News articles: public read, service role manages
CREATE POLICY "Public read news_articles"
  ON news_articles FOR SELECT USING (true);
CREATE POLICY "Service role manages news_articles"
  ON news_articles FOR ALL USING (auth.role() = 'service_role');
-- Allow anon inserts so the frontend admin can link articles
CREATE POLICY "Anon can insert news_articles"
  ON news_articles FOR INSERT WITH CHECK (true);

-- Article-product links: public read, anyone can insert (admin links from frontend)
CREATE POLICY "Public read article_product_links"
  ON article_product_links FOR SELECT USING (true);
CREATE POLICY "Anon can insert article_product_links"
  ON article_product_links FOR INSERT WITH CHECK (true);


-- ═══════════════════════════════════════════════════════════════
-- 7. UPDATED dashboard_stats with news article counts
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql STABLE AS $$
BEGIN
  RETURN jsonb_build_object(
    'total_products',       (SELECT count(*) FROM products),
    'total_versions',       (SELECT count(*) FROM product_versions),
    'total_changes',        (SELECT count(*) FROM change_events),
    'shrinkflation_events', (SELECT count(*) FROM change_events WHERE is_shrinkflation AND NOT false_positive),
    'categories_tracked',   (SELECT count(DISTINCT category) FROM products WHERE category IS NOT NULL),
    'avg_shrink_pct',       (SELECT round(avg(abs(size_delta_pct)), 1) FROM change_events WHERE size_delta_pct < 0 AND NOT false_positive),
    'worst_shrink_pct',     (SELECT round(min(size_delta_pct), 1) FROM change_events WHERE NOT false_positive),
    'pending_review',       (SELECT count(*) FROM reddit_staging WHERE status = 'pending' AND tier IN ('auto', 'review')),
    'total_staged',         (SELECT count(*) FROM reddit_staging),
    'staged_promoted',      (SELECT count(*) FROM reddit_staging WHERE status = 'promoted'),
    'staged_dismissed',     (SELECT count(*) FROM reddit_staging WHERE status = 'dismissed'),
    'staged_rejected',      (SELECT count(*) FROM reddit_staging WHERE status = 'rejected'),
    'staged_evidence_wall', (SELECT count(*) FROM reddit_staging WHERE status = 'evidence_wall'),
    'evidence_wall_count',  (SELECT count(*) FROM evidence_wall WHERE status = 'approved'),
    'total_signals',        (SELECT count(*) FROM signals_summary WHERE confidence = 'confirmed' OR confidence = 'suspicious'),
    'confirmed_signals',    (SELECT count(*) FROM signals_summary WHERE confidence = 'confirmed'),
    'suspicious_signals',   (SELECT count(*) FROM signals_summary WHERE confidence = 'suspicious'),
    'brands_tracked',       (SELECT count(DISTINCT brand) FROM signals_summary WHERE brand IS NOT NULL),
    'false_positives',      (SELECT count(*) FROM change_events WHERE false_positive),
    'avg_confidence',       (SELECT round(avg(confidence_score), 0) FROM reddit_staging WHERE status = 'promoted'),
    -- New: news article stats
    'news_articles_count',  (SELECT count(*) FROM news_articles WHERE status = 'active'),
    'news_linked_products', (SELECT count(DISTINCT product_upc) FROM article_product_links)
  );
END;
$$;


-- ═══════════════════════════════════════════════════════════════
-- 8. UPDATE get_product_history to include news citations
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION get_product_history(p_upc text)
RETURNS jsonb
LANGUAGE plpgsql STABLE AS $$
DECLARE
  result jsonb;
BEGIN
  SELECT jsonb_build_object(
    'product', (
      SELECT to_jsonb(p.*) FROM products p WHERE p.upc = p_upc
    ),
    'versions', (
      SELECT coalesce(jsonb_agg(to_jsonb(pv.*) ORDER BY pv.observed_date ASC), '[]'::jsonb)
      FROM product_versions pv WHERE pv.product_upc = p_upc
    ),
    'changes', (
      SELECT coalesce(jsonb_agg(to_jsonb(ce.*) ORDER BY ce.detected_date ASC), '[]'::jsonb)
      FROM change_events ce WHERE ce.product_upc = p_upc
    ),
    'upvotes', (
      SELECT count(*) FROM upvotes u WHERE u.upc = p_upc
    ),
    'news_citations', (
      SELECT coalesce(jsonb_agg(
        jsonb_build_object(
          'article_id', na.id,
          'url', na.url,
          'title', na.title,
          'outlet', na.outlet,
          'published_at', na.published_at,
          'article_type', na.article_type,
          'context', apl.context
        ) ORDER BY na.published_at DESC
      ), '[]'::jsonb)
      FROM article_product_links apl
      JOIN news_articles na ON na.id = apl.article_id
      WHERE apl.product_upc = p_upc AND na.status = 'active'
    )
  ) INTO result;

  RETURN result;
END;
$$;

COMMIT;
