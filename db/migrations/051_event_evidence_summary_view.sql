-- Migration 051: event_evidence_summary view
--
-- Powers the event-led evidence trail on /brands/[name] (and later
-- /products/[id]). One row per published_changes event, with the
-- contributing claims fully joined out into a `sources` JSONB array
-- so the Next.js page can render a card + click-to-expand list in a
-- single query — no N+1.
--
-- Each source row is shaped:
--   {
--     "claim_id":          uuid,
--     "source_type":       text  -- 'gdelt' | 'news' | 'reddit' | ...
--     "url":               text  -- raw_items.source_url
--     "domain":            text  -- raw_payload.domain (gdelt) or
--                                 -- parsed from source_url
--     "publisher":         text  -- raw_payload.source_name (news) or null
--     "title":             text  -- raw_payload.title
--     "image":             text  -- raw_payload.socialimage (gdelt) or null
--     "claim_image_path":  text  -- supabase storage path for reddit-archived
--                                 -- image, when one exists
--     "date":              timestamptz  -- raw_items.source_date
--   }
--
-- The view is intentionally a regular VIEW, not a materialized one.
-- Per-brand queries are filtered by entity_id and run cheap; if the
-- pattern grows hot we can swap to MATERIALIZED + REFRESH from
-- promote_claims.py.

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
) srcs ON TRUE;

COMMENT ON VIEW event_evidence_summary IS
    'One row per published_changes event with contributing claims '
    'denormalised into a sources JSONB array. Filter by entity_id '
    'for per-brand page renders. Added by migration 051.';
