-- Drop date_before column from reddit_staging
-- Community members report when they noticed shrinkflation, not when the old size existed.
-- The "before" date is always a guess. We keep only date_noticed.

ALTER TABLE reddit_staging DROP COLUMN IF EXISTS date_before;
