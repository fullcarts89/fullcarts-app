# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Python Compatibility

Target runtime is Python 3.9 (macOS system Python). Never use:
- `X | Y` union type syntax (use `Optional[X]`, `Union[X, Y]`)
- `dict[K, V]`, `list[T]`, `set[T]` in annotations (use `Dict`, `List`, `Set` from typing)
Always grep the entire project for these patterns before committing.

## Supabase

- Project: ntyhbapphnzlariakgrw
- URL: https://ntyhbapphnzlariakgrw.supabase.co
- Site: https://fullcarts.org
- Admin login: long-press header logo -> password prompt (hash in app_settings table)

## Commands

### Pipeline (data ingestion)

All scrapers use the unified CLI. Requires `SUPABASE_KEY` (service_role) and `SUPABASE_URL` env vars.

```bash
pip install -r pipeline/requirements.txt

# Run any scraper
python -m pipeline <command> [--dry-run]

# Common commands: reddit_recent, news_rss, gdelt, off_daily, off_discovery,
# kroger, kroger_discovery, walmart, walmart_discovery, usda_quarterly,
# bls_shrinkflation, fred_cpi, open_prices, upc_backfill, wayback,
# google_trends, consumer_reports

# Wayback has extra flags
python -m pipeline wayback --url URL --brand BRAND --product NAME [--upc UPC]

# Pipeline scripts (not scrapers)
python3 pipeline/scripts/promote_claims.py [--limit N] [--dry-run]
python3 -m pipeline.scripts.dedup_entities [--auto] [--dry-run]
python3 -m pipeline.scripts.auto_approve_claims [--threshold 80] [--dry-run]
python3 -m pipeline.scripts.backfill_entity_images [--limit N] [--dry-run] [--no-off-api]
python3 -m pipeline.scripts.activate_variants [--dry-run]
python3 -m pipeline.scripts.promote_skimpflation [--dry-run] [--min-score 5]
python3 -m pipeline.scripts.wikidata_manufacturer_backfill [--limit N] [--dry-run]
python3 -m pipeline.scripts.match_consumer_reports [--dry-run]
```

### Pipeline tests

```bash
cd pipeline && python -m pytest tests/
python -m pytest tests/test_claim_parsing.py  # single test file
python -m pytest tests/test_claim_parsing.py::test_name -v  # single test
```

### Web frontend (Next.js)

```bash
cd web
npm install  # or pnpm install
npm run dev    # dev server
npm run build  # production build
npm run lint   # eslint
```

Requires `web/.env.local` with `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, and `SUPABASE_SERVICE_ROLE_KEY`.

## Architecture

### Data flow

```
Scrapers (10+ sources) → raw_items table (immutable evidence locker)
  → extract_claims.py (Claude Haiku AI extraction) → claims table
  → admin review (approve/discard) → promote_claims.py
  → product_entities → pack_variants → variant_observations
  → change_candidates → published_changes (public record)
