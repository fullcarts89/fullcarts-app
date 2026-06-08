-- Migration 072: pre-launch security lockdown
--
-- Closes two classes of anon-key exploit found in the pre-launch audit. The
-- public site ships the Supabase *anon* key in the browser bundle, so anything
-- the anon role can reach via PostgREST is reachable by anyone on the internet.
-- Every admin mutation in the web app goes through the *service-role* client
-- (web/src/lib/supabase/admin.ts), which has BYPASSRLS and is unaffected by the
-- changes below. So these are pure lockdowns with no impact on the app.
--
--   (1) SECURITY DEFINER mutation RPCs were created without a REVOKE, so
--       Postgres defaulted EXECUTE to PUBLIC (incl. anon). An attacker could
--       call /rest/v1/rpc/merge_entities (etc.) directly with the public anon
--       key and merge / retract / rebrand / reassign any entity, bypassing the
--       isAdminRequest() check in the route handlers entirely.
--
--   (2) Several tables shipped with RLS disabled. A public-schema table with
--       RLS off is fully readable AND writable through the anon key. These are
--       all internal / admin / audit tables read by the app exclusively through
--       the service-role client, so enabling RLS with a service-role-only
--       policy denies anon without touching app behaviour.
--
-- Pattern mirrors the existing hardening in 010_audit_fixes.sql (update_staging
-- _status) and the RLS template in 040_fred_cpi_data.sql.

BEGIN;

-- ── (1) Revoke anon EXECUTE on the SECURITY DEFINER mutation RPCs ─────────────
-- These are the entity-mutation functions exposed via PostgREST /rpc/. The web
-- app calls them through the service-role client, which is unaffected by the
-- revoke. Trigger functions (trg_retract_orphaned_entity, fn_claim_status_log)
-- and read-only functions (dashboard_stats) are not directly RPC-callable in a
-- harmful way and are left as-is.

REVOKE EXECUTE ON FUNCTION set_entity_field(uuid, text, text, text)            FROM anon, PUBLIC;
REVOKE EXECUTE ON FUNCTION merge_entities(uuid, uuid, text)                    FROM anon, PUBLIC;
REVOKE EXECUTE ON FUNCTION set_entity_retracted(uuid, boolean)                 FROM anon, PUBLIC;
REVOKE EXECUTE ON FUNCTION reassign_events_by_size(uuid, uuid, numeric, numeric, text, text) FROM anon, PUBLIC;

-- ── (2) Enable RLS on the tables that shipped without it ─────────────────────
-- Helper: enable RLS + a single service-role-ALL policy (idempotent). Anon gets
-- no permissive policy, so it is denied SELECT/INSERT/UPDATE/DELETE entirely.

DO $$
DECLARE
    t text;
    tables text[] := ARRAY[
        'data_quality_flags',   -- 063: admin review queue
        'entity_edit_log',      -- 065: inline-edit audit trail
        'entity_merge_log',     -- 065: merge audit trail
        'claim_status_log',     -- 064: claim-status audit trail
        'event_reassign_log',   -- 070: event-reassign audit trail
        'usda_products',        -- 026: USDA FDC snapshots (read via service role)
        'usda_product_history', -- 027: USDA history (read via service role)
        'discovery_catalog'     -- 045: pipeline discovery queue (internal)
    ];
BEGIN
    FOREACH t IN ARRAY tables LOOP
        IF to_regclass('public.' || t) IS NULL THEN
            RAISE NOTICE 'skip %, table does not exist', t;
            CONTINUE;
        END IF;
        EXECUTE format('ALTER TABLE public.%I ENABLE ROW LEVEL SECURITY', t);
        EXECUTE format('DROP POLICY IF EXISTS "Service role full access %1$s" ON public.%1$I', t);
        EXECUTE format(
            'CREATE POLICY "Service role full access %1$s" ON public.%1$I '
            'FOR ALL USING (auth.role() = ''service_role'')', t);
    END LOOP;
END $$;

-- ── (3) app_settings — legacy admin-password-hash store ──────────────────────
-- No migration creates this table; it predates the migration series and may or
-- may not exist in the live DB. The current Next.js app does NOT use it (admin
-- auth reads ADMIN_PASSWORD_HASH from env). Only the retired standalone
-- fullcarts.html read it via the anon key. If it still exists, lock it so the
-- anon role can never read the hash.

DO $$
BEGIN
    IF to_regclass('public.app_settings') IS NOT NULL THEN
        EXECUTE 'ALTER TABLE public.app_settings ENABLE ROW LEVEL SECURITY';
        EXECUTE 'DROP POLICY IF EXISTS "Service role full access app_settings" ON public.app_settings';
        EXECUTE 'CREATE POLICY "Service role full access app_settings" ON public.app_settings '
                'FOR ALL USING (auth.role() = ''service_role'')';
    ELSE
        RAISE NOTICE 'app_settings does not exist — nothing to lock';
    END IF;
END $$;

COMMIT;
