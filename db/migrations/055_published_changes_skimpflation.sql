-- Migration 055: extend published_changes to carry skimpflation events
--
-- Until now published_changes was strictly size-based: every row had a
-- non-null size_before / size_after / size_unit / size_delta_pct.
-- Migration 029 already gave us the `nutrition_skimpflation()` function
-- that detects ingredient swaps from USDA cross-release diffs, but
-- those findings were never folded into the same event stream the
-- public site renders.
--
-- This migration:
--   1. Relaxes the size_* NOT NULLs so non-size events can be inserted.
--   2. Adds skimp_score + nutrient_deltas JSON columns for skimpflation
--      payloads. Both nullable; they only fill for change_type='skimpflation'.
--   3. Adds a sanity CHECK so size-based events still carry size data
--      and skimpflation events still carry skimp data.
--
-- The script that produces these rows is
-- `pipeline/scripts/promote_skimpflation.py` (added in the same PR).
-- It runs daily via `pipeline_promote.yml`.

ALTER TABLE published_changes
    ALTER COLUMN size_before    DROP NOT NULL,
    ALTER COLUMN size_after     DROP NOT NULL,
    ALTER COLUMN size_unit      DROP NOT NULL,
    ALTER COLUMN size_delta_pct DROP NOT NULL,
    -- Skimpflation events don't run through change_candidates.
    ALTER COLUMN candidate_id   DROP NOT NULL;

ALTER TABLE published_changes
    ADD COLUMN IF NOT EXISTS skimp_score      NUMERIC,
    ADD COLUMN IF NOT EXISTS nutrient_deltas  JSONB;

-- Sanity: size events still need size data, skimp events still need
-- nutrient data. The constraint is permissive on purpose — restoration
-- + shrinkflation + downsizing all keep the old shape; only the new
-- 'skimpflation' rows are allowed to skip size_*.
ALTER TABLE published_changes DROP CONSTRAINT IF EXISTS published_changes_shape_check;
ALTER TABLE published_changes ADD CONSTRAINT published_changes_shape_check CHECK (
    (
        change_type = 'skimpflation'
        AND skimp_score IS NOT NULL
        AND nutrient_deltas IS NOT NULL
    )
    OR (
        change_type <> 'skimpflation'
        AND size_before IS NOT NULL
        AND size_after IS NOT NULL
        AND size_unit IS NOT NULL
        AND size_delta_pct IS NOT NULL
    )
);

-- Indexes — we'll filter by change_type a lot now that the column has
-- a third meaningful value.
CREATE INDEX IF NOT EXISTS idx_published_skimpflation
    ON published_changes (entity_id, observed_date DESC)
    WHERE change_type = 'skimpflation' AND NOT is_retracted;

-- The size-focused views all pre-date skimpflation events; the cleanest
-- way to keep them honest is to exclude change_type='skimpflation' at
-- the view boundary. New skimp-aware queries should hit published_changes
-- directly.

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
WHERE pc.change_type <> 'skimpflation';

-- Same shape, but only the skimpflation rows. Used by the upcoming
-- /products/[id] integration so the page can render its nutrient table
-- straight from published_changes (no separate USDA call needed once
-- the pipeline starts populating).
CREATE OR REPLACE VIEW skimpflation_events AS
SELECT
    pc.id              AS event_id,
    pc.entity_id,
    pc.brand,
    pc.product_name,
    pc.severity,
    pc.observed_date,
    pc.skimp_score,
    pc.nutrient_deltas,
    pc.evidence_count,
    pc.evidence_summary
FROM published_changes pc
WHERE pc.change_type = 'skimpflation' AND NOT pc.is_retracted;

COMMENT ON VIEW skimpflation_events IS
    'Skimpflation-only slice of published_changes (change_type='
    '''skimpflation''). One row per documented recipe change; '
    'nutrient_deltas carries the per-nutrient before/after JSON. '
    'Added by migration 055.';

COMMENT ON COLUMN published_changes.skimp_score IS
    'Aggregate skimpflation score (sum of bad-direction nutrient '
    'deltas). Null for non-skimpflation rows. See migration 055.';
COMMENT ON COLUMN published_changes.nutrient_deltas IS
    'JSON array of { nutrient, unit, before, after, delta_pct, '
    'bad_direction }. Null for non-skimpflation rows.';
