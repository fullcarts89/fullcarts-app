-- Add date_noticed column to reddit_staging
-- Stores the first-of-month date when the shrinkflation was noticed (derived from post date)
ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS date_noticed date;
