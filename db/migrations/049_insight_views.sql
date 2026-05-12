-- Migration 049: Add insight views for content generation and public website
--
-- These views power the public-facing pages and social media content pipeline.
-- They build on the existing brand_scorecard, category_stats, and recent_changes
-- views from migration 043.

-- 1. brand_rankings — Top brands ranked by shrinkflation frequency
CREATE OR REPLACE VIEW brand_rankings AS
SELECT
  brand,
  product_count,
  shrinkflation_events,
  restoration_events,
  total_shrinkage_pct,
  ROUND(total_shrinkage_pct / NULLIF(shrinkflation_events, 0), 1) AS avg_shrink_per_event,
  first_detected,
  last_detected
FROM brand_scorecard
WHERE brand IS NOT NULL
ORDER BY shrinkflation_events DESC;

-- 2. biggest_shrinks — Most dramatic individual product downsizings
CREATE OR REPLACE VIEW biggest_shrinks AS
SELECT
  pc.id,
  pc.brand,
  pc.product_name,
  pc.size_before,
  pc.size_after,
  pc.size_unit,
  pc.size_delta_pct,
  pc.observed_date,
  pc.published_at,
  pe.image_url,
  pe.category
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE pc.change_type = 'shrinkflation'
  AND NOT pc.is_retracted
  AND pc.size_delta_pct IS NOT NULL
ORDER BY pc.size_delta_pct ASC;

-- 3. shrinkflation_timeline — Monthly event counts for charting
CREATE OR REPLACE VIEW shrinkflation_timeline AS
SELECT
  DATE_TRUNC('month', observed_date)::date AS month,
  COUNT(*) AS events,
  COUNT(*) FILTER (WHERE change_type = 'shrinkflation') AS shrink_events,
  COUNT(*) FILTER (WHERE change_type = 'restoration') AS restoration_events,
  ROUND(AVG(size_delta_pct) FILTER (WHERE size_delta_pct < 0), 1) AS avg_shrink_pct
FROM published_changes
WHERE NOT is_retracted
  AND observed_date IS NOT NULL
GROUP BY DATE_TRUNC('month', observed_date)
ORDER BY month;

-- 4. cpi_shrinkflation_context — FRED CPI alongside shrinkflation event counts
CREATE OR REPLACE VIEW cpi_shrinkflation_context AS
SELECT
  f.observation_date,
  f.series_name,
  f.value AS food_at_home_cpi,
  LAG(f.value) OVER (ORDER BY f.observation_date) AS prev_month_cpi,
  ROUND(
    ((f.value - LAG(f.value) OVER (ORDER BY f.observation_date))
     / NULLIF(LAG(f.value) OVER (ORDER BY f.observation_date), 0)) * 100,
    2
  ) AS cpi_mom_change_pct,
  (SELECT COUNT(*)
   FROM published_changes pc
   WHERE NOT pc.is_retracted
     AND DATE_TRUNC('month', pc.observed_date) = DATE_TRUNC('month', f.observation_date)
  ) AS shrink_events_that_month
FROM fred_cpi_data f
WHERE f.series_id = 'CPIUFDNS'
ORDER BY f.observation_date DESC;

-- 5. content_candidates — Scored published changes for social media selection
CREATE OR REPLACE VIEW content_candidates AS
SELECT
  pc.id,
  pc.brand,
  pc.product_name,
  pc.size_before,
  pc.size_after,
  pc.size_unit,
  pc.size_delta_pct,
  pc.change_type,
  pc.severity,
  pc.observed_date,
  pc.published_at,
  pc.evidence_summary,
  pe.image_url,
  pe.category,
  (CASE WHEN pe.image_url IS NOT NULL THEN 20 ELSE 0 END)
  + (CASE WHEN ABS(pc.size_delta_pct) >= 20 THEN 25
          WHEN ABS(pc.size_delta_pct) >= 10 THEN 15
          WHEN ABS(pc.size_delta_pct) >= 5 THEN 10
          ELSE 5 END)
  + (CASE WHEN pc.observed_date >= CURRENT_DATE - 30 THEN 15
          WHEN pc.observed_date >= CURRENT_DATE - 90 THEN 10
          WHEN pc.observed_date >= CURRENT_DATE - 365 THEN 5
          ELSE 0 END)
  AS content_score
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE NOT pc.is_retracted
ORDER BY content_score DESC;

-- 6. news_brand_mentions — Cross-reference news coverage with our data
CREATE OR REPLACE VIEW news_brand_mentions AS
SELECT
  c.brand,
  COUNT(DISTINCT ri.id) AS news_mentions,
  bs.shrinkflation_events AS documented_events,
  MIN(ri.source_date) AS earliest_news_mention,
  MAX(ri.source_date) AS latest_news_mention
FROM claims c
JOIN raw_items ri ON ri.id = c.raw_item_id
LEFT JOIN brand_scorecard bs ON lower(bs.brand) = lower(c.brand)
WHERE ri.source_type IN ('news', 'gdelt')
  AND c.brand IS NOT NULL
GROUP BY c.brand, bs.shrinkflation_events
HAVING COUNT(DISTINCT ri.id) >= 2
ORDER BY news_mentions DESC;
