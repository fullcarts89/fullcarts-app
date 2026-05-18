-- Migration 056: indexes + view for the corporate-parent tree
--
-- product_entities.manufacturer already exists (migration 001 declared
-- it nullable), but every row is currently NULL because no scraper has
-- populated it. This migration:
--
--   1. Adds an index on manufacturer for the corporate-tree queries.
--   2. Adds a `corporate_tree` view that surfaces, per manufacturer:
--      - distinct_brands count
--      - total_products
--      - total_shrinkflation_events
--      - worst_delta_pct (across all child events)
--      - a sample of representative brand thumbnails (top 3 by events)
--
-- The pipeline script `wikidata_manufacturer_backfill.py` (added in the
-- same PR) is what fills the column. Once that runs the view becomes
-- non-empty and the /insights "corporate parents" section lights up.

CREATE INDEX IF NOT EXISTS idx_entities_manufacturer
    ON product_entities (lower(manufacturer))
    WHERE manufacturer IS NOT NULL;

CREATE OR REPLACE VIEW corporate_tree AS
WITH brand_events AS (
    SELECT
        pe.manufacturer,
        pe.brand,
        COUNT(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS brand_shrink_events,
        MIN(pc.size_delta_pct) FILTER (WHERE pc.change_type = 'shrinkflation') AS brand_worst,
        MAX(pe.image_url)        AS brand_thumb
    FROM   product_entities pe
    LEFT JOIN published_changes pc
           ON pc.entity_id = pe.id AND NOT pc.is_retracted
    WHERE  pe.manufacturer IS NOT NULL
      AND  pe.manufacturer <> ''
    GROUP  BY pe.manufacturer, pe.brand
)
SELECT
    manufacturer,
    COUNT(DISTINCT brand)                 AS distinct_brands,
    SUM(brand_shrink_events)              AS total_shrinkflation_events,
    MIN(brand_worst)                      AS worst_delta_pct,
    -- Top three brands by event count, with their thumbs, for the
    -- card preview on /insights. Aggregated as a JSON array so the
    -- page can iterate without a second query.
    (
        SELECT jsonb_agg(jsonb_build_object(
                   'brand', x.brand,
                   'events', x.brand_shrink_events,
                   'worst', x.brand_worst,
                   'thumbnail', x.brand_thumb
               ) ORDER BY x.brand_shrink_events DESC NULLS LAST)
        FROM (
            SELECT be.brand, be.brand_shrink_events, be.brand_worst, be.brand_thumb
            FROM   brand_events be
            WHERE  be.manufacturer = be_outer.manufacturer
            ORDER  BY be.brand_shrink_events DESC NULLS LAST
            LIMIT  3
        ) x
    ) AS top_brands
FROM brand_events be_outer
GROUP BY manufacturer
HAVING COUNT(DISTINCT brand) >= 1
ORDER BY total_shrinkflation_events DESC NULLS LAST;

COMMENT ON VIEW corporate_tree IS
    'One row per manufacturer with rolled-up brand and event counts. '
    'top_brands carries the three highest-event child brands with '
    'their thumbnails. Empty until wikidata_manufacturer_backfill.py '
    'has run. Added by migration 056.';
