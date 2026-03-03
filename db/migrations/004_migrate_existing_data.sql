-- ============================================================
-- Migration 004: Backfill product_versions + change_events
-- from existing events table data.
--
-- This is a ONE-TIME migration. Run after 001-003.
-- It converts the existing events table rows into the new
-- longitudinal product_versions + change_events format.
-- ============================================================

BEGIN;

-- Step 1: Create product_versions from existing events
-- Each event has old_size → new_size. We create TWO versions per event:
-- one for the "before" state, one for the "after" state.

-- Insert "before" versions (the old_size before the change)
INSERT INTO product_versions (product_upc, observed_date, size, unit, price, source, notes, created_by)
SELECT
  e.upc,
  -- Approximate the "before" date as 1 year before the event
  (e.date - interval '1 year')::date,
  e.old_size,
  COALESCE(e.unit, p.unit, 'oz'),
  e.price_before,
  COALESCE(e.source, 'community'),
  'Backfilled from events table (before state)',
  'migration_004'
FROM events e
JOIN products p ON p.upc = e.upc
WHERE e.old_size IS NOT NULL
ON CONFLICT (product_upc, observed_date, source) DO NOTHING;

-- Insert "after" versions (the new_size after the change)
INSERT INTO product_versions (product_upc, observed_date, size, unit, price, source, notes, created_by)
SELECT
  e.upc,
  e.date,
  e.new_size,
  COALESCE(e.unit, p.unit, 'oz'),
  e.price_after,
  COALESCE(e.source, 'community'),
  'Backfilled from events table (after state)',
  'migration_004'
FROM events e
JOIN products p ON p.upc = e.upc
WHERE e.new_size IS NOT NULL
ON CONFLICT (product_upc, observed_date, source) DO NOTHING;


-- Step 2: Run change detection to generate change_events from the new versions
SELECT detect_all_changes();


-- Step 3: Mark products with multiple shrinkflation events as repeat offenders
UPDATE products SET repeat_offender = true
WHERE upc IN (
  SELECT product_upc
  FROM change_events
  WHERE is_shrinkflation = true
  GROUP BY product_upc
  HAVING count(*) > 1
);

COMMIT;
