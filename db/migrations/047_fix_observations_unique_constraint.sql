-- Fix variant_observations unique constraint so ON CONFLICT works with PostgREST.
--
-- The original index used COALESCE(retailer, '') — a functional expression index.
-- supabase-py upsert() ON CONFLICT only accepts plain column names and cannot
-- reference functional expression indexes, causing:
--   "there is no unique or exclusion constraint matching the ON CONFLICT specification"
--
-- Fix: drop the functional index and add a plain UNIQUE constraint on the same
-- columns that the scrapers already specify in their on_conflict= calls.
--
-- NULLS NOT DISTINCT (PostgreSQL 15+) preserves the COALESCE semantics: two rows
-- with retailer IS NULL and identical (variant_id, observed_date, source_type)
-- are treated as duplicates, matching the behaviour of the old functional index.

DROP INDEX IF EXISTS idx_observations_unique;

ALTER TABLE variant_observations
    ADD CONSTRAINT variant_observations_unique
    UNIQUE NULLS NOT DISTINCT (variant_id, observed_date, source_type, retailer);
