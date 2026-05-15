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
# bls_shrinkflation, fred_cpi, open_prices, upc_backfill, wayback

# Wayback has extra flags
python -m pipeline wayback --url URL --brand BRAND --product NAME [--upc UPC]

# Pipeline scripts (not scrapers)
python3 pipeline/scripts/promote_claims.py [--limit N] [--dry-run]
python3 -m pipeline.scripts.dedup_entities [--auto] [--dry-run]
python3 -m pipeline.scripts.auto_approve_claims [--threshold 80] [--dry-run]
python3 -m pipeline.scripts.backfill_entity_images [--limit N] [--dry-run]
python3 -m pipeline.scripts.activate_variants [--dry-run]
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
- `claims` — AI-extracted assertions with confidence scores, status workflow: pending → approved → matched
- `product_entities` — Canonical products (brand + name), full-text search via tsvector
- `pack_variants` — Specific SKUs with UPC, linked to entities. `is_active=true` enables weekly monitoring
- `variant_observations` — Time-series size/price snapshots
- `published_changes` — Public-facing shrinkflation records with evidence
- `fred_cpi_data`, `bls_shrinkflation` — Economic indicator tables (not in raw_items)
- `usda_products`, `usda_product_history` — USDA FDC product snapshots across 7 releases

### Database migrations

SQL migrations in `db/migrations/` numbered `001_` through `050_`. Deploy manually via Supabase SQL Editor (or via the Management API with a PAT). Views in `043_rewrite_views_new_schema.sql` and `049_insight_views.sql` power the frontend. Migration `050_event_dedup.sql` added `published_changes.evidence_count` + a dedup index.

### Design reference

`web/public/mockups/brands-cadbury.html` is the locked visual reference for the future `/brands/[name]` Next.js route. Uses the existing `FULLCARTS_DESIGN_EXPORT.md` system (dark graphite + Space Grotesk + JetBrains Mono + alert red). Deploys to `/mockups/brands-cadbury.html` once Vercel picks up the merge.

### GitHub Actions

17 workflows in `.github/workflows/` run scrapers on schedule (daily/weekly/monthly/quarterly). Key ones:
- `pipeline_promote.yml` — Daily 12:00 UTC: auto-decline junk → auto-approve high-confidence claims (threshold 90 + hard filters) → promote → backfill entity images. Markdown summaries in job output.
- `pipeline_extraction.yml` — Daily 10:00 UTC: AI claim extraction from `raw_items` (Claude Haiku) + nightly vision enrichment
- `pipeline_reddit.yml` / `pipeline_news.yml` — Daily/12h: ingest new data
- `phase1_execution.yml` — Manual: run individual Phase 1 data-credibility scripts (event dedup, entity dedup, etc.)
