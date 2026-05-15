# FullCarts: Data → Insights → Content Plan

**Date:** May 12, 2026
**Last updated:** May 15, 2026
**Status:** Phase 1 complete and shipped. Data pipeline cleanups landed (event dedup, entity dedup, image fallbacks). Brand-page mockup mature; Phase 2 (real Next.js pages) is the next active workstream.

---

## Progress Tracker

### Phase 1: Make the Data Credible — ✅ COMPLETE

| Task | Status | Outcome |
|------|--------|---------|
| 1.1 Dedup audit | ✅ Shipped (#60) | Strict-mode dedup merged 707 obvious dupes (14,856 → 14,149). Per-brand fuzzy passes possible via `--fuzzy`. |
| 1.2 Image backfill | ✅ Shipped (#60) | `backfill_entity_images.py` paginates correctly; daily cron in `pipeline_promote.yml`. 1,108 entity images populated; coverage now 85%+ for brands with news coverage. |
| 1.3 BLS CPI fix | ✅ Live | Re-run produced 825 CPI + 134 counts rows in `bls_shrinkflation`. NULL R-CPI-SC is a BLS-side data gap (no fix possible). |
| 1.4 Activate variants | ✅ Live | All 3,489 pack_variants now `is_active=true`. |
| 1.5 Auto-approve claims | ✅ Shipped (#61) | Wired into daily `pipeline_promote.yml` workflow with threshold 90 + hard filters: image required, CPG-unit allowlist, sub-score floors. Daily markdown summary lands in GitHub Actions. |
| — Insight views | ✅ Live | Migration 049 deployed; 6 views queryable. |
| — Auto-decline | ✅ Shipped (#62) | OFF + news/gdelt + reddit no-image rules; cleared 12,896 pending claims (queue: 14,844 → 1,948). Wired daily. |
| — Event dedup (syndication) | ✅ Shipped (#63, #64) | Collapse `published_changes` on `(entity_id, size_before, size_after)`. **3,899 → 2,800** rows platform-wide. Cadbury: **395 → 105** events. Each event tracks `evidence_count` + full source list. |
| — Cadbury manual dedup | ✅ Live | 32 ghost entities deleted + 16 fuzzy merges executed. Cadbury entities: **138 → 88**. With-changes count: **94 → 76**. |
| — Daily workflow | ✅ Live | `pipeline_promote.yml` now runs: auto_decline → auto_approve → promote → backfill_entity_images. One workflow, one schedule (12:00 UTC), one job summary. |

### Phase 2: Build the Insight Layer

| Task | Status | Notes |
|------|--------|-------|
| 2.1 Insight queries | ✅ Deployed | Migration 049 in production. |
| 2.2.0 `/brands/[name]` mockup | ✅ **Cadbury reference mockup at `web/public/mockups/brands-cadbury.html`** | Includes hero stats, year-by-year timeline (with caveat about coverage gaps), wall-of-shame with source links + socialimage fallback, products grid with image-first sort + top-25 + expand, **event-led evidence trail** with parent-network grouping (Newsquest UK / Reach plc / DMGT / News UK), inline expand to per-source list, typographic placeholders, route-intent toast. All numbers consistent (105 events / 76 products / 526 sources). **Aesthetic locked in: existing FULLCARTS_DESIGN_EXPORT.md — "Investigative Journalism meets Modern Product Design"**, dark graphite + Space Grotesk + JetBrains Mono. |
| 2.2.1 `/brands/[name]` Next.js | **Next active workstream** | Mockup is mature enough to translate into Server Components with live Supabase queries + ISR (revalidate: 3600). |
| 2.2.2 `/products/[id]` mockup | Pending | Where brand-page cards route to. Pattern after the brand page. |
| 2.2.3 Homepage / `/products` / `/insights` / `/about` | Pending | Per design doc. Homepage depends on brand-page patterns. |
| 2.3 Content generation API | Pending | Thin JSON wrappers over Supabase views. |
| 2.4 Skimpflation pipeline | Pending | Connect `nutrition_skimp_results` → `published_changes`. |
| — `socialimage` → `entity.image_url` backfill | Designed, queued | GDELT raw_payload already has the URLs; just need to plumb to `entity.image_url` via `backfill_entity_images.py` extension. ~30 min PR. |
| — URL-pattern syndication detection | Designed, queued | Replace hand-curated Newsquest/Reach domain table with URL-pattern detection (e.g. Newsquest's `/resources/images/{id}/?type=og-image`). |
| — `event_evidence_summary` SQL view | Pending | For real Next.js page to render event-led trail without N+1 queries. |

### Phase 3: Launch Content Engine

| Task | Status | Notes |
|------|--------|-------|
| Strategy doc | ✅ Shipped (#59) | `docs/plans/2026-05-13-social-content-engine.md` — faceless social content engine plan. |
| 3.1 Platform & audience | **Planned** | Instagram, TikTok, X, newsletter, blog |
| 3.2 Content pillar templates | **Planned** | 6 pillars with SQL queries defined in plan |
| 3.3 Content scoring | **SQL written** | `content_candidates` view in migration 049 |
| 3.4 Content calendar | **Planned** | Weekly rhythm defined in plan |
| 3.5 Remaining gaps | **Identified** | OG tags, image generation, tip form, tracking |

### Execution Order for Phase 1

Run these in order with `SUPABASE_KEY` set. Use `--dry-run` first on each.

```bash
# 1. Dedup audit (cleans entity table)
python -m pipeline.scripts.dedup_entities --dry-run
python -m pipeline.scripts.dedup_entities --auto

# 2. BLS scraper re-run (fills NULL CPI values)
python -m pipeline.cli bls_shrinkflation

# 3. Auto-approve high-confidence pending claims
python -m pipeline.scripts.auto_approve_claims --dry-run
python -m pipeline.scripts.auto_approve_claims --threshold 80

# 4. Backfill images (claim images first, then entity propagation)
python -m pipeline.scripts.backfill_claim_images --status approved
python -m pipeline.scripts.backfill_claim_images --status matched
python -m pipeline.scripts.backfill_entity_images

# 5. Activate variants for weekly monitoring
python -m pipeline.scripts.activate_variants --dry-run
python -m pipeline.scripts.activate_variants

# 6. Deploy insight views
# → Run db/migrations/049_insight_views.sql in Supabase SQL Editor
```

---

## Phase 1: Make the Data Credible (1–2 weeks)

The goal of Phase 1 is to ensure the 3,096 published changes are accurate, deduplicated, and visually presentable before any public-facing content is built on top of them.

---

### Task 1.1: Audit Deduplication Quality

**Why:** `promote_claims.py` deduplicates on `MD5(lower(brand) + lower(product_name))[:16]`. If Reddit users describe the same product differently ("Lay's Classic Chips" vs "Lays Potato Chips Classic"), they become separate entities. Duplicate entities inflate brand rankings and undermine credibility.

**Steps:**

1. Run a SQL audit query to surface likely duplicates:
```sql
SELECT a.id AS id_a, b.id AS id_b,
       a.brand, a.canonical_name AS name_a, b.canonical_name AS name_b
FROM product_entities a
JOIN product_entities b
  ON lower(a.brand) = lower(b.brand)
  AND a.id < b.id
  AND similarity(lower(a.canonical_name), lower(b.canonical_name)) > 0.5
ORDER BY similarity(lower(a.canonical_name), lower(b.canonical_name)) DESC
LIMIT 100;
```
(Requires `pg_trgm` extension — already used for fuzzy search indexes on `usda_products`.)

2. For each cluster of duplicates, merge into a single canonical entity:
   - Pick the entity with the most published_changes as the canonical one
   - Update `published_changes.entity_id` for the others to point to the canonical
   - Update `pack_variants.entity_id` likewise
   - Delete the orphaned product_entities rows

3. Write a `pipeline/scripts/dedup_entities.py` script to automate this. It should:
   - Group entities by brand
   - Within each brand, cluster by trigram similarity > 0.6
   - Present clusters for manual confirmation (interactive mode) or auto-merge (batch mode with `--auto` flag for similarity > 0.85)
   - Log every merge for audit trail

**Deliverable:** A verified count of unique product entities and a clean `brand_scorecard` view.

**Estimated effort:** 1 day

---

### Task 1.2: Backfill Product Images

**Why:** Every `product_entities.image_url` is NULL. Visual social media content is impossible without images.

**What already exists:**
- `backfill_claim_images.py` — downloads Reddit images, resizes to WebP, uploads to Supabase Storage (`claim-images` bucket). Already has Wayback Machine fallback for dead URLs.
- Kroger discovery scraper captures `product.images[0].sizes[0].url`
- Walmart discovery scraper captures `largeImage` or `mediumImage`
- OFF discovery scraper captures `image_url`
- All of these are stored in `raw_items.raw_payload` but never propagated to `product_entities.image_url`

**Steps:**

1. **Run the existing claim image backfill** for all approved/matched claims:
```bash
python -m pipeline.scripts.backfill_claim_images --status approved --limit 5000
python -m pipeline.scripts.backfill_claim_images --status matched --limit 5000
```
This populates `claims.image_storage_path` with Supabase Storage paths.

2. **Write a new script `pipeline/scripts/backfill_entity_images.py`** that propagates images to `product_entities.image_url`:

   Priority order for image source:
   1. Supabase Storage path from `claims.image_storage_path` (highest quality — curated)
   2. Kroger API image URL (from `raw_items` where `source_type='kroger_api'`, matched by UPC via `pack_variants`)
   3. Walmart API image URL (same pattern, `source_type='walmart'`)
   4. Open Food Facts image URL (same pattern, `source_type='openfoodfacts'`)

   The script should:
   - Join `product_entities` → `pack_variants` → `raw_items` to find matching images
   - For claims-sourced images, use the Supabase Storage public URL
   - For API-sourced images, use the external URL directly (Kroger/Walmart/OFF CDNs)
   - Update `product_entities.image_url` with the best available image
   - Track: entities_updated, entities_still_missing

3. **Add image backfill to the daily promote workflow:**
   After `promote_claims.py` runs in `pipeline_promote.yml`, also run the entity image backfill so new entities get images automatically.

**Deliverable:** image_url populated for 70%+ of product_entities. Remaining gaps are products only reported via text (no photo, no retail API match).

**Estimated effort:** 1–2 days

---

### Task 1.3: Fix BLS CPI Index Values

**Why:** BLS downsizing/upsizing counts are loaded, but `official_cpi` and `rcpi_sc` columns are NULL. This blocks the most authoritative content pillar — comparing official CPI to the shrinkflation-adjusted R-CPI-SC index.

**Current status from PIPELINE_FIX_PLAN.md:** The BLS CPI parser was partially fixed on 2026-03-21 (Excel serial date handling added). Unclear if the data file merge issue was fully resolved.

**Steps:**

1. **Verify current state:**
```sql
SELECT series, period,
       downsizing_count, upsizing_count,
       official_cpi, rcpi_sc
FROM bls_shrinkflation
ORDER BY period DESC
LIMIT 20;
```
If `official_cpi` and `rcpi_sc` are still NULL, proceed with the fix.

2. **Debug the data file parsing:**
   - Download the BLS XLSX files manually and inspect their structure
   - Check if `_parse_data_file()` in `bls_shrinkflation.py` returns 0 rows
   - The most likely issue: series name mismatch between counts file ("All food") and data file (different capitalization or naming)
   - Fix: normalize series names to `lower().strip()` before the merge key

3. **Re-run the BLS scraper** after the fix:
```bash
python -m pipeline.cli bls_shrinkflation
```

4. **Verify:**
```sql
SELECT COUNT(*) FROM bls_shrinkflation WHERE official_cpi IS NOT NULL;
-- Should be > 0
```

**Deliverable:** Complete BLS data with both counts AND CPI index values.

**Estimated effort:** 2–4 hours

---

### Task 1.4: Activate Weekly Price Monitoring

**Why:** `off_daily` and `kroger_weekly` scrapers produce 0 rows because they query `pack_variants WHERE is_active = true` and need populated records. Until these run, you have no ongoing price/size monitoring and Pillar 4 (Price-Per-Unit Watchdog) is blocked.

**Steps:**

1. **Verify pack_variants has records:**
```sql
SELECT COUNT(*) FROM pack_variants;
SELECT COUNT(*) FROM pack_variants WHERE is_active = true;
```
If `is_active` defaults to false or NULL, update:
```sql
UPDATE pack_variants SET is_active = true WHERE upc IS NOT NULL AND upc NOT LIKE 'CLAIM-%';
```
(Only activate variants with real UPCs — synthetic CLAIM- keys won't match any API.)

2. **Manually trigger Kroger weekly to test:**
```bash
python -m pipeline.cli kroger --dry-run
```
Verify it loads active UPCs and attempts to fetch. Then run without `--dry-run`.

3. **Manually trigger OFF daily to test:**
```bash
python -m pipeline.cli off_daily --dry-run
```

4. **Verify `variant_observations` are being created:**
```sql
SELECT source_type, COUNT(*) 
FROM variant_observations 
GROUP BY source_type;
```
After two weekly Kroger runs (2 weeks apart), price trend data becomes available.

**Deliverable:** Weekly Kroger and daily OFF monitoring producing `variant_observations` rows.

**Estimated effort:** Half day (mostly verification and one-time SQL)

---

### Task 1.5: Run Pending Claims Through Extraction

**Why:** 6,278 claims are still in `pending` status. Many of these may contain valid shrinkflation data that was never reviewed. Processing them increases your published dataset significantly.

**Steps:**

1. **Check the pending claims breakdown:**
```sql
SELECT 
  source_type,
  COUNT(*) AS total,
  COUNT(*) FILTER (WHERE old_size IS NOT NULL AND new_size IS NOT NULL) AS has_sizes,
  ROUND(AVG((confidence_scores->>'overall')::numeric), 1) AS avg_confidence
FROM claims
WHERE status = 'pending'
GROUP BY source_type
ORDER BY total DESC;
```

2. **Auto-approve high-confidence pending claims:**
   Claims with overall confidence > 80% AND both old/new sizes present are likely valid. Write a script or SQL:
```sql
UPDATE claims
SET status = 'approved'
WHERE status = 'pending'
  AND (confidence_scores->>'overall')::numeric >= 80
  AND old_size IS NOT NULL
  AND new_size IS NOT NULL;
```

3. **Run promote_claims.py** to process the newly approved claims:
```bash
python -m pipeline.scripts.promote_claims
```

4. **Re-run the entity image backfill** for the new entities.

**Deliverable:** Potentially 1,000–2,000 additional published changes, expanding coverage.

**Estimated effort:** Half day

---

## Phase 2: Build the Insight Layer (1–2 weeks)

Phase 2 turns raw data into queryable insights and builds the public-facing pages to display them. By the end of Phase 2, fullcarts.org shows real data to visitors.

---

### Task 2.1: Create Insight Queries

**Why:** The database views (`brand_scorecard`, `category_stats`, etc.) exist but there's no curated set of "headline stat" queries designed for content generation. These queries become the backbone of both the website and social media content.

**Deliverables — a set of SQL views or functions:**

#### A. Brand Rankings
```sql
-- Top 10 worst offender brands (by number of shrinkflation events)
CREATE OR REPLACE VIEW brand_rankings AS
SELECT
  brand,
  product_count,
  shrinkflation_events,
  restoration_events,
  total_shrinkage_pct,
  ROUND(total_shrinkage_pct / NULLIF(shrinkflation_events, 0), 1) AS avg_shrink_per_event,
  first_detected,
  last_detected
FROM brand_scorecard
WHERE brand IS NOT NULL
ORDER BY shrinkflation_events DESC;
```

#### B. Biggest Individual Shrinks
```sql
CREATE OR REPLACE VIEW biggest_shrinks AS
SELECT
  pc.brand,
  pc.product_name,
  pc.size_before,
  pc.size_after,
  pc.size_unit,
  pc.size_delta_pct,
  pc.observed_date,
  pe.image_url,
  pe.category
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE pc.change_type = 'shrinkflation'
  AND NOT pc.is_retracted
  AND pc.size_delta_pct IS NOT NULL
ORDER BY pc.size_delta_pct ASC
LIMIT 50;
```

#### C. Category Breakdown
```sql
-- Already exists as category_stats view, but add average price impact
CREATE OR REPLACE VIEW category_insights AS
SELECT
  cs.*,
  (SELECT ROUND(AVG(ABS(vo.price_per_unit)), 2)
   FROM variant_observations vo
   JOIN pack_variants pv ON pv.id = vo.variant_id
   JOIN product_entities pe2 ON pe2.id = pv.entity_id
   WHERE pe2.category = cs.category) AS avg_price_per_unit
FROM category_stats cs;
```

#### D. Shrinkflation Timeline (for charts)
```sql
CREATE OR REPLACE VIEW shrinkflation_timeline AS
SELECT
  DATE_TRUNC('month', observed_date)::date AS month,
  COUNT(*) AS events,
  COUNT(*) FILTER (WHERE change_type = 'shrinkflation') AS shrink_events,
  COUNT(*) FILTER (WHERE change_type = 'restoration') AS restoration_events,
  ROUND(AVG(size_delta_pct) FILTER (WHERE size_delta_pct < 0), 1) AS avg_shrink_pct
FROM published_changes
WHERE NOT is_retracted
  AND observed_date IS NOT NULL
GROUP BY DATE_TRUNC('month', observed_date)
ORDER BY month;
```

#### E. CPI vs Shrinkflation Context
```sql
CREATE OR REPLACE VIEW cpi_shrinkflation_context AS
SELECT
  f.observation_date,
  f.value AS food_at_home_cpi,
  LAG(f.value) OVER (ORDER BY f.observation_date) AS prev_month_cpi,
  ROUND(((f.value - LAG(f.value) OVER (ORDER BY f.observation_date)) 
    / NULLIF(LAG(f.value) OVER (ORDER BY f.observation_date), 0)) * 100, 2) AS cpi_mom_change_pct,
  (SELECT COUNT(*) FROM published_changes pc
   WHERE NOT pc.is_retracted
     AND DATE_TRUNC('month', pc.observed_date) = DATE_TRUNC('month', f.observation_date)
  ) AS shrink_events_that_month
FROM fred_cpi_data f
WHERE f.series_id = 'CPIUFDNS'
ORDER BY f.observation_date DESC;
```

#### F. Skimpflation Highlights
```sql
-- Surface the USDA nutrition change data for content
-- Requires: nutrition_skimp_results table (254 products already flagged)
CREATE OR REPLACE VIEW skimpflation_highlights AS
SELECT
  up.brand_name,
  up.description,
  up.gtin_upc,
  up.category,
  nsr.signal_type,
  nsr.nutrient,
  nsr.old_value,
  nsr.new_value,
  nsr.change_pct,
  nsr.earliest_release,
  nsr.latest_release
FROM nutrition_skimp_results nsr
JOIN usda_products up ON up.gtin_upc = nsr.gtin_upc
ORDER BY ABS(nsr.change_pct) DESC;
```

#### G. News Coverage Cross-Reference
```sql
-- Which brands get the most news coverage about shrinkflation?
CREATE OR REPLACE VIEW news_brand_mentions AS
SELECT
  c.brand,
  COUNT(DISTINCT ri.id) AS news_mentions,
  bs.shrinkflation_events AS our_documented_events,
  MIN(ri.source_date) AS earliest_news_mention,
  MAX(ri.source_date) AS latest_news_mention
FROM claims c
JOIN raw_items ri ON ri.id = c.raw_item_id
LEFT JOIN brand_scorecard bs ON lower(bs.brand) = lower(c.brand)
WHERE ri.source_type IN ('news', 'gdelt')
  AND c.brand IS NOT NULL
GROUP BY c.brand, bs.shrinkflation_events
HAVING COUNT(DISTINCT ri.id) >= 2
ORDER BY news_mentions DESC;
```

**Estimated effort:** 1 day to write, test, and deploy as a migration

---

### Task 2.2: Build Public Website Pages

**Why:** The current public site is a "Coming Soon" page. The admin UI works but is private. You need public pages that display insights to visitors and serve as landing pages for social media links.

**Tech:** Next.js app already exists at `/web/src/app/`. Supabase client is configured. Design system is documented in `FULLCARTS_DESIGN_EXPORT.md`.

#### Page 1: Homepage Dashboard (`/`)
Replace the "Coming Soon" page with a live dashboard showing:

- **Hero stats row:** Total products tracked, total shrinkflation events detected, number of brands, average shrink %
  - Data source: `dashboard_stats()` function (already exists)
- **"Latest Catches" feed:** 5 most recent published_changes with product image, brand, product name, size change, and date
  - Data source: `recent_changes` view
- **"Worst Offenders" mini-leaderboard:** Top 5 brands by shrinkflation event count
  - Data source: `brand_scorecard` view
- **CTA:** "Explore the full database" → links to products page

**Key implementation notes:**
- Server-rendered (SSR) for SEO — use Supabase server client
- Revalidate every hour (`revalidate: 3600`)
- Apply existing design system (dark theme, Space Grotesk headings, red accent for shrinkflation)

#### Page 2: Products Listing (`/products`)
Searchable, filterable product catalog:

- **Search bar:** Full-text search on product name / brand (product_entities has tsvector)
- **Filter sidebar:** Category dropdown, sort by (worst shrink %, most events, most recent)
- **Product cards:** Image, brand, product name, total shrink %, number of events, latest event date
- **Pagination:** 20 per page

Data source: `product_entities` joined with aggregate data from `published_changes`

#### Page 3: Product Detail (`/products/[id]`)
Individual product page — this is what social media posts link to:

- **Product header:** Image, brand, product name, category
- **Size timeline:** Visual chart showing size over time (from `variant_observations`)
- **Change history:** List of all published_changes for this product with evidence links
- **Evidence trail:** Links to original Reddit posts, news articles, or API sources
- **Price data:** If available from Kroger/OFF, show price-per-unit trend
- **Related products:** Other products from the same brand

Data source: `product_entities` + `published_changes` + `variant_observations` + `raw_items`

#### Page 4: Brand Scorecard (`/brands/[name]`)
Brand accountability page:

- **Brand header:** Brand name, total products tracked, total events
- **Products list:** All products from this brand with their shrink data
- **Timeline:** When did this brand's shrinkflation events occur?
- **Restoration credit:** Any restorations get highlighted positively
- **News coverage:** Related news articles mentioning this brand

Data source: `brand_scorecard` view + `published_changes` filtered by brand

#### Page 5: Insights / Trends (`/insights`)
The "By the Numbers" page for macro context:

- **Shrinkflation timeline chart:** Events per month over time
- **CPI comparison:** FRED food CPI vs. shrinkflation event frequency
- **BLS official data:** Government downsizing counts by quarter
- **Category breakdown:** Bar chart of most-affected categories
- **Skimpflation section:** Top nutrition change findings from USDA data

Data source: `shrinkflation_timeline`, `cpi_shrinkflation_context`, `bls_shrinkflation`, `category_stats`, `skimpflation_highlights`

#### Page 6: About (`/about`)
Static page explaining FullCarts mission, methodology, data sources, and evidence standards.

**Estimated effort:** 5–7 days for all pages. Prioritize Pages 1, 2, 3, and 5 — these are the most linkable from social media.

---

### Task 2.3: Build an API for Content Generation

**Why:** Social media content creation tools (and potentially future automation) need clean JSON endpoints to pull insight data.

**Endpoints to add (Next.js API routes):**

```
GET /api/stats              → dashboard_stats() output
GET /api/brands/top         → Top N brands from brand_scorecard
GET /api/products/worst     → Biggest individual shrinks
GET /api/products/latest    → Most recent published_changes
GET /api/products/[id]      → Single product detail with all changes
GET /api/categories         → category_stats view
GET /api/timeline           → shrinkflation_timeline view
GET /api/insights/cpi       → cpi_shrinkflation_context view
GET /api/insights/bls       → bls_shrinkflation data
```

These are thin wrappers over the Supabase views/functions. Cache with `Cache-Control: s-maxage=3600` (1 hour).

**Estimated effort:** 1 day

---

### Task 2.4: Connect Skimpflation Data to the Publishing Pipeline

**Why:** 254 USDA products with nutrition changes are sitting in `nutrition_skimp_results` with no path to `published_changes`. This is unique data nobody else has — it deserves to be surfaced.

**Steps:**

1. Write `pipeline/scripts/promote_skimpflation.py`:
   - Read from `nutrition_skimp_results`
   - For each result, find or create a `product_entity` (match by UPC via `usda_products.gtin_upc` → `pack_variants.upc`)
   - Create a `published_change` with `change_type = 'skimpflation'`
   - Store the nutrient change details in `evidence_summary` JSONB
   - Set `size_delta_pct` to NULL (not a size change) — add a new field `nutrition_delta_pct` or store in evidence_summary

2. Update the `recent_changes` view to include skimpflation changes.

3. Add a skimpflation badge/tag in the frontend (use the existing evidence tag system — "Skimpflation" tag already defined in ClaimActions).

**Deliverable:** ~254 skimpflation entries in published_changes, visible on the website.

**Estimated effort:** 1 day

---

## Phase 3: Launch Content Engine (Ongoing)

Phase 3 defines the social media strategy and the operational process for turning insights into posts on an ongoing basis.

---

### Task 3.1: Define Target Platforms and Audience

**Recommended platform priority:**

| Platform | Why | Content Format | Posting Cadence |
|----------|-----|---------------|-----------------|
| **Instagram** | Visual before/after content performs well. 25-44 age demographic is primary grocery shopper. | Carousel posts, Reels, Stories | 3-4x/week |
| **TikTok** | Highest viral potential. "Exposing brands" content trends regularly. | Short-form video (15-60s) | 3-5x/week |
| **X (Twitter)** | Best for data-driven hot takes, threading, and journalist engagement. | Text + image posts, threads | Daily |
| **Newsletter** | Deepest engagement. Owned audience. Weekly roundup format. | Long-form email | 1x/week |
| **Website blog** | SEO value. Permanent home for deep-dive analyses. | Articles (800-1500 words) | 1-2x/month |

**Audience personas:**

1. **The Frustrated Shopper** — Notices their cereal box feels lighter. Wants validation and information. Engages with "gotcha" reveals and brand rankings.
2. **The Data Nerd** — Loves charts, statistics, and methodology. Engages with CPI comparisons, trend analyses, and skimpflation deep-dives.
3. **The Activist Consumer** — Wants to hold brands accountable. Shares content to pressure companies. Engages with "worst offender" lists and restoration wins.
4. **The Journalist** — Looking for defensible data to cite in articles. Needs clean numbers, methodology transparency, and easy-to-reference pages.

---

### Task 3.2: Content Pillar Templates

Each pillar gets a repeatable template that can be filled from database queries.

#### Pillar 1: "Gotcha" Product Reveals (3x/week)

**Template — Instagram Carousel / TikTok:**
- Slide 1: Product image with brand name — "Did you notice?"
- Slide 2: Before size (e.g., "Was: 16 oz") with old packaging reference
- Slide 3: After size (e.g., "Now: 13.5 oz") — highlight the delta
- Slide 4: "That's a {X}% reduction while the price stayed the same"
- Slide 5: CTA — "Follow @fullcarts for more" + link to product page

**Data query:**
```sql
SELECT pc.brand, pc.product_name, pc.size_before, pc.size_after,
       pc.size_unit, pc.size_delta_pct, pe.image_url,
       pc.observed_date, pc.evidence_summary
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE NOT pc.is_retracted
  AND pc.change_type = 'shrinkflation'
  AND pe.image_url IS NOT NULL
  AND ABS(pc.size_delta_pct) >= 5
ORDER BY pc.published_at DESC;
```

**Selection criteria for "post-worthy" reveals:**
- Has product image
- Size change >= 5% (dramatic enough to be interesting)
- Well-known brand (recognizable to general audience)
- Recent or timely (tie to current news cycle if possible)

---

#### Pillar 2: "Worst Offenders" Rankings (1x/week)

**Template — Instagram Carousel / X Thread:**
- "The Top 5 Shrinkflation Offenders This Month"
- One slide per brand: logo area, number of products affected, average shrink %
- Final slide: "See the full leaderboard at fullcarts.org/brands"

**Data query:**
```sql
SELECT brand, shrinkflation_events, product_count,
       ROUND(total_shrinkage_pct / NULLIF(shrinkflation_events, 0), 1) AS avg_shrink_pct
FROM brand_scorecard
WHERE brand IS NOT NULL AND shrinkflation_events > 0
ORDER BY shrinkflation_events DESC
LIMIT 10;
```

**Variations:**
- "Worst Offenders: Snack Edition" (filter by category)
- "Worst Offenders: 2025 vs 2024" (filter by year)
- "Most Improved: Brands That Restored Sizes" (use restoration_events)

---

#### Pillar 3: "By the Numbers" Macro Trends (1x/week)

**Template — X Thread / Newsletter / Blog:**
- Lead with an authoritative stat: "The BLS recorded {X} products decreasing in size in Q{N} {YEAR}"
- Follow with FRED CPI context: "Meanwhile, the Food-at-Home CPI rose {Y}% — meaning you're paying more AND getting less"
- Add FullCarts-specific data: "We've documented {Z} shrinkflation events across {N} brands"
- Link to the /insights page for the full picture

**Data queries:**
```sql
-- BLS headline stat
SELECT period, SUM(downsizing_count) AS total_downsized
FROM bls_shrinkflation
WHERE period >= DATE_TRUNC('quarter', CURRENT_DATE - INTERVAL '3 months')
GROUP BY period ORDER BY period DESC LIMIT 1;

-- FRED YoY food inflation
SELECT observation_date, value,
  ROUND(((value - LAG(value, 12) OVER (ORDER BY observation_date))
    / NULLIF(LAG(value, 12) OVER (ORDER BY observation_date), 0)) * 100, 1) AS yoy_pct
FROM fred_cpi_data
WHERE series_id = 'CPIUFDNS'
ORDER BY observation_date DESC LIMIT 1;
```

---

#### Pillar 4: Price-Per-Unit Watchdog (after Kroger monitoring is live — ~2 weeks)

**Template — Instagram / X:**
- "{Product} used to cost ${X}/oz. Now it's ${Y}/oz."
- "That's a {Z}% increase in what you're actually paying per ounce"
- Visual: price-per-unit line chart over time

**Data query (once variant_observations has price data):**
```sql
SELECT vo.observed_date, vo.size, vo.size_unit, vo.price, vo.price_per_unit,
       pv.variant_name, pe.brand, pe.canonical_name
FROM variant_observations vo
JOIN pack_variants pv ON pv.id = vo.variant_id
JOIN product_entities pe ON pe.id = pv.entity_id
WHERE pe.id = '{entity_id}'
ORDER BY vo.observed_date;
```

**Note:** This pillar is blocked until Task 1.4 is complete and at least 2 weeks of Kroger data has accumulated.

---

#### Pillar 5: Skimpflation Spotlight (1x/week after Task 2.4)

**Template — Instagram Carousel / TikTok:**
- "They didn't just shrink it — they changed the recipe"
- Slide 1: Product name and image
- Slide 2: "Protein dropped {X}%" or "Sugar increased {Y}%"
- Slide 3: Comparison table — before vs after nutrition
- Slide 4: "Source: USDA FoodData Central" — builds credibility
- CTA: "What products have you noticed taste different?"

**Data query:**
```sql
SELECT up.brand_name, up.description, up.gtin_upc,
       nsr.nutrient, nsr.old_value, nsr.new_value,
       ROUND(nsr.change_pct, 1) AS change_pct,
       nsr.signal_type
FROM nutrition_skimp_results nsr
JOIN usda_products up ON up.gtin_upc = nsr.gtin_upc
WHERE ABS(nsr.change_pct) >= 10
ORDER BY ABS(nsr.change_pct) DESC;
```

**This is a unique differentiator.** No other consumer platform cross-references USDA nutrition data across releases to detect ingredient/nutrition quality changes. Lead with this angle.

---

#### Pillar 6: Restoration Wins (1-2x/month)

**Template — Instagram / X:**
- "GOOD NEWS: {Brand} restored {Product} to its original size!"
- Positive framing — "Proof that speaking up works"
- Side-by-side: shrunk size → restored size
- Tag the brand

**Data query:**
```sql
SELECT * FROM restorations ORDER BY published_at DESC LIMIT 10;
```

**Why this matters for strategy:** Purely punitive content burns out audiences. Restoration posts provide emotional relief, incentivize brand behavior change, and show FullCarts is fair. They also tend to get shared by the brands themselves.

---

### Task 3.3: Content Selection & Prioritization Process

Not all 3,096 published changes are worth posting about. Define a scoring system:

**Post-worthiness score (0-100):**

| Factor | Weight | Criteria |
|--------|--------|----------|
| Brand recognition | 30 | Major national brand = 30, regional = 15, store brand = 5 |
| Shrink magnitude | 25 | >20% = 25, 10-20% = 15, 5-10% = 10, <5% = 5 |
| Has image | 20 | Yes = 20, No = 0 |
| Recency | 15 | Last 30 days = 15, last 90 = 10, last year = 5, older = 0 |
| News tie-in | 10 | Brand is in recent news = 10, otherwise 0 |

**Implementation:** Add a `content_score` column to `published_changes` or create a view. Sort by score when selecting content for the week.

```sql
CREATE OR REPLACE VIEW content_candidates AS
SELECT
  pc.*,
  pe.image_url,
  pe.category,
  -- Simple scoring model
  (CASE WHEN pe.image_url IS NOT NULL THEN 20 ELSE 0 END)
  + (CASE WHEN ABS(pc.size_delta_pct) >= 20 THEN 25
          WHEN ABS(pc.size_delta_pct) >= 10 THEN 15
          WHEN ABS(pc.size_delta_pct) >= 5 THEN 10
          ELSE 5 END)
  + (CASE WHEN pc.observed_date >= CURRENT_DATE - 30 THEN 15
          WHEN pc.observed_date >= CURRENT_DATE - 90 THEN 10
          WHEN pc.observed_date >= CURRENT_DATE - 365 THEN 5
          ELSE 0 END)
  AS content_score
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE NOT pc.is_retracted
  AND pc.change_type = 'shrinkflation'
ORDER BY content_score DESC;
```

---

### Task 3.4: Content Calendar Framework

**Weekly rhythm:**

| Day | Platform | Pillar | Notes |
|-----|----------|--------|-------|
| Monday | Instagram + TikTok | Pillar 1: Gotcha Reveal | Start the week with a "Did you know?" |
| Tuesday | X | Pillar 3: By the Numbers | Data-driven post, thread format |
| Wednesday | Instagram + TikTok | Pillar 1: Gotcha Reveal | Second product reveal |
| Thursday | Instagram | Pillar 2 or 5: Rankings or Skimpflation | Carousel format |
| Friday | X + Instagram | Pillar 1: Gotcha Reveal | "Friday Find" |
| Saturday | — | Rest / queue prep | Select next week's content |
| Sunday | Newsletter | All pillars | Weekly roundup email |

**Monthly specials:**
- 1st of month: "Monthly Shrinkflation Report" (macro stats + top findings)
- Mid-month: "Brand Spotlight" deep-dive (one brand's full history)
- End of month: "Restoration of the Month" (positive story)

---

### Task 3.5: Gaps That Still Need Closing

These are items not covered by Phases 1-2 that the content strategy depends on:

| Gap | Impact | Suggested Fix | Priority |
|-----|--------|--------------|----------|
| **No OG meta tags / social cards** | Links shared on social media show no preview image or description | Add `generateMetadata()` to each Next.js page with og:image, og:title, og:description | High — do during Phase 2 page build |
| **No image generation for social posts** | Can't auto-create branded graphics from data | Build a template system (Canvas API, or use a service like Placid/Bannerbear, or generate with HTML→PNG) | Medium — manual design works initially |
| **No URL shortener / tracking** | Can't track which social posts drive traffic | Use Vercel Analytics (free) or add UTM params to links | Medium |
| **No community engagement loop** | Social followers can't easily submit tips back to FullCarts | Add a public tip submission form on the website that writes to the `tips` table | Medium — do after Phase 2 |
| **Open Prices geographic coverage** | Open Prices data is crowdsourced — coverage may be sparse in the US | Check: `SELECT COUNT(*), country_code FROM open_prices_data GROUP BY country_code` — if US coverage is thin, deprioritize this source | Low |
| **USDA release lag** | USDA FDC releases quarterly with ~2 month lag. Latest is 2025-12-18. No 2026 data yet. | Monitor for 2026-04 release. Run `usda_quarterly` when available. | Low — automated via workflow |
| **No A/B testing on content** | Don't know which angles resonate | Track engagement per pillar manually for first 30 days, then optimize | Low — do after launch |

---

## Execution Timeline Summary

| Week | Phase | Key Deliverables |
|------|-------|-----------------|
| **1** | Phase 1 | Dedup audit complete. Image backfill running. BLS fix verified. Pack_variants activated. |
| **2** | Phase 1→2 | Pending claims processed. Insight queries deployed. Start homepage rebuild. |
| **3** | Phase 2 | Homepage + Products page + Product detail page live. API endpoints working. |
| **4** | Phase 2 | Brand scorecard page + Insights page live. Skimpflation pipeline connected. OG meta tags added. |
| **5** | Phase 3 | Social accounts created. First week of content posted (5 posts). Newsletter #1 sent. |
| **6+** | Phase 3 | Ongoing content cadence. Kroger price data available for Pillar 4. Iterate based on engagement data. |

---

## Dependencies Diagram

```
Phase 1.1 (Dedup) ──────────────────────────────┐
Phase 1.2 (Images) ─────────────────────────────┤
Phase 1.3 (BLS Fix) ───────────────────┐        │
Phase 1.4 (Pack Variants) ──┐          │        │
Phase 1.5 (Pending Claims) ─┤          │        │
                             │          │        │
                             ▼          ▼        ▼
                     Phase 2.1 (Insight Queries) ─┐
                                                   │
                     Phase 2.2 (Website Pages) ◄───┤
                     Phase 2.3 (API Endpoints) ◄───┤
                     Phase 2.4 (Skimpflation)  ◄───┘
                             │
                             ▼
                     Phase 3.1-3.5 (Content Launch)
                             │
                     Phase 1.4 (2 weeks later)
                             │
                             ▼
                     Pillar 4 (Price-Per-Unit) unlocked
```
