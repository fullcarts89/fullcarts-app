-- ============================================================
-- Migration 010: Enrich evidence_wall as a signals table +
--                unified signals_summary view
-- ============================================================

BEGIN;

-- ── Add signal_type to evidence_wall ─────────────────────────
-- Classifies the type of suspicious behavior observed.
-- The existing 'tag' column stays for visual/display categorization;
-- signal_type is for analytical aggregation.
ALTER TABLE evidence_wall
  ADD COLUMN IF NOT EXISTS signal_type text DEFAULT 'unverified_size_change';

COMMENT ON COLUMN evidence_wall.signal_type IS
  'Analytical signal type: stealth_redesign, ppu_increase, ingredient_swap, count_reduction, regional_test, unverified_size_change';

-- ── Add severity to evidence_wall ────────────────────────────
-- 1 = low (minor / ambiguous), 2 = medium (credible), 3 = high (egregious)
ALTER TABLE evidence_wall
  ADD COLUMN IF NOT EXISTS severity integer DEFAULT 2
  CHECK (severity BETWEEN 1 AND 3);

-- ── Unified signals_summary view ─────────────────────────────
-- Combines confirmed shrinkflation events (from change_events) with
-- suspicious behavior signals (from evidence_wall) into one queryable
-- dataset for dashboards and visualizations.
CREATE OR REPLACE VIEW signals_summary AS

-- Confirmed signals from change_events
SELECT
  'confirmed'::text           AS confidence,
  ce.product_upc              AS upc,
  p.name                      AS product_name,
  p.brand,
  p.category,
  ce.change_type              AS signal_type,
  ce.severity,
  ce.detected_date            AS date_spotted,
  ce.size_delta_pct,
  ce.price_per_unit_delta_pct,
  NULL::text                  AS image_url,
  NULL::text                  AS tag,
  NULL::text                  AS source_url,
  ce.created_at
FROM change_events ce
JOIN products p ON p.upc = ce.product_upc
WHERE ce.is_shrinkflation = true

UNION ALL

-- Suspicious signals from evidence_wall
SELECT
  'suspicious'::text          AS confidence,
  NULL::text                  AS upc,
  ew.product_name,
  ew.brand,
  ew.category,
  ew.signal_type,
  ew.severity,
  ew.date_spotted,
  NULL::numeric               AS size_delta_pct,
  NULL::numeric               AS price_per_unit_delta_pct,
  ew.image_url,
  ew.tag,
  ew.source_url,
  ew.created_at
FROM evidence_wall ew
WHERE ew.status = 'approved'

ORDER BY date_spotted DESC NULLS LAST, created_at DESC;


-- ── Aggregate view: brand_signal_counts ──────────────────────
-- Powers the brand heat map on the leaderboard/shame screen.
CREATE OR REPLACE VIEW brand_signal_counts AS
SELECT
  brand,
  count(*)                                          AS total_signals,
  count(*) FILTER (WHERE confidence = 'confirmed')  AS confirmed_count,
  count(*) FILTER (WHERE confidence = 'suspicious') AS suspicious_count,
  count(DISTINCT signal_type)                       AS tactic_diversity,
  max(date_spotted)                                 AS latest_signal,
  min(date_spotted)                                 AS earliest_signal
FROM signals_summary
WHERE brand IS NOT NULL
GROUP BY brand
ORDER BY total_signals DESC;


-- ── Aggregate view: signal_type_counts ───────────────────────
-- Powers the tactics breakdown chart.
CREATE OR REPLACE VIEW signal_type_counts AS
SELECT
  signal_type,
  count(*)                                          AS total,
  count(*) FILTER (WHERE confidence = 'confirmed')  AS confirmed,
  count(*) FILTER (WHERE confidence = 'suspicious') AS suspicious
FROM signals_summary
WHERE signal_type IS NOT NULL
GROUP BY signal_type
ORDER BY total DESC;


-- ── Aggregate view: monthly_signal_counts ────────────────────
-- Powers the trends-over-time chart.
CREATE OR REPLACE VIEW monthly_signal_counts AS
SELECT
  date_trunc('month', COALESCE(date_spotted, created_at::date))::date AS month,
  count(*)                                          AS total,
  count(*) FILTER (WHERE confidence = 'confirmed')  AS confirmed,
  count(*) FILTER (WHERE confidence = 'suspicious') AS suspicious
FROM signals_summary
GROUP BY 1
ORDER BY 1;


-- ── Updated dashboard_stats function ─────────────────────────
-- Now includes staging pipeline counts and evidence wall counts
-- so the frontend can show real collection metrics.
CREATE OR REPLACE FUNCTION dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql STABLE AS $$
BEGIN
  RETURN jsonb_build_object(
    'total_products',       (SELECT count(*) FROM products),
    'total_versions',       (SELECT count(*) FROM product_versions),
    'total_changes',        (SELECT count(*) FROM change_events),
    'shrinkflation_events', (SELECT count(*) FROM change_events WHERE is_shrinkflation),
    'categories_tracked',   (SELECT count(DISTINCT category) FROM products WHERE category IS NOT NULL),
    'avg_shrink_pct',       (SELECT round(avg(abs(size_delta_pct)), 1) FROM change_events WHERE size_delta_pct < 0),
    'worst_shrink_pct',     (SELECT round(min(size_delta_pct), 1) FROM change_events),
    'pending_review',       (SELECT count(*) FROM reddit_staging WHERE status = 'pending' AND tier IN ('auto', 'review')),
    -- New: full pipeline stats
    'total_staged',         (SELECT count(*) FROM reddit_staging),
    'staged_promoted',      (SELECT count(*) FROM reddit_staging WHERE status = 'promoted'),
    'staged_dismissed',     (SELECT count(*) FROM reddit_staging WHERE status = 'dismissed'),
    'staged_rejected',      (SELECT count(*) FROM reddit_staging WHERE status = 'rejected'),
    'staged_evidence_wall', (SELECT count(*) FROM reddit_staging WHERE status = 'evidence_wall'),
    'evidence_wall_count',  (SELECT count(*) FROM evidence_wall WHERE status = 'approved'),
    'total_signals',        (SELECT count(*) FROM signals_summary),
    'confirmed_signals',    (SELECT count(*) FROM signals_summary WHERE confidence = 'confirmed'),
    'suspicious_signals',   (SELECT count(*) FROM signals_summary WHERE confidence = 'suspicious'),
    'brands_tracked',       (SELECT count(DISTINCT brand) FROM signals_summary WHERE brand IS NOT NULL)
  );
END;
$$;

COMMIT;
