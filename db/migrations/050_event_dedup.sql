-- Migration 050: Event deduplication
--
-- Each shrinkflation event ought to be a single published_changes row with
-- multiple corroborating sources, not N rows for N syndicated copies of the
-- same article. Before this migration, news syndication (Newsquest, Reach
-- plc, etc.) inflated Cadbury's event count from ~115 unique events to 395
-- separately-counted rows.
--
-- This migration:
--   1. Adds evidence_count to published_changes (default 1)
--   2. Pre-populates it from the existing evidence_summary array length so
--      we have an accurate count on day one
--   3. Adds an index to support the dedup-on-promote lookup that runs on
--      every new approved claim going forward
--
-- The actual de-duplication of existing rows runs as a separate one-time
-- script (pipeline/scripts/dedup_events.py) immediately after this lands.

-- 1. Add evidence_count column (every existing row has 1 supporting claim,
--    so the default of 1 is correct until the backfill recomputes it)
ALTER TABLE published_changes
  ADD COLUMN IF NOT EXISTS evidence_count INTEGER NOT NULL DEFAULT 1;

-- 2. Index the dedup lookup key. Every approved claim now triggers a
--    SELECT on (entity_id, size_before, size_after, observed_date) to
--    decide whether to merge into an existing event or create a new one.
CREATE INDEX IF NOT EXISTS idx_published_changes_dedup_key
  ON published_changes (entity_id, size_before, size_after, observed_date)
  WHERE NOT is_retracted;

-- 3. Pre-populate evidence_count from the existing evidence_summary JSONB
--    array length so the count is meaningful immediately (will be
--    overwritten as the backfill script merges duplicates).
UPDATE published_changes
SET    evidence_count = COALESCE(jsonb_array_length(evidence_summary), 1)
WHERE  evidence_summary IS NOT NULL
  AND  jsonb_array_length(evidence_summary) >= 1;
