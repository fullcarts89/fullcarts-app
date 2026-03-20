-- Migration 043: Rewrite views to use new schema
-- The old views reference products/product_versions/change_events (now empty)
-- This rewrites them to use product_entities/published_changes

-- 1. shrinkflation_leaderboard
CREATE OR REPLACE VIEW shrinkflation_leaderboard AS
SELECT
  pe.id AS entity_id,
  pe.canonical_name AS name,
  pe.brand,
  pe.category,
  pe.image_url,
  count(pc.id) AS total_changes,
  count(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrink_count,
  round(sum(pc.size_delta_pct) FILTER (WHERE pc.size_delta_pct < 0), 2) AS cumulative_shrink_pct,
  min(pc.observed_date) AS first_observed,
  max(pc.observed_date) AS last_observed
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE NOT pc.is_retracted
GROUP BY pe.id, pe.canonical_name, pe.brand, pe.category, pe.image_url
HAVING count(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') > 0
ORDER BY cumulative_shrink_pct ASC;

-- 2. brand_scorecard
CREATE OR REPLACE VIEW brand_scorecard AS
SELECT
  pe.brand,
  count(DISTINCT pe.id) AS product_count,
  count(pc.id) AS total_events,
  count(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrinkflation_events,
  count(pc.id) FILTER (WHERE pc.change_type = 'restoration') AS restoration_events,
  round(sum(pc.size_delta_pct) FILTER (WHERE pc.change_type = 'shrinkflation'), 2) AS total_shrinkage_pct,
  min(pc.observed_date) AS first_detected,
  max(pc.observed_date) AS last_detected
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE NOT pc.is_retracted
GROUP BY pe.brand
ORDER BY shrinkflation_events DESC;

-- 3. recent_changes
CREATE OR REPLACE VIEW recent_changes AS
SELECT
  pc.*,
  pe.canonical_name AS product_canonical_name,
  pe.brand AS product_brand,
  pe.category AS product_category,
  pe.image_url AS product_image_url
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE NOT pc.is_retracted
ORDER BY pc.published_at DESC;

-- 4. category_stats
CREATE OR REPLACE VIEW category_stats AS
SELECT
  pe.category,
  count(DISTINCT pe.id) AS product_count,
  count(pc.id) AS total_events,
  count(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrink_events,
  round(avg(pc.size_delta_pct) FILTER (WHERE pc.size_delta_pct < 0), 2) AS avg_shrink_pct,
  max(pc.observed_date) AS latest_event_date
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE pe.category IS NOT NULL AND NOT pc.is_retracted
GROUP BY pe.category
ORDER BY shrink_events DESC;

-- 5. restorations
CREATE OR REPLACE VIEW restorations AS
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
  AND NOT pc.is_retracted
ORDER BY pc.published_at DESC;

-- 6. dashboard_stats function
CREATE OR REPLACE FUNCTION dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql STABLE
SET search_path = public
AS $$
BEGIN
  RETURN jsonb_build_object(
    'total_products', (SELECT count(*) FROM product_entities),
    'total_changes', (SELECT count(*) FROM published_changes WHERE NOT is_retracted),
    'shrinkflation_events', (SELECT count(*) FROM published_changes WHERE NOT is_retracted AND change_type = 'shrinkflation'),
    'categories_tracked', (SELECT count(DISTINCT category) FROM product_entities WHERE category IS NOT NULL),
    'avg_shrink_pct', (SELECT round(avg(abs(size_delta_pct)), 1) FROM published_changes WHERE size_delta_pct < 0 AND NOT is_retracted),
    'worst_shrink_pct', (SELECT round(min(size_delta_pct), 1) FROM published_changes WHERE NOT is_retracted),
    'pending_review', (SELECT count(*) FROM claims WHERE status = 'pending')
  );
END;
$$;
