-- Add body column to reddit_staging so reviewers can see original post content
-- even when the Reddit post has been deleted or archived.
ALTER TABLE reddit_staging ADD COLUMN IF NOT EXISTS body text;
