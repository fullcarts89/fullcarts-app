-- ============================================================
-- Migration 003: Views, convenience functions, and analytics
-- ============================================================

BEGIN;

-- ── View: product_timeline ────────────────────────────────
-- Full history of a product's size/price changes over time.
-- Used by the public-facing product history page.
CREATE OR REPLACE VIEW product_timeline AS
SELECT
  p.upc,
  p.name,
  p.brand,
  p.category,
  p.image_url,
  pv.id             AS version_id,
  pv.observed_date,
  pv.size,
  pv.unit,
  pv.price,
  pv.price_per_unit,
  pv.retailer,
  pv.source,
  pv.evidence_url,
  ce.id             AS change_event_id,
  ce.size_delta_pct,
  ce.price_per_unit_delta_pct,
  ce.change_type,
  ce.is_shrinkflation,
  ce.severity
FROM products p
JOIN product_versions pv ON pv.product_upc = p.upc
LEFT JOIN change_events ce ON ce.version_after_id = pv.id
ORDER BY p.upc, pv.observed_date ASC;


-- ── View: shrinkflation_leaderboard ───────────────────────
-- Products ranked by total shrinkage. Powers the "Worst Offenders" page.
CREATE OR REPLACE VIEW shrinkflation_leaderboard AS
SELECT
  p.upc,
  p.name,
  p.brand,
  p.category,
  p.image_url,
  p.repeat_offender,

  -- Aggregate stats
  count(ce.id)                                AS total_changes,
  count(ce.id) FILTER (WHERE ce.is_shrinkflation)  AS shrink_count,
  round(sum(ce.size_delta_pct) FILTER (WHERE ce.size_delta_pct < 0), 2)
                                              AS cumulative_shrink_pct,

  -- Latest version info
  (SELECT pv.size FROM product_versions pv
   WHERE pv.product_upc = p.upc ORDER BY pv.observed_date DESC LIMIT 1)
                                              AS current_size,
  (SELECT pv.unit FROM product_versions pv
   WHERE pv.product_upc = p.upc ORDER BY pv.observed_date DESC LIMIT 1)
                                              AS current_unit,
  (SELECT pv.price FROM product_versions pv
   WHERE pv.product_upc = p.upc ORDER BY pv.observed_date DESC LIMIT 1)
                                              AS latest_price,
  (SELECT pv.price_per_unit FROM product_versions pv
   WHERE pv.product_upc = p.upc ORDER BY pv.observed_date DESC LIMIT 1)
                                              AS latest_ppu,

  -- Earliest known version
  (SELECT pv.size FROM product_versions pv
   WHERE pv.product_upc = p.upc ORDER BY pv.observed_date ASC LIMIT 1)
                                              AS original_size,

  -- First and last observation dates
  min(pv.observed_date)                       AS first_observed,
  max(pv.observed_date)                       AS last_observed

FROM products p
LEFT JOIN product_versions pv ON pv.product_upc = p.upc
LEFT JOIN change_events ce ON ce.product_upc = p.upc
GROUP BY p.upc, p.name, p.brand, p.category, p.image_url, p.repeat_offender
HAVING count(ce.id) FILTER (WHERE ce.is_shrinkflation) > 0
ORDER BY cumulative_shrink_pct ASC;  -- most shrunk first (most negative)


-- ── View: recent_changes ─────────────────────────────────
-- Latest detected changes. Powers the dashboard and feed.
CREATE OR REPLACE VIEW recent_changes AS
SELECT
  ce.*,
  p.name        AS product_name,
  p.brand       AS product_brand,
  p.category    AS product_category,
  p.image_url   AS product_image_url
FROM change_events ce
JOIN products p ON p.upc = ce.product_upc
ORDER BY ce.detected_date DESC, ce.created_at DESC;


-- ── View: category_stats ─────────────────────────────────
-- Aggregate shrinkflation stats by product category.
CREATE OR REPLACE VIEW category_stats AS
SELECT
  p.category,
  count(DISTINCT p.upc)                       AS product_count,
  count(ce.id)                                AS total_events,
  count(ce.id) FILTER (WHERE ce.is_shrinkflation) AS shrink_events,
  round(avg(ce.size_delta_pct) FILTER (WHERE ce.size_delta_pct < 0), 2)
                                              AS avg_shrink_pct,
  round(avg(ce.price_per_unit_delta_pct) FILTER (WHERE ce.price_per_unit_delta_pct > 0), 2)
                                              AS avg_ppu_increase_pct,
  max(ce.detected_date)                       AS latest_event_date
FROM products p
LEFT JOIN change_events ce ON ce.product_upc = p.upc
WHERE p.category IS NOT NULL
GROUP BY p.category
ORDER BY shrink_events DESC;


-- ── View: pending_review ─────────────────────────────────
-- Staging entries awaiting admin review. Powers the admin dashboard.
CREATE OR REPLACE VIEW pending_review AS
SELECT
  rs.*,
  CASE
    WHEN rs.old_size IS NOT NULL AND rs.new_size IS NOT NULL AND rs.old_size > 0
    THEN round(((rs.new_size - rs.old_size) / rs.old_size) * 100, 2)
    ELSE NULL
  END AS computed_pct
FROM reddit_staging rs
WHERE rs.status = 'pending' AND rs.tier IN ('auto', 'review')
ORDER BY rs.fields_found DESC, rs.score DESC;


-- ── Function: get_product_history ─────────────────────────
-- Returns full product history as JSON for API consumption.
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
    )
  ) INTO result;

  RETURN result;
END;
$$;


-- ── Function: dashboard_stats ─────────────────────────────
-- Quick aggregate stats for the frontend header.
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
    'pending_review',       (SELECT count(*) FROM reddit_staging WHERE status = 'pending' AND tier IN ('auto', 'review'))
  );
END;
$$;

COMMIT;
