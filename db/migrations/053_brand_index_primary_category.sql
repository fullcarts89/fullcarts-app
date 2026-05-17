-- Migration 053: extend brand_index view with primary_category
--
-- /brands index needs a per-brand category to power the category-filter
-- chip strip and to let users browse the directory by what they shop.
-- primary_category = the category that the most product_entities under
-- this brand carry (mode). Null for brands whose entities have no
-- category set.
--
-- CREATE OR REPLACE VIEW can't change a view's column list, so DROP
-- + CREATE. Safe because no migrations or app code other than the
-- /brands page reads brand_index today.

DROP VIEW IF EXISTS brand_index;

CREATE VIEW brand_index AS
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
),
brand_cats AS (
    SELECT DISTINCT ON (brand) brand, category AS primary_category
    FROM (
        SELECT brand, category, COUNT(*) AS cnt
        FROM   product_entities
        WHERE  category IS NOT NULL
        GROUP  BY brand, category
    ) c
    ORDER BY brand, cnt DESC
)
SELECT br.brand,
       br.product_count,
       br.shrinkflation_events,
       br.restoration_events,
       br.avg_shrink_per_event,
       br.first_detected,
       br.last_detected,
       bt.image_url       AS thumbnail,
       bw.worst_delta_pct,
       bc.primary_category
FROM   brand_rankings br
LEFT JOIN brand_thumbs bt ON bt.brand = br.brand
LEFT JOIN brand_worst  bw ON bw.brand = br.brand
LEFT JOIN brand_cats   bc ON bc.brand = br.brand;

COMMENT ON VIEW brand_index IS
    'One row per brand. Migration 052 added it; migration 053 added '
    'primary_category (mode of product_entities.category per brand).';
