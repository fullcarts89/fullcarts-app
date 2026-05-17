-- Migration 052: brand_index view
--
-- Powers the /brands index page. Joins brand_rankings with a single
-- representative thumbnail per brand (pulled from the most-recent
-- product_entity that has an image). One query from the page, sorted
-- in JS for the four sort options the index supports.

CREATE OR REPLACE VIEW brand_index AS
WITH brand_thumbs AS (
    SELECT DISTINCT ON (brand) brand, image_url
    FROM   product_entities
    WHERE  image_url IS NOT NULL
    ORDER  BY brand, created_at DESC
),
brand_worst AS (
    SELECT brand, MIN(size_delta_pct) AS worst_delta_pct
    FROM   published_changes
    WHERE  NOT is_retracted AND change_type = 'shrinkflation'
    GROUP  BY brand
)
SELECT br.brand,
       br.product_count,
       br.shrinkflation_events,
       br.restoration_events,
       br.avg_shrink_per_event,
       br.first_detected,
       br.last_detected,
       bt.image_url      AS thumbnail,
       bw.worst_delta_pct
FROM   brand_rankings br
LEFT JOIN brand_thumbs bt ON bt.brand = br.brand
LEFT JOIN brand_worst  bw ON bw.brand = br.brand;

COMMENT ON VIEW brand_index IS
    'One row per brand for the /brands index page. Joins '
    'brand_rankings with a representative thumbnail and the brand''s '
    'worst single-event shrink. Added by migration 052.';
