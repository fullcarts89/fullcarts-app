-- Migration 054: product_index view
--
-- Powers the /products index page. One row per product_entity with at
-- least one non-retracted shrinkflation event. Mirrors the brand_index
-- shape (added in 052 / extended in 053) so the same client component
-- pattern can drive both directories.
--
-- Fields:
--   entity_id, brand, canonical_name, category, image_url
--   shrinkflation_events, restoration_events
--   avg_shrink_per_event   (avg size_delta_pct for shrinks only)
--   worst_delta_pct        (min size_delta_pct for shrinks; most-negative)
--   first_detected, last_detected
--   manufacturer (passthrough — null until Wikidata backfill ships)

CREATE OR REPLACE VIEW product_index AS
SELECT
    pe.id              AS entity_id,
    pe.brand,
    pe.canonical_name,
    pe.category,
    pe.image_url,
    pe.manufacturer,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrinkflation_events,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'restoration')   AS restoration_events,
    ROUND(
        AVG(pc.size_delta_pct) FILTER (
            WHERE pc.change_type = 'shrinkflation'
              AND pc.size_delta_pct IS NOT NULL
        )::numeric,
        1
    ) AS avg_shrink_per_event,
    MIN(pc.size_delta_pct) FILTER (
        WHERE pc.change_type = 'shrinkflation'
    ) AS worst_delta_pct,
    MIN(pc.observed_date) AS first_detected,
    MAX(pc.observed_date) AS last_detected
FROM   product_entities pe
JOIN   published_changes pc ON pc.entity_id = pe.id
WHERE  NOT pc.is_retracted
GROUP  BY pe.id, pe.brand, pe.canonical_name, pe.category, pe.image_url, pe.manufacturer
HAVING COUNT(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') > 0;

COMMENT ON VIEW product_index IS
    'One row per product_entity with at least one non-retracted '
    'shrinkflation event. Powers the /products index page. Mirrors '
    'brand_index shape (migration 052 + 053).';
