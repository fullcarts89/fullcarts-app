-- Aggregate daily claim extraction counts by source type (last N days)
-- Returns one row per (date, source_type) with claim count
CREATE OR REPLACE FUNCTION pipeline_daily_stats(days_back integer DEFAULT 14)
RETURNS TABLE (
  extraction_date date,
  source_type text,
  claim_count bigint
)
LANGUAGE sql STABLE
AS $$
  SELECT
    DATE(c.extracted_at) AS extraction_date,
    r.source_type,
    COUNT(*) AS claim_count
  FROM claims c
  JOIN raw_items r ON c.raw_item_id = r.id
  WHERE c.extracted_at >= NOW() - (days_back || ' days')::interval
  GROUP BY DATE(c.extracted_at), r.source_type
  ORDER BY extraction_date, r.source_type;
$$;
