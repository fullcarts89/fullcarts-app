-- Add body and image_url columns to reddit_staging so reviewers can see
-- original post content even when the Reddit post has been deleted or archived.
ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS body text;
ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS image_url text;
