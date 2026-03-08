-- 012_full_data_reset.sql
-- Full data wipe for clean re-scrape.
-- Run once, then trigger a backfill via the scrape_reddit workflow.
--
-- Safe order: products CASCADE handles all FK children,
-- then clear independent tables.

BEGIN;

-- Cascade-deletes: events, product_versions, change_events,
-- upvotes, flags, confirmations
DELETE FROM products;

-- Independent tables (no FK constraints)
DELETE FROM reddit_staging;
DELETE FROM evidence_wall;
DELETE FROM submissions;
DELETE FROM contributors;

COMMIT;
