-- Drop region columns from all tables
-- Region is too speculative for community-reported data — hard to pinpoint
-- where a product change is happening from a Reddit post alone.

ALTER TABLE reddit_staging DROP COLUMN IF EXISTS region;
ALTER TABLE products DROP COLUMN IF EXISTS region;
ALTER TABLE product_versions DROP COLUMN IF EXISTS region;
