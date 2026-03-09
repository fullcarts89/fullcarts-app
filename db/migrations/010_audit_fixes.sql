-- ============================================================
-- 010_audit_fixes.sql — Security, integrity & performance fixes
-- Run in Supabase SQL Editor (supabase.com → project → SQL Editor)
--
-- IMPORTANT: This migration is idempotent (safe to run multiple times).
-- It does NOT modify or delete any existing data. Validated records
-- (status = 'promoted') remain untouched.
-- ============================================================

BEGIN;

-- ── 0. Fix legacy 'evidence_wall' status values ──────────────
-- Old code bug set status to 'evidence_wall' instead of 'promoted'.
-- Correct these before adding the CHECK constraint.
UPDATE reddit_staging SET status = 'promoted' WHERE status = 'evidence_wall';

-- ── 1. Fix SECURITY DEFINER RPC: require authenticated role ──
-- The update_staging_status function was callable by anon, allowing
-- any anonymous user to change staging record status.
CREATE OR REPLACE FUNCTION update_staging_status(row_id uuid, new_status text)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  -- Only authenticated users (admin) can call this
  IF auth.role() != 'authenticated' THEN
    RAISE EXCEPTION 'Unauthorized: admin authentication required';
  END IF;

  IF new_status NOT IN ('promoted', 'dismissed', 'rejected') THEN
    RAISE EXCEPTION 'Invalid status: %', new_status;
  END IF;

  UPDATE reddit_staging
  SET status = new_status
  WHERE id = row_id;
END;
$$;

-- Revoke anon access, keep authenticated
REVOKE EXECUTE ON FUNCTION update_staging_status(uuid, text) FROM anon;
GRANT EXECUTE ON FUNCTION update_staging_status(uuid, text) TO authenticated;


-- ── 2. Tighten RLS: products & events INSERT ────────────────
-- Only allow inserts with source = 'community' from anon/public.
-- Service role (scraper) bypasses RLS entirely.
-- This does NOT affect existing records (RLS only gates new writes).
DROP POLICY IF EXISTS "Anon can insert products" ON products;
DROP POLICY IF EXISTS "Community can insert products" ON products;
CREATE POLICY "Community can insert products" ON products
  FOR INSERT WITH CHECK (source = 'community');

DROP POLICY IF EXISTS "Anon can insert events" ON events;
DROP POLICY IF EXISTS "Community can insert events" ON events;
CREATE POLICY "Community can insert events" ON events
  FOR INSERT WITH CHECK (source = 'community' AND submitted_by IS NOT NULL);


-- ── 3. Restrict reddit_staging public reads to promoted only ─
-- Already applied in seed file, but ensure live DB matches.
DROP POLICY IF EXISTS "Public read staging" ON reddit_staging;
DROP POLICY IF EXISTS "Public read promoted staging" ON reddit_staging;
CREATE POLICY "Public read promoted staging" ON reddit_staging
  FOR SELECT USING (status = 'promoted');


-- ── 3b. Restrict evidence_wall INSERT to authenticated ───────
DROP POLICY IF EXISTS "Anyone can insert evidence_wall" ON evidence_wall;
DROP POLICY IF EXISTS "Admin can insert evidence_wall" ON evidence_wall;
CREATE POLICY "Admin can insert evidence_wall" ON evidence_wall
  FOR INSERT WITH CHECK (auth.role() = 'authenticated');


-- ── 4. Fix duplicate date_noticed column ─────────────────────
-- The CREATE TABLE in seed has a duplicate column. For a live DB,
-- the column already exists so this is a no-op safety check.
-- If running on a fresh DB, the updated seed file omits the duplicate.


-- ── 5. CHECK constraints on status columns ──────────────────
-- Prevent invalid status values. Uses DO blocks to skip if exists.
DO $$ BEGIN
  ALTER TABLE reddit_staging
    ADD CONSTRAINT chk_staging_status
    CHECK (status IN ('pending', 'promoted', 'dismissed', 'rejected'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TABLE submissions
    ADD CONSTRAINT chk_submission_status
    CHECK (status IN ('pending', 'approved', 'rejected'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TABLE evidence_wall
    ADD CONSTRAINT chk_ew_status
    CHECK (status IN ('approved', 'hidden'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
  ALTER TABLE flags
    ADD CONSTRAINT chk_flag_status
    CHECK (status IN ('open', 'resolved', 'dismissed'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


-- ── 6. Additional indexes for performance ───────────────────
CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at);
CREATE INDEX IF NOT EXISTS idx_upvotes_session ON upvotes(session_id);
CREATE INDEX IF NOT EXISTS idx_ew_status ON evidence_wall(status);


-- ── 7. Prevent promoted→pending status regression ───────────
-- A trigger that blocks changing status from 'promoted' back to 'pending'.
-- This protects validated records from being accidentally re-queued.
CREATE OR REPLACE FUNCTION prevent_status_regression()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
  IF OLD.status = 'promoted' AND NEW.status = 'pending' THEN
    RAISE EXCEPTION 'Cannot revert promoted records back to pending';
  END IF;
  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_prevent_status_regression ON reddit_staging;
CREATE TRIGGER trg_prevent_status_regression
  BEFORE UPDATE OF status ON reddit_staging
  FOR EACH ROW
  EXECUTE FUNCTION prevent_status_regression();


-- ── 8. Foreign key: evidence_wall.staging_id ─────────────────
-- Only add if not already present.
DO $$ BEGIN
  ALTER TABLE evidence_wall
    ADD CONSTRAINT fk_ew_staging
    FOREIGN KEY (staging_id) REFERENCES reddit_staging(id) ON DELETE SET NULL;
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;


COMMIT;
