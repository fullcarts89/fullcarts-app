-- Add vision analysis columns to reddit_staging so AI-extracted product
-- details and visual-only shrinkflation observations are preserved.

ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS ai_description text;
ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS visual_only boolean DEFAULT false;
