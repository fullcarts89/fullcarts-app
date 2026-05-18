-- Migration 062: Entity retraction (Phase 2D step 1)
--
-- Originally drafted as migration 054 in PR #75. Renumbered to 062 during
-- the rebase onto main because 054 was claimed by `054_product_index_view.sql`
-- (PR #73 product index work) which landed first. The semantics of this
-- migration are unchanged — only the file name moved.
--
-- Adds an `is_retracted` flag to `product_entities` so the admin can pull
-- bad entities offline without deleting them. Sister column to the
-- pre-existing `published_changes.is_retracted` from migration 001.
--
-- Retracting an entity must also retract every event tied to that entity,
-- otherwise existing views (which all filter `WHERE NOT pc.is_retracted`)
-- would keep surfacing the retracted entity's events under the brand-level
-- aggregates. The `set_entity_retracted` RPC encapsulates both writes in
-- one transaction so the admin action can't half-apply.
--
-- Views that pull from `product_entities` independent of `published_changes`
-- (brand_index's brand_thumbs / brand_cats CTEs, dashboard_stats counts)
-- get explicit `is_retracted = false` filters. Everything else benefits
-- automatically from the event cascade.

-- 1. The column
ALTER TABLE product_entities
    ADD COLUMN IF NOT EXISTS is_retracted BOOLEAN NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_entities_active
    ON product_entities (id)
    WHERE NOT is_retracted;

COMMENT ON COLUMN product_entities.is_retracted IS
    'Admin-set: hides this entity (and cascades to its published_changes) '
    'from every public view. Reversible. Toggle via set_entity_retracted() RPC.';

-- 2. RPC — single-transaction toggle for entity + its events
CREATE OR REPLACE FUNCTION set_entity_retracted(
    p_entity_id  UUID,
    p_retracted  BOOLEAN
)
RETURNS TABLE (entity_id UUID, events_affected INTEGER)
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
    v_events_affected INTEGER;
BEGIN
    UPDATE product_entities
       SET is_retracted = p_retracted,
           updated_at   = now()
     WHERE id = p_entity_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'entity % not found', p_entity_id;
    END IF;

    UPDATE published_changes
       SET is_retracted = p_retracted
     WHERE entity_id = p_entity_id
       AND is_retracted IS DISTINCT FROM p_retracted;

    GET DIAGNOSTICS v_events_affected = ROW_COUNT;

    RETURN QUERY SELECT p_entity_id, v_events_affected;
END;
$$;

COMMENT ON FUNCTION set_entity_retracted IS
    'Atomically retract/unretract an entity AND all its published_changes. '
    'Returns the entity id + number of event rows whose flag actually flipped.';

-- 3. Rebuild brand_index — its CTEs pull product_entities outside the
--    published_changes path, so they need explicit filtering.
--    Migration 053 last touched this; preserving its column list.
DROP VIEW IF EXISTS brand_index;

CREATE VIEW brand_index AS
WITH brand_thumbs AS (
    SELECT DISTINCT ON (brand) brand, image_url
    FROM   product_entities
    WHERE  image_url IS NOT NULL
      AND  NOT is_retracted
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
          AND  NOT is_retracted
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
    'One row per brand. Migration 062 added is_retracted filters to the '
    'thumb + category CTEs so retracted entities can''t leak their image '
    'or category into the brand index.';

-- 4. event_evidence_summary — pre-existing leak: it never filtered
--    pc.is_retracted, so retracted events from published_changes leaked
--    into /brands/[name] and /products/[id]. Fix while we're rebuilding
--    views that touch retraction. (Definition otherwise unchanged from
--    migration 051.)
CREATE OR REPLACE VIEW event_evidence_summary AS
SELECT
    pc.id              AS event_id,
    pc.entity_id,
    pc.brand,
    pc.product_name,
    pc.size_before,
    pc.size_after,
    pc.size_unit,
    pc.size_delta_pct,
    pc.severity,
    pc.observed_date,
    pc.evidence_count,
    COALESCE(srcs.sources, '[]'::jsonb) AS sources
FROM published_changes pc
LEFT JOIN LATERAL (
    SELECT jsonb_agg(
               jsonb_build_object(
                   'claim_id',         c.id,
                   'source_type',      ri.source_type,
                   'url',              ri.source_url,
                   'domain',           COALESCE(
                                           ri.raw_payload->>'domain',
                                           substring(
                                               ri.source_url FROM
                                               '^https?://(?:www\.)?([^/]+)'
                                           )
                                       ),
                   'publisher',        ri.raw_payload->>'source_name',
                   'title',            ri.raw_payload->>'title',
                   'image',            ri.raw_payload->>'socialimage',
                   'claim_image_path', c.image_storage_path,
                   'date',             ri.source_date
               )
               ORDER BY ri.source_date DESC NULLS LAST
           ) AS sources
    FROM   jsonb_array_elements(pc.evidence_summary) AS evt
    JOIN   claims c
        ON c.id = (evt->>'claim_id')::uuid
    LEFT JOIN raw_items ri
        ON ri.id = c.raw_item_id
) srcs ON TRUE
WHERE NOT pc.is_retracted;

-- 5. dashboard_stats — exclude retracted entities from product/category counts.
CREATE OR REPLACE FUNCTION dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql STABLE
SET search_path = public
AS $$
BEGIN
  RETURN jsonb_build_object(
    'total_products', (
        SELECT count(*) FROM product_entities WHERE NOT is_retracted
    ),
    'total_changes', (
        SELECT count(*) FROM published_changes WHERE NOT is_retracted
    ),
    'shrinkflation_events', (
        SELECT count(*) FROM published_changes
        WHERE NOT is_retracted AND change_type = 'shrinkflation'
    ),
    'categories_tracked', (
        SELECT count(DISTINCT category) FROM product_entities
        WHERE category IS NOT NULL AND NOT is_retracted
    ),
    'avg_shrink_pct', (
        SELECT round(avg(abs(size_delta_pct)), 1) FROM published_changes
        WHERE size_delta_pct < 0 AND NOT is_retracted
    ),
    'worst_shrink_pct', (
        SELECT round(min(size_delta_pct), 1) FROM published_changes
        WHERE NOT is_retracted
    ),
    'pending_review', (
        SELECT count(*) FROM claims WHERE status = 'pending'
    )
  );
END;
$$;
