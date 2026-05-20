-- Migration 067: enrich event_evidence_summary source rows
--
-- The /products/[id] and /brands/[name] event-detail panels need more per-
-- source metadata so admins can triage retract decisions without clicking
-- through to every source. Today's source row shows publisher + title +
-- date. After this migration each source also carries:
--
--   author         — Reddit/news post author (when present)
--   body_excerpt   — first ~240 chars of post body / article description:
--                    * Reddit:    raw_payload.selftext
--                    * GDELT:     raw_payload.socialdescription
--                    * news:      raw_payload.description
--                    Empty selftext is filtered to NULL so the UI can
--                    decide whether to render the excerpt block.
--
-- The view is the only thing changing. Existing fields stay byte-identical;
-- TypeScript types just gain optional properties.

BEGIN;

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
                   'date',             ri.source_date,
                   'author',           ri.raw_payload->>'author',
                   'body_excerpt',     NULLIF(
                                           LEFT(
                                               COALESCE(
                                                   ri.raw_payload->>'selftext',
                                                   ri.raw_payload->>'socialdescription',
                                                   ri.raw_payload->>'description',
                                                   ''
                                               ),
                                               240
                                           ),
                                           ''
                                       )
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

COMMIT;

-- Verification: pick a high-evidence Cadbury event and confirm the new
-- fields surface on Reddit-typed sources.
--
--   SELECT event_id, brand, product_name,
--          jsonb_path_query(sources, '$[*] ? (@.source_type == "reddit")')
--                          ->>'author' AS reddit_author
--     FROM event_evidence_summary
--    WHERE brand ILIKE '%cadbury%'
--      AND jsonb_path_exists(sources, '$[*] ? (@.source_type == "reddit")')
--    LIMIT 3;
