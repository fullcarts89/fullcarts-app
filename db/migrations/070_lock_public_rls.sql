-- 070_lock_public_rls.sql
-- Phase 1 (data protection): close the anon REST bulk-extraction surface.
--
-- WHY THIS EXISTS
-- ---------------
-- The Supabase anon key is public by design, and 002_rls_policies.sql granted
-- anon SELECT on the data tables via `USING (true)`. That left the PostgREST
-- endpoint wide open:
--     GET https://<ref>.supabase.co/rest/v1/published_changes?select=*
-- returns the entire database as paginated JSON to anyone with the anon key.
--
-- A read-path audit (2026-05-25) confirmed the Next.js frontend reads ALL data
-- through the service_role client (web/src/lib/supabase/admin.ts), which has
-- BYPASSRLS and is unaffected by anything below. The two anon-key clients
-- (client.ts, server.ts) are imported by NOTHING. middleware.ts uses the anon
-- key only for auth.getUser() (auth schema), not public-table reads. So locking
-- the anon/authenticated roles out of schema `public` breaks no frontend path.
--
-- TWO NON-OBVIOUS GOTCHAS this migration must handle (a base-table RLS change
-- alone would be a false fix):
--   1. Postgres VIEWS run as their owner (postgres) and BYPASS RLS. None of the
--      ~24 public views use security_invoker, so tightening base-table RLS would
--      NOT stop `GET /rest/v1/brand_index?select=*` from dumping the same data.
--   2. SECURITY DEFINER functions (merge_entities, set_entity_field,
--      set_entity_retracted, get_product_history, dashboard_stats, ...) are
--      EXECUTE-granted to anon by Supabase defaults, so anon can call destructive
--      admin RPCs and bulk read-RPCs via /rest/v1/rpc/<fn>.
--
-- The fix therefore works at the ROLE/GRANT layer (covers tables, views, AND
-- routines at once) and keeps RLS as defense-in-depth underneath.
--
-- Deploy via Supabase SQL Editor (you run as `postgres`) or the Management API
-- (POST /v1/projects/{ref}/database/query, set a User-Agent header).

-- ============================================================
-- PART A — Remove the misleading "anyone can read" RLS policies
-- ------------------------------------------------------------
-- After Part B, anon/authenticated lose the table GRANT entirely, so these
-- policies are never even consulted. We still drop them so the schema's RLS
-- honestly reflects intent and stays deny-by-default if a GRANT is ever
-- re-added by mistake. The service_role "...manages..." FOR ALL policies from
-- 002 are intentionally left in place — that is what the frontend uses.
-- ============================================================

DROP POLICY IF EXISTS "Anyone can read products"        ON product_entities;
DROP POLICY IF EXISTS "Anyone can read variants"        ON pack_variants;
DROP POLICY IF EXISTS "Anyone can read observations"    ON variant_observations;
DROP POLICY IF EXISTS "Public reads non-retracted changes" ON published_changes;
DROP POLICY IF EXISTS "Anyone can read evidence files"  ON evidence_files;

-- ============================================================
-- PART B — Revoke the public REST surface from anon + authenticated
-- ------------------------------------------------------------
-- REVOKE ... ON ALL TABLES covers base tables AND views (views are relations
-- for GRANT purposes; we have no materialized views). ON ALL ROUTINES covers
-- every function/RPC. This is the single lever that actually closes both the
-- view-bypass leak and the anon-callable-RPC hole.
--
-- service_role is NOT touched here (it has BYPASSRLS + its own grants), so the
-- frontend keeps full access. The `postgres` / `supabase_admin` roles are
-- likewise unaffected.
-- ============================================================

REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL ROUTINES  IN SCHEMA public FROM anon, authenticated;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM anon, authenticated;

-- Keep future migration-created objects locked by default (applies to objects
-- created by the role running migrations, i.e. postgres).
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES    FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON ROUTINES  FROM anon, authenticated;
ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON SEQUENCES FROM anon, authenticated;

-- ============================================================
-- PART C — Preserve what RLS itself needs
-- ------------------------------------------------------------
-- The reviewer/admin RLS policies on raw_items/claims/change_candidates/etc.
-- call public.user_role() during policy evaluation. That function must remain
-- EXECUTE-able by the evaluating roles or those policies error out. user_role()
-- only reads the request JWT claims — it exposes no table data.
-- ============================================================

GRANT EXECUTE ON FUNCTION public.user_role() TO anon, authenticated;

-- ============================================================
-- PART D — Cheap belt-and-suspenders query-cost caps
-- ------------------------------------------------------------
-- Bounds runaway queries even if a future policy/grant is loosened. anon is
-- fully denied above, but this protects the authenticated role too and costs
-- nothing. (PostgREST row caps via pgrst.db_max_rows are deliberately left for
-- a separate, reload-coupled change — anon returning zero rows makes them moot.)
-- ============================================================

ALTER ROLE anon          SET statement_timeout = '5s';
ALTER ROLE authenticated SET statement_timeout = '10s';

-- ============================================================
-- POST-DEPLOY VERIFICATION (run from a shell, NOT in SQL)
-- ------------------------------------------------------------
-- With the ANON key, every one of these must return [] or a permission error:
--   curl "$URL/rest/v1/published_changes?select=*"  -H "apikey: $ANON" -H "Authorization: Bearer $ANON"
--   curl "$URL/rest/v1/product_entities?select=*"    -H "apikey: $ANON" -H "Authorization: Bearer $ANON"
--   curl "$URL/rest/v1/brand_index?select=*"         -H "apikey: $ANON" -H "Authorization: Bearer $ANON"   -- view
--   curl "$URL/rest/v1/skimpflation_events?select=*" -H "apikey: $ANON" -H "Authorization: Bearer $ANON"   -- view
--   curl -X POST "$URL/rest/v1/rpc/merge_entities" -H "apikey: $ANON" -H "Authorization: Bearer $ANON" \
--        -H "Content-Type: application/json" -d '{}'                                                       -- must be denied
-- Then load fullcarts.org and confirm every public page still renders (it uses
-- service_role, so it should be unaffected). Storage-served evidence images are
-- unaffected — the `evidence` bucket is object-level public, independent of the
-- evidence_files TABLE locked above.

-- ============================================================
-- ROLLBACK (paste into SQL Editor to fully revert this migration)
-- ------------------------------------------------------------
-- GRANT SELECT ON ALL TABLES   IN SCHEMA public TO anon, authenticated;
-- GRANT EXECUTE ON ALL ROUTINES IN SCHEMA public TO anon, authenticated;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT  ON TABLES   TO anon, authenticated;
-- ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT EXECUTE ON ROUTINES TO anon, authenticated;
-- ALTER ROLE anon          RESET statement_timeout;
-- ALTER ROLE authenticated RESET statement_timeout;
-- CREATE POLICY "Anyone can read products"     ON product_entities    FOR SELECT USING (true);
-- CREATE POLICY "Anyone can read variants"     ON pack_variants       FOR SELECT USING (true);
-- CREATE POLICY "Anyone can read observations" ON variant_observations FOR SELECT USING (true);
-- CREATE POLICY "Public reads non-retracted changes" ON published_changes FOR SELECT USING (NOT is_retracted);
-- CREATE POLICY "Anyone can read evidence files" ON evidence_files     FOR SELECT USING (true);