```

### Two pipeline generations (coexist in same repo)

- **Legacy** (`backend/`, `reddit_public_scraper.py`, `reddit_scraper.py`): Old scrapers writing to `reddit_staging` → `products` table with synthetic `REDDIT-` UPCs. Still present but superseded.
- **Current** (`pipeline/`): Modern scraper framework with `BaseScraper` base class, cursor-based pagination, `raw_items` as canonical store. All new work goes here.

### Pipeline scraper pattern

All scrapers inherit from `pipeline/scrapers/base.py:BaseScraper` and implement:
- `fetch(cursor, dry_run)` → list of items
- `store(items)` → writes to Supabase (default: `raw_items` table)
- `next_cursor(items, prev_cursor)` → cursor state for resumption

Cursor state persists in `scraper_state` table. Config lives in `pipeline/config.py`.

### Supabase client tiers (web frontend)

- `web/src/lib/supabase/client.ts` — Browser client (anon key, RLS-enforced)
- `web/src/lib/supabase/server.ts` — Server Component client (anon key + cookie session)
- `web/src/lib/supabase/admin.ts` — Service role client (bypasses RLS, server-only)

### Key database tables

- `raw_items` — Immutable raw payloads from all sources, deduped by `(source_type, source_id)`
- `claims` — AI-extracted assertions with confidence scores. Status workflow: `pending` → admin approves → `matched` → daily `promote_claims` cron either keeps `matched` (claim originated a new event) or flips to `evidence` (claim folded into an existing event during dedup). Admins also flip claims to `evidence` directly when tagging them for an evidence-wall channel (Skimpflation / So Smol / etc. — recognisable by non-empty `evidence_tags`). The `/admin/claims` Evidence tab filters out fold-ins via an `evidence_tags IS NOT NULL` predicate so the two senses of `evidence` don't conflate in the review queue. `discarded` is the terminal "junk" bucket. The legacy `approved` and `unmatched` statuses are retired; nothing writes them.
- `product_entities` — Canonical products (brand + name), full-text search via tsvector
- `pack_variants` — Specific SKUs with UPC, linked to entities. `is_active=true` enables weekly monitoring
- `variant_observations` — Time-series size/price snapshots
- `published_changes` — Public-facing shrinkflation records with evidence
- `fred_cpi_data`, `bls_shrinkflation` — Economic indicator tables (not in raw_items)
- `usda_products`, `usda_product_history` — USDA FDC product snapshots across 7 releases

### Database migrations

SQL migrations in `db/migrations/` numbered `001_` through `067_`. Deploy manually via Supabase SQL Editor or via the Management API with a PAT (`POST /v1/projects/{ref}/database/query`; **set a `User-Agent` header** or Cloudflare returns 1010). Views in `043_rewrite_views_new_schema.sql` and `049_insight_views.sql` plus newer per-page views power the frontend. Notable recent additions:

- `050_event_dedup.sql` — `published_changes.evidence_count` + dedup index on `(entity_id, size_before, size_after)`
- `051_event_evidence_summary_view.sql` — `event_evidence_summary` view, used by `/brands/[name]` evidence trail
- `052_brand_index_view.sql` + `053_brand_index_primary_category.sql` — `brand_index` view (1,167 rows), used by `/brands` index page; includes per-brand thumbnail, worst delta, primary category
- `054_product_index_view.sql` — `product_index` view (per-entity rollup), used by `/products` index page
- `055_published_changes_skimpflation.sql` — relaxes size_* / candidate_id NOT NULL, adds `skimp_score` + `nutrient_deltas` columns + `skimpflation_events` view; rewrites `event_evidence_summary` to exclude skimpflation rows so size-focused views stay clean
- `056_corporate_tree.sql` — `corporate_tree` view (per-manufacturer rollup with top-3 child brands as a JSONB array), used by /insights "Who actually owns these brands" section. Empty until Wikidata backfill runs
- `057_google_trends_data.sql` — `google_trends_data` table, drives the fourth line on the /insights macro chart. Refreshed monthly via `pipeline_google_trends.yml`
- `058_consumer_reports_findings.sql` — `consumer_reports_findings` table for structured CR citations. Refreshed monthly via `pipeline_consumer_reports.yml`. Powers the "Press coverage" section on `/products/[id]`
- `060_claims_status_discipline.sql` + `066_rollback_merged_status.sql` — 060 carved a `merged` value out of `evidence`; 066 reverted that (UI now filters the Evidence tab by `evidence_tags IS NOT NULL` instead — see `web/src/app/admin/claims/page.tsx`). 066 keeps the soft `status='matched' ⇒ matched_entity_id NOT NULL` invariant that 060 introduced
- `061_published_changes_sanity.sql` — auto-retracts size-ratio violators (1L→900L class of AI unit-parse errors) via the in-place `is_retracted` columns and installs a CHECK constraint on `size_after / size_before ∈ [0.05, 5.0]` (retracted rows exempted — they're the trash bin). `promote_claims.sane_size_ratio()` mirrors the bounds so the daily cron rejects violators before insert
- `062_entity_retraction.sql` — `product_entities.is_retracted` flag + `set_entity_retracted()` RPC (cascades retract to all the entity's `published_changes`). Rebuilds `brand_index` and `dashboard_stats()` to exclude retracted entities; closes a pre-existing leak where `event_evidence_summary` didn't filter `pc.is_retracted`. Powers `/admin/entities`. (Renumbered from `054_` during PR #75 rebase to clear collision with `054_product_index_view.sql`.)
- `063_data_quality_flags.sql` — `data_quality_flags` soft-flag quarantine table. Detectors in `promote_claims` (short_brand) and `cleanup_stuck_matched` (stuck_approved_claim) write here instead of mutating suspect rows. Partial unique index makes the writes idempotent across cron runs. `pipeline/lib/data_quality_flags.raise_flag()` is the writer helper
- `064_claim_status_audit_log.sql` — `claim_status_log` append-only audit trail + AFTER UPDATE trigger on `claims.status`. Future bulk-status drift bugs (the cleanup_stuck_matched regression class) surface as visible group rows instead of invisible silent updates
- `065_entity_edit_merge_logs.sql` — Phase 2D steps 2+4. Adds `entity_edit_log` + `set_entity_field()` RPC (single-field inline edit with audit trail); `entity_merge_log` + `merge_entities()` RPC (all-or-nothing merge of source→target with claim/event/variant move counts logged). Powers the new edit / merge buttons on `/admin/entities`
- `067_event_evidence_richer_sources.sql` — extends `event_evidence_summary` with `author` (Reddit) and `body_excerpt` (Reddit selftext / GDELT socialdescription / news description, first 240 chars). The per-source row on `/products/[id]` + `/brands/[name]` now shows a thumb + author + excerpt + an admin-only "Inspect raw payload" expander backed by `/api/admin/source-payload`

### Web routes (Next.js App Router)

| Route | Type | Notes |
|---|---|---|
| `/` | Static + ISR 1h | Live homepage. Hero, counters, "Just documented" sidecar, methodology, Brand of the Week, Most Active, Recent Shrinks, 7-tag evidence grid. |
| `/brands` | Static + ISR 1h | All 1,167 brands. Severity tiers + category chips + search. Pre-builds at deploy. |
| `/brands/[name]` | SSG + ISR 1h | Per-brand scorecard. 20 brands pre-built; rest lazy. Includes TimelineExplorer (clickable year chart + cap-to-5-per-year events). |
| `/products/[id]` | SSG + ISR 1h | Per-product scorecard. Top 30 by event count pre-built; rest lazy. Hero, SVG step-chart trajectory, change-history accordion, retailers grid (Kroger/Walmart/OFF/Open Prices), related-products rail. |
| `/insights` | Static + ISR 1h | Macro insights. 8 sections: hero counters, BLS headline + news, three-line trend chart (events + BLS + CPI), category bars, repeat offenders, skimpflation leaderboard, news feed, restoration corner. |
| `/about` | Static | Mission, methodology, full source list. The "Submit a tip" section is now a CTA linking to `/submit` (the embedded `TipForm` was retired). Contact `fullcartsinfo@gmail.com`. |
| `/products` | Static + ISR 1h | All entities with at least one shrink event. Severity tiers + category chips + brand-or-name search, mirroring `/brands`. |
| `/submit` | Static | Public community submission page. Structured `multipart/form-data` form (brand/product/old+new size/prices/description + **required evidence**) → `POST /api/submit`. **Evidence is mandatory: a link, one or more photos, or both** (up to 4 photos — e.g. a before & after pair). Photos are downscaled/compressed client-side (canvas → JPEG, ~1600px, with a combined-size guard) to stay under Vercel's request-body limit, uploaded server-side (service role) to the public `claim-images` bucket under `community/<id>/`. All paths are stored in `raw_payload.image_storage_paths` and the first is mirrored to `claims.image_storage_path` (so single-image consumers keep working) — the `/admin/claims` card renders a thumbnail grid when there are multiple, via the same `ClaimImage` component used for scraped evidence. Each submission writes a `raw_items` evidence anchor (`source_type='community_tip'`) + a `pending` `claims` row (`extractor_version='community-v1'`) pointing at it — satisfying `claims.raw_item_id NOT NULL`. From there it's an ordinary pending claim that rides the normal approve → promote pipeline; no new claim status, no migration. Surfaced in `/admin/claims` via a pink "Community" badge + source filter (`source=community_tip`) + a pending-count banner linking to the filtered, newest-first view ("top of queue"). Confidence is stamped a modest `overall: 0.5` so the threshold-90 `auto_approve_claims` cron never publishes a submission unreviewed. Abuse defenses on `/api/submit`: IP hashing, 60 s per-session dedup (keyed on the payload `session_id`), 6 MB photo backstop, image-mime allowlist. The legacy `tips` table + `/api/tips` + `about/_components/TipForm.tsx` are retired (left in place, dormant). |
| `/admin/claims` | SSR | Claim review queue (pending/matched/evidence/discarded). Evidence tab filters by `evidence_tags` non-empty so dedup fold-ins (also at `status='evidence'`) stay out of the tab without needing a separate status value. Long-press the public homepage logo to reveal the password form. Sets `admin_session` cookie checked by `middleware.ts`. |
| `/admin/entities` | SSR | Entity browser. Paginated table with brand+name search, status filter (active/retracted/all), per-row retract toggle. Retracting cascades to `published_changes`. Cells are click-to-edit for brand / canonical_name / category / manufacturer (writes via `set_entity_field` RPC, logged to `entity_edit_log`). Each row has a `merge⇒` button (PR #103: debounced entity search picker — type a brand/name, pick the target, no UUIDs required; UUID paste still works as fallback) for moving everything into another entity (`merge_entities` RPC + `entity_merge_log`). Retracted rows also expose a `↺ pending` button that resets all attached claims back to `status='pending'`. Page-level `Merge brand →` button (PR #104/#105) opens a modal for bulk-rebrand: every active entity carrying brand `X` gets set to brand `Y`, audited per-row in `entity_edit_log` (so per-entity rollback works via click-to-edit); modal stays open after submit so you can chain rebrands. |
| `/admin/duplicates` | SSR | Two sections. (1) **Exact-match** (PR #91): server-side groups non-retracted entities by `(brand, slugify(canonical_name))`, per-row Merge + "Merge N selected" batch toolbar. (2) **Size-Signature** (PR #101): groups by `(brand, size_before, size_after, size_unit)` so AI-extracted name drift like "Bottle"/"Gatorade Bottle"/"Sports Drink" collapses under one candidate; ✓ name match / ⚠ names diverge hint. Each member row surfaces its backing source URLs (reddit/news/gdelt) pulled from `event_evidence_summary`. Three actions per row: (a) `Merge into target` (radio + button → `POST /api/admin/merge-pair` route handler — deliberately NOT a server action so the page stays anchored after submit, see Known gotchas); (b) click any size chip → `Extract events at this size to another entity` (PR #102: `reassign_events_by_size` RPC, audited in `event_reassign_log` from migration 070); (c) per-source `↩ send to pending` red button (PR #102: calls existing `/api/admin/retract-event` to retract the event + flip backing claims back to `status='pending'`). |
| `/admin/quality-flags` | SSR | Unified review queue backed by the `data_quality_flags` table (migration 063). Filters by status (open / resolved / all), flag_kind, severity. Per-row Resolve (with optional note) + Reopen. Sticky toolbar with bulk Resolve. Target link routes to the appropriate fix surface (`/products/<entity>`, `/admin/claims`, `/admin/entities`). All open flags share the partial unique index on `(flag_kind, target_id)` so detectors stay idempotent across cron runs. |

Shared nav lives at `web/src/components/SiteNav.tsx` (client component, uses `usePathname` for active detection). All public routes render `<SiteNav />` once at the top of their JSX.

### Admin affordances on public pages

When the founder is signed in (long-press logo → `/admin/login` → password → 7-day `admin_session` cookie), a red **"↩ Send to pending"** button renders inside every expanded event-detail panel on `/products/[id]` (change-history accordion) and `/brands/[name]` (timeline). One click + confirm → `published_changes.is_retracted=true` for that event + every backing claim flipped to `status='pending'` with `matched_*` nulled. Routes: `POST /api/admin/retract-event`, `GET /api/admin/whoami` (existence check so non-admins see nothing). Helper: `web/src/lib/admin-auth.ts`. Component: `web/src/components/admin/RetractEventButton.tsx`.

### Design reference

Visual targets are committed alongside the routes that realised them:
- `web/public/mockups/brands-cadbury.html` → `/brands/[name]`
- `web/public/mockups/homepage.html` → `/`
- `web/public/mockups/products-cadbury-dairy-milk-mini-eggs.html` → `/products/[id]`
- `web/public/mockups/insights.html` → `/insights`

All use the `FULLCARTS_DESIGN_EXPORT.md` system (dark graphite + Space Grotesk + JetBrains Mono + alert red). New pages should match this aesthetic. Mockups stay in `web/public/mockups/` as historical references — useful when diffing the real page against the originally-approved design.

### GitHub Actions

20 workflows in `.github/workflows/` run scrapers on schedule (daily/weekly/monthly/quarterly). Key ones:
- `pipeline_promote.yml` — Daily 12:00 UTC: auto-decline junk → auto-approve high-confidence claims (threshold 90 + hard filters) → promote → backfill entity images. Markdown summaries in job output.
- `pipeline_extraction.yml` — Daily 10:00 UTC: AI claim extraction from `raw_items` (Claude Haiku) + nightly vision enrichment
- `pipeline_reddit.yml` / `pipeline_news.yml` — Daily/12h: ingest new data
- `phase1_execution.yml` — Manual: run individual Phase 1 data-credibility scripts (event dedup, entity dedup, etc.). Step 9/10 = `restore_matched_originators` dry-run / apply.

### Known gotchas

- **`/admin/claims` Evidence tab does not equal `status='evidence'`.** The DB bucket holds two unrelated row types: admin-tagged evidence-wall claims (Skimpflation / So Smol / etc., recognisable by non-empty `evidence_tags`) AND dedup fold-ins written by `promote_claims` (no `evidence_tags`). The tab disambiguates at the query layer by filtering on `evidence_tags IS NOT NULL AND evidence_tags <> '{}'`. **Do not solve future status-overload problems by adding new values to the `claims_status_check` constraint** — extend the UI filter instead. (See `feedback_no_new_claim_status_buckets.md` in the user's memory.)
- **`promote_claims.py` writes the originator's claim id into `change_candidates.supporting_claims[]` exactly once at candidate-create time.** Folded-in claims go to `published_changes.evidence_summary` instead. That asymmetry is what `cleanup_stuck_matched.py:108-130` (originator guard) and `restore_matched_originators.py` rely on to tell originators from duplicates.
- **`published_changes.brand` and `published_changes.product_name` are denormalized snapshots** copied from `product_entities` at promote_claims time. `/brands/[name]` joins events by `published_changes.brand` so any code path that mutates `product_entities.brand` or `canonical_name` MUST cascade to `published_changes`. Migration 071 wired this into `merge_entities()`, `reassign_events_by_size()`, and the merge-brand route; future mutation paths must continue the pattern. Sanity check that should always return 0: `SELECT COUNT(*) FROM published_changes pc JOIN product_entities pe ON pe.id = pc.entity_id WHERE pc.brand <> pe.brand OR pc.product_name <> pe.canonical_name`.
- **Next.js Server Actions auto-refresh the calling route on completion**, even without `revalidatePath`. This caused the page-jump bug on `/admin/duplicates` mid-triage. For admin mutations where session state must survive, use a **route handler** (`web/src/app/api/admin/*/route.ts`) called via `fetch` from the client — not a Server Action. The route handler can still call `revalidatePath` for OTHER routes (public ISR surfaces) without affecting the calling page. See `operational-server-actions-auto-refresh.md` in user memory + the `merge-pair` / `merge-brand` / `reassign-events-by-size` routes for the pattern.
