-- Add unique constraint on events to prevent duplicate entries from
-- multiple promotion pathways (promote_staging, reddit_scraper, reddit_public_scraper).
-- This allows .upsert(..., on_conflict="upc,date,source") to work correctly.

ALTER TABLE events
  ADD CONSTRAINT events_upc_date_source_unique UNIQUE (upc, date, source);
