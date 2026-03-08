-- ============================================================
-- Migration 011: Data quality & human-review-required pipeline
--
-- Key changes:
--   1. Add confidence_score, extraction_method to staging
--   2. Add reviewer audit trail fields to staging
--   3. Add retailer to product_versions (region removed in 014)
--   4. Add false_positive + retracted_at to change_events
--   5. Update promote function to require human review
--   6. Add validation constraints
-- ============================================================

BEGIN;

-- ═══════════════════════════════════════════════════════════════
-- 1. REDDIT_STAGING: richer extraction metadata
-- ═══════════════════════════════════════════════════════════════

-- Numeric confidence score (0-100) instead of just tier
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS confidence_score integer DEFAULT 0
  CHECK (confidence_score BETWEEN 0 AND 100);

COMMENT ON COLUMN reddit_staging.confidence_score IS
  'Numeric extraction confidence: 0-100. Calculated from fields_found, keyword match, vision analysis, source reliability.';

-- How was the data extracted?
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS extraction_method text DEFAULT 'text';

COMMENT ON COLUMN reddit_staging.extraction_method IS
  'Primary extraction method: text, vision, text+vision, manual';

-- region column removed in migration 014_drop_region.sql

-- Retailer mentioned in post (Walmart, Costco, etc.)
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS retailer text;


-- ═══════════════════════════════════════════════════════════════
-- 2. REDDIT_STAGING: reviewer audit trail
-- ═══════════════════════════════════════════════════════════════

-- Who reviewed this entry (session_id or 'admin')
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS reviewed_by text;

-- When was it reviewed
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS reviewed_at timestamptz;

-- Which fields did the reviewer edit (JSON array of field names)
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS fields_edited text[];

-- Reviewer notes (why rejected, corrections made, etc.)
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS review_notes text;

-- Original values before reviewer edits (snapshot for audit)
ALTER TABLE reddit_staging
  ADD COLUMN IF NOT EXISTS original_values jsonb;

-- date_before column removed in migration 013_drop_date_before.sql


-- ═══════════════════════════════════════════════════════════════
-- 3. PRODUCT_VERSIONS: retailer + region
-- ═══════════════════════════════════════════════════════════════

-- region column removed in migration 014_drop_region.sql

-- (retailer column already exists in product_versions — just add comment)
COMMENT ON COLUMN product_versions.retailer IS
  'Store where this size/price was observed (Walmart, Costco, Target, etc.)';


-- ═══════════════════════════════════════════════════════════════
-- 4. CHANGE_EVENTS: retractions / false positives
-- ═══════════════════════════════════════════════════════════════

ALTER TABLE change_events
  ADD COLUMN IF NOT EXISTS false_positive boolean DEFAULT false;

ALTER TABLE change_events
  ADD COLUMN IF NOT EXISTS retracted_at timestamptz;

ALTER TABLE change_events
  ADD COLUMN IF NOT EXISTS retracted_by text;

ALTER TABLE change_events
  ADD COLUMN IF NOT EXISTS retraction_reason text;

COMMENT ON COLUMN change_events.false_positive IS
  'Marked true when a change_event is determined to be incorrect data.';


-- region column for products removed in migration 014_drop_region.sql


-- ═══════════════════════════════════════════════════════════════
-- 6. Updated update_staging_status RPC to record audit fields
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION update_staging_status_v2(
  row_id uuid,
  new_status text,
  reviewer text DEFAULT 'admin',
  edited_fields text[] DEFAULT NULL,
  notes text DEFAULT NULL
)
RETURNS void
LANGUAGE plpgsql SECURITY DEFINER AS $$
BEGIN
  UPDATE reddit_staging
  SET status = new_status,
      reviewed_by = reviewer,
      reviewed_at = now(),
      fields_edited = COALESCE(edited_fields, fields_edited),
      review_notes = COALESCE(notes, review_notes)
  WHERE id = row_id;
END;
$$;


-- ═══════════════════════════════════════════════════════════════
-- 7. Updated dashboard_stats with quality metrics
-- ═══════════════════════════════════════════════════════════════

CREATE OR REPLACE FUNCTION dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql STABLE AS $$
BEGIN
  RETURN jsonb_build_object(
    'total_products',       (SELECT count(*) FROM products),
    'total_versions',       (SELECT count(*) FROM product_versions),
    'total_changes',        (SELECT count(*) FROM change_events),
    'shrinkflation_events', (SELECT count(*) FROM change_events WHERE is_shrinkflation AND NOT false_positive),
    'categories_tracked',   (SELECT count(DISTINCT category) FROM products WHERE category IS NOT NULL),
    'avg_shrink_pct',       (SELECT round(avg(abs(size_delta_pct)), 1) FROM change_events WHERE size_delta_pct < 0 AND NOT false_positive),
    'worst_shrink_pct',     (SELECT round(min(size_delta_pct), 1) FROM change_events WHERE NOT false_positive),
    'pending_review',       (SELECT count(*) FROM reddit_staging WHERE status = 'pending' AND tier IN ('auto', 'review')),
    'total_staged',         (SELECT count(*) FROM reddit_staging),
    'staged_promoted',      (SELECT count(*) FROM reddit_staging WHERE status = 'promoted'),
    'staged_dismissed',     (SELECT count(*) FROM reddit_staging WHERE status = 'dismissed'),
    'staged_rejected',      (SELECT count(*) FROM reddit_staging WHERE status = 'rejected'),
    'staged_evidence_wall', (SELECT count(*) FROM reddit_staging WHERE status = 'evidence_wall'),
    'evidence_wall_count',  (SELECT count(*) FROM evidence_wall WHERE status = 'approved'),
    'total_signals',        (SELECT count(*) FROM signals_summary WHERE confidence = 'confirmed' OR confidence = 'suspicious'),
    'confirmed_signals',    (SELECT count(*) FROM signals_summary WHERE confidence = 'confirmed'),
    'suspicious_signals',   (SELECT count(*) FROM signals_summary WHERE confidence = 'suspicious'),
    'brands_tracked',       (SELECT count(DISTINCT brand) FROM signals_summary WHERE brand IS NOT NULL),
    'false_positives',      (SELECT count(*) FROM change_events WHERE false_positive),
    'avg_confidence',       (SELECT round(avg(confidence_score), 0) FROM reddit_staging WHERE status = 'promoted')
  );
END;
$$;

COMMIT;
