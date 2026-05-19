-- Migration 059: corporate_tree v2 — only manufacturers with >= 5 events.
--
-- v1 (migration 056) had no event-count floor, so single-event Wikidata
-- noise (countries, holding cos, natural persons) leaked onto /insights
-- even after a SPARQL guard caught most of them. This bumps the HAVING
-- clause so a manufacturer only appears when it actually has enough
-- volume to be a meaningful corporate-parent rollup.
--
-- 5 is the same threshold we use elsewhere in the site for "real
-- pattern" vs "one-off claim". Easy to revisit in the view definition
-- if we ever want a finer cut.

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
HAVING SUM(brand_shrink_events) >= 5            -- new: hide single-event manufacturers
ORDER BY total_shrinkflation_events DESC NULLS LAST;

COMMENT ON VIEW corporate_tree IS
    'One row per manufacturer with rolled-up brand and event counts. '
    'Filtered to >= 5 shrinkflation events to keep Wikidata noise off '
    'the /insights page. top_brands carries the three highest-event '
    'child brands with their thumbnails. Updated by migration 059.';
