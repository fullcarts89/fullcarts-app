# FullCarts Architecture

**FullCarts** is a consumer transparency platform tracking shrinkflation — historical package size and price changes across consumer goods.

---

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│  Reddit (public JSON + PRAW)  │  Community submissions  │  RSS  │
│  Arctic Shift (historical)    │  Open Food Facts (future)       │
└──────────────┬──────────────────────────────┬───────────────────┘
               │                              │
               ▼                              ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│    reddit_staging        │    │     submissions          │
│  (confidence-tiered      │    │  (community form input)  │
│   scraper output queue)  │    │                          │
└──────────┬───────────────┘    └──────────┬───────────────┘
           │ promote_staging.py            │ admin approval
           ▼                               ▼
┌──────────────────────────────────────────────────────────────┐
│                   NORMALIZED DATA LAYER                       │
│                                                               │
│  products ──────── product_versions ──────── change_events   │
│  (master record)   (each observed       (computed deltas     │
│                     size/price state)    between versions)    │
│                                                               │
│  Legacy tables kept for backward compatibility:               │
│  events, upvotes, flags                                       │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                   SUPABASE REST API                           │
│  Auto-generated endpoints for all tables + views              │
│  Custom RPC functions: get_product_history, dashboard_stats   │
└──────────┬───────────────────────────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────────────────────────┐
│                      FRONTEND                                 │
│  index.html       — marketing landing page                    │
│  fullcarts.html   — main app (product DB, scanner, admin)     │
│                                                               │
│  Deployed via GitHub Pages at fullcarts.org                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
fullcarts-app/
├── index.html                    # Marketing landing page
├── fullcarts.html                # Main app (stays at root for GitHub Pages)
├── CNAME                         # fullcarts.org domain config
│
├── db/
│   └── migrations/
│       ├── 001_product_versions.sql    # Longitudinal product tracking
│       ├── 002_change_events.sql       # Delta computation + classification
│       ├── 003_views_and_indexes.sql   # Views, functions, analytics
│       └── 004_migrate_existing_data.sql  # One-time backfill from events
│
├── backend/
│   ├── config.py                 # Shared configuration
│   ├── lib/
│   │   ├── supabase_client.py    # Lazy-init Supabase client
│   │   └── nlp.py                # NLP parser (brands, sizes, prices)
│   ├── scrapers/
│   │   ├── news_scraper.py        # Google News RSS (no API key)
│   │   └── openfoodfacts_scraper.py  # OFF weight-change monitor
│   ├── jobs/
│   │   ├── change_detector.py    # Compare versions → create events
│   │   └── promote_staging.py    # Staging → normalized tables
│   └── requirements.txt
│
├── .github/workflows/
│   ├── scrape_reddit.yml         # Every 6h: scrape + detect
│   ├── scrape_sources.yml        # Every 12h: news RSS + Open Food Facts
│   └── detect_changes.yml        # Every 12h: promote + detect
│
├── reddit_public_scraper.py      # Public Reddit scraper (no API key)
├── reddit_scraper.py             # PRAW-based scraper (needs credentials)
├── supabase_seed.sql             # Original schema + seed data
└── requirements.txt              # Root-level Python deps
```

---

## Database Schema

### Entity Relationship

```
products (1) ──── (N) product_versions (1) ──── (0..1) change_events
    │                                                        │
    │                  change_events.version_before_id ───────┘
    │                  change_events.version_after_id  ───────┘
    │
    ├── (N) events          (legacy, kept for backward compat)
    ├── (N) upvotes         (community engagement)
    ├── (N) flags           (error reporting)
    └── (N) reddit_staging  (scraper queue, via synthetic UPC)
```

### Core Tables

#### `products` — Master product record
| Column | Type | Notes |
|--------|------|-------|
| upc (PK) | text | Barcode or `REDDIT-{hash}` for unidentified products |
| name | text | Product name |
| brand | text | Brand / manufacturer |
| category | text | Beverages, Snacks, Paper Goods, etc. |
| current_size | numeric | Latest known size (updated by change detector) |
| unit | text | oz, fl oz, sheets, ct, etc. |
| type | text | shrinkflation, downsizing, skimpflation, etc. |
| repeat_offender | boolean | Auto-set when 2+ shrinkflation events detected |
| image_url | text | Product photo URL |
| source | text | community, reddit_bot, scraper |

#### `product_versions` — Each observed state over time
| Column | Type | Notes |
|--------|------|-------|
| id (PK) | uuid | Auto-generated |
| product_upc (FK) | text | → products.upc |
| observed_date | date | When this version was observed |
| size | numeric | Package size at this point in time |
| unit | text | Unit of measurement |
| price | numeric | Observed retail price (nullable) |
| price_per_unit | numeric | **GENERATED**: `price / size` (stored) |
| retailer | text | Where observed (Walmart, Target, etc.) |
| evidence_url | text | Photo/screenshot proof |
| source | text | community, reddit_bot, scraper, bls |
| source_url | text | Original source link |
| UNIQUE | | `(product_upc, observed_date, source)` |

#### `change_events` — Computed deltas between versions
| Column | Type | Notes |
|--------|------|-------|
| id (PK) | uuid | Auto-generated |
| product_upc (FK) | text | → products.upc |
| version_before_id (FK) | uuid | → product_versions.id |
| version_after_id (FK) | uuid | → product_versions.id |
| detected_date | date | When the change occurred |
| old_size / new_size | numeric | Before/after sizes |
| size_delta_pct | numeric | `((new - old) / old) * 100` (negative = shrunk) |
| old_price / new_price | numeric | Before/after prices |
| old_price_per_unit | numeric | `old_price / old_size` |
| new_price_per_unit | numeric | `new_price / new_size` |
| price_per_unit_delta_pct | numeric | PPU change % (positive = more expensive) |
| change_type | text | shrinkflation, downsizing, upsizing, price_hike, skimpflation, restoration |
| is_shrinkflation | boolean | `true` when size ↓ and price same or ↑ |
| severity | text | minor (<5%), moderate (5-15%), major (>15%) |
| verified | boolean | Admin-verified |
| UNIQUE | | `(version_before_id, version_after_id)` |

### Views

| View | Purpose | Powers |
|------|---------|--------|
| `product_timeline` | Full history of a product's versions + changes | Public product page |
| `shrinkflation_leaderboard` | Products ranked by cumulative shrinkage | "Worst Offenders" page |
| `recent_changes` | Latest detected changes with product info | Dashboard feed |
| `category_stats` | Aggregate stats by product category | Category analytics |
| `pending_review` | Staging entries awaiting admin action | Admin dashboard |

### SQL Functions

| Function | Returns | Usage |
|----------|---------|-------|
| `classify_change(old_size, new_size, old_price, new_price)` | jsonb | Classify a single change |
| `detect_changes_for_product(upc)` | integer | Detect new events for one product |
| `detect_all_changes()` | integer | Detect events for all products |
| `get_product_history(upc)` | jsonb | Full product JSON (versions + changes + upvotes) |
| `dashboard_stats()` | jsonb | Aggregate stats for frontend header |

---

## REST API Endpoints

Supabase auto-generates REST endpoints for all tables and views. The base URL is:
```
https://yvpfefatajcfptfjntkn.supabase.co/rest/v1/
```

All requests require headers:
```
apikey: <your-anon-key>
Authorization: Bearer <your-anon-key>
```

### Product Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/products?select=*` | List all products |
| GET | `/products?upc=eq.{upc}` | Get product by UPC |
| GET | `/products?brand=eq.{brand}` | Filter by brand |
| GET | `/products?category=eq.{category}` | Filter by category |
| GET | `/products?repeat_offender=eq.true` | Repeat offenders only |
| GET | `/products?select=*&order=created_at.desc&limit=20` | Latest products |

### Product Version Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product_versions?product_upc=eq.{upc}&order=observed_date.asc` | Version history for a product |
| GET | `/product_versions?select=*,products(name,brand)` | Versions with product info (join) |
| POST | `/product_versions` | Add a new version observation |

### Change Event Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/change_events?product_upc=eq.{upc}&order=detected_date.asc` | Changes for a product |
| GET | `/change_events?is_shrinkflation=eq.true&order=detected_date.desc` | All shrinkflation events |
| GET | `/change_events?severity=eq.major&order=size_delta_pct.asc` | Major changes (worst first) |
| GET | `/change_events?change_type=eq.shrinkflation&order=detected_date.desc&limit=50` | Recent shrinkflation |

### View Endpoints (read-only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/product_timeline?upc=eq.{upc}` | Full timeline for a product |
| GET | `/shrinkflation_leaderboard?order=cumulative_shrink_pct.asc&limit=25` | Worst offenders |
| GET | `/recent_changes?limit=20` | Latest changes feed |
| GET | `/category_stats` | Stats by category |
| GET | `/pending_review` | Admin: items to review |

### RPC Endpoints (custom functions)

| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/rpc/get_product_history` | `{"p_upc": "048500205020"}` | Full product JSON |
| POST | `/rpc/dashboard_stats` | `{}` | Aggregate dashboard stats |
| POST | `/rpc/detect_changes_for_product` | `{"p_upc": "048500205020"}` | Trigger change detection |
| POST | `/rpc/detect_all_changes` | `{}` | Trigger full scan |

### Example: Fetch Product Timeline (JavaScript)

```javascript
const { data } = await supabase
  .from('product_timeline')
  .select('*')
  .eq('upc', '048500205020')
  .order('observed_date', { ascending: true });

// data = [
//   { upc: '048500205020', name: 'Tropicana Pure Premium OJ', observed_date: '2018-06-01',
//     size: 89, unit: 'fl oz', price: 4.49, price_per_unit: 0.0505,
//     size_delta_pct: null, change_type: null },
//   { ..., observed_date: '2019-06-01', size: 64, price: 3.99, price_per_unit: 0.0623,
//     size_delta_pct: -28.09, change_type: 'shrinkflation', severity: 'major' },
//   { ..., observed_date: '2022-01-01', size: 52, price: 4.99, price_per_unit: 0.096,
//     size_delta_pct: -18.75, change_type: 'shrinkflation', severity: 'major' },
// ]
```

### Example: Dashboard Stats (JavaScript)

```javascript
const { data } = await supabase.rpc('dashboard_stats');

// data = {
//   total_products: 25,
//   total_versions: 50,
//   total_changes: 22,
//   shrinkflation_events: 18,
//   categories_tracked: 11,
//   avg_shrink_pct: 11.2,
//   worst_shrink_pct: -28.1,
//   pending_review: 43
// }
```

---

## Change Detection Logic

The change detector compares consecutive `product_versions` for each product and creates `change_events`.

### Algorithm

```
For each product with ≥ 2 versions:
  Sort versions by observed_date ASC
  For each consecutive pair (v_before, v_after):
    If sizes differ AND no change_event exists for this pair:
      1. Compute size_delta_pct = ((new - old) / old) * 100
      2. Compute price_per_unit for both versions
      3. Compute ppu_delta_pct = ((new_ppu - old_ppu) / old_ppu) * 100
      4. Classify:
         - size ↓ + price same/↑  → shrinkflation (is_shrinkflation = true)
         - size ↓ + price ↓       → downsizing
         - size ↑                  → upsizing
         - size same + price ↑     → price_hike
      5. Assign severity:
         - |delta| < 5%   → minor
         - |delta| 5-15%  → moderate
         - |delta| ≥ 15%  → major
      6. Insert change_event
```

### Running

```bash
# Scan all products
python -m backend.jobs.change_detector

# Scan a single product
python -m backend.jobs.change_detector --upc 048500205020

# Dry run (no writes)
python -m backend.jobs.change_detector --dry-run

# Or via SQL directly:
SELECT detect_all_changes();
SELECT detect_changes_for_product('048500205020');
```

---

## Admin Dashboard Extensions

The existing admin dashboard in `fullcarts.html` reviews `reddit_staging` entries. To support the new schema, extend it with:

### 1. Change Event Review Panel
```
Query: GET /recent_changes?verified=eq.false&limit=50
Actions:
  - Verify event (PATCH /change_events?id=eq.{id} → {verified: true, verified_by: 'admin'})
  - Dismiss false positive (DELETE /change_events?id=eq.{id})
  - Edit classification (PATCH → {change_type: 'downsizing'})
```

### 2. Product Version Manager
```
Query: GET /product_timeline?upc=eq.{upc}
Actions:
  - Add version (POST /product_versions → {product_upc, observed_date, size, unit, price})
  - Upload evidence (store image URL in evidence_url field)
  - Merge duplicate products (update product_versions.product_upc, delete old product)
```

### 3. Submission Approval Flow
```
When admin approves a submission:
  1. Upsert product record
  2. Insert product_version (before + after states)
  3. Run change detection: POST /rpc/detect_changes_for_product
  4. Update submission status to 'approved'
```

---

## Public-Facing Product Page

The product history page displays:

### 1. Product Header
- Name, brand, category, image
- Current size and price
- Repeat offender badge
- Total shrinkage percentage

### 2. Timeline Chart
- X-axis: observed_date
- Y-axis (left): size
- Y-axis (right): price_per_unit
- Color-coded dots: green (upsizing/stable), red (shrinkflation), orange (downsizing)

### 3. Before/After Cards
For each `change_event`:
```
┌──────────────────────────────────────────────┐
│  SHRINKFLATION  ·  Jan 2022  ·  MAJOR        │
├──────────────────────────────────────────────┤
│  64 fl oz → 52 fl oz        -18.75%          │
│  $3.99 → $4.99              +25.06%          │
│  $0.062/fl oz → $0.096/fl oz  +53.7% PPU    │
│                                              │
│  📸 [evidence photo]                         │
│  📝 "New carton design debuted same quarter" │
└──────────────────────────────────────────────┘
```

### 4. Computed Deltas Display
```
Original size:   89 fl oz (2018)
Current size:    52 fl oz (2022)
Total shrinkage: -41.6%
Price then:      $4.49 ($0.050/fl oz)
Price now:       $4.99 ($0.096/fl oz)
PPU increase:    +90.1%
```

---

## 6-Week Data Collection Plan

### Week 1: Foundation (Deploy what exists)
- [ ] Run migration SQL files (001–004) in Supabase SQL Editor
- [ ] Set `SUPABASE_URL` and `SUPABASE_KEY` as GitHub repository secrets
- [ ] Enable the `scrape_reddit.yml` workflow
- [ ] Run `reddit_public_scraper.py --backfill` once (seeds historical data)
- [ ] Verify product_versions and change_events populate correctly
- **Expected data: ~200-500 Reddit posts → ~50-100 product_versions**

### Week 2: Reddit API + Monitoring
- [ ] Register Reddit API app at reddit.com/prefs/apps (Script type)
- [ ] Add `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` to GitHub secrets
- [ ] Enable PRAW scraper alongside public scraper for broader subreddit coverage
- [ ] Set up RSS feed monitoring for r/shrinkflation as a lightweight backup
- [ ] Review and approve first batch of admin-queue entries
- **If Reddit API rejected:** Use public JSON scraper (already works without API). Also set up Arctic Shift download for full historical archive.

### Week 3: Data Quality + Admin Workflow
- [ ] Review all `tier=review` staging entries via admin dashboard
- [ ] Manually add 20-30 well-documented shrinkflation cases with evidence photos
- [ ] Cross-reference Reddit data against seed data (merge duplicates)
- [ ] Add product images for top 25 products
- [ ] Test the `detect_all_changes()` pipeline end-to-end
- **Target: 100+ verified products with full version history**

### Week 4: Expand Sources
- [ ] Add Google News RSS scraper for shrinkflation articles
- [ ] Integrate Open Food Facts API for product weight data
- [ ] Pull BLS CPI data for category-level trends
- [ ] Add Arctic Shift historical download if not done in Week 2
- [ ] Build category_stats view validation
- **Target: 300+ products across 10+ categories**

### Week 5: Frontend + Public Features
- [ ] Build product history timeline page using `product_timeline` view
- [ ] Build "Worst Offenders" leaderboard using `shrinkflation_leaderboard` view
- [ ] Add before/after comparison cards using `change_events` data
- [ ] Add dashboard stats header using `dashboard_stats()` RPC
- [ ] Deploy updated frontend to fullcarts.org
- **Target: Public-facing product pages for top 50 products**

### Week 6: Scale + Harden
- [ ] Load test with 1000+ product_versions
- [ ] Add database indexes if query performance degrades
- [ ] Set up monitoring/alerting for scraper failures
- [ ] Document data provenance for all sources
- [ ] Write contributor guide for community data submissions
- [ ] Plan Phase 2: OCR pipeline for Reddit image posts, YouTube scraper
- **Target: 500+ products, automated pipeline running reliably**

### Reddit API Rejection Fallback Strategy

If your Reddit API application is rejected:

1. **Continue with public JSON scraper** — Already built, no API key needed. Fetches from `reddit.com/r/shrinkflation.json`. Limited to ~1000 most recent posts.

2. **Arctic Shift for historical data** — Download the complete r/shrinkflation archive:
   ```
   https://arctic-shift.photon-reddit.com/download-tool
   ```
   Select subreddit `shrinkflation`, download all posts. Parse with the existing NLP pipeline.

3. **RSS feeds for ongoing monitoring** — No auth required:
   ```
   https://www.reddit.com/r/shrinkflation/new/.rss?limit=100
   ```
   Poll every hour, feed into the NLP parser.

4. **PullPush for mid-range history** — Data through May 2025:
   ```
   https://api.pullpush.io/reddit/search/submission/?subreddit=shrinkflation
   ```

5. **Diversify away from Reddit** — Prioritize Open Food Facts, BLS data, Google News, and community submissions. Reddit is valuable but shouldn't be the only source.

---

## Scaling Considerations

### Database (10k+ SKUs)
- `product_versions` table will grow to ~50k-100k rows at 10k SKUs with ~5-10 versions each
- The UNIQUE constraint and indexes on `(product_upc, observed_date)` keep queries fast
- Supabase free tier supports this volume easily
- Consider partitioning `product_versions` by year if it exceeds 1M rows

### Query Performance
- The `price_per_unit` GENERATED column avoids runtime computation
- Views like `shrinkflation_leaderboard` use aggregation — consider materialized views if they become slow
- The `detect_all_changes()` function is O(N * M) where N = products, M = avg versions per product

### Category-Level Analytics
The schema is designed to support category analytics via:
- `products.category` — already populated by the NLP category guesser
- `category_stats` view — pre-built aggregate stats
- Future: add `products.subcategory` for finer granularity (e.g., Snacks → Chips, Cookies)
- Future: add `products.parent_company` for conglomerate-level analysis (e.g., all P&G brands)

### Legal Defensibility
- Every `product_version` has `source`, `source_url`, `evidence_url`, and `created_at`
- The `change_events` table links to specific version IDs for full audit trail
- `verified` / `verified_by` / `verified_at` fields enable admin attestation
- `reddit_staging` preserves the raw scraper output before any processing
- No personally identifiable information stored (no Reddit usernames)

---

## Running via GitHub Actions (Recommended)

Everything runs on GitHub's servers — nothing on your machine.

### One-time setup

1. Go to your repo → **Settings → Secrets and variables → Actions**
2. Add two repository secrets:
   - `SUPABASE_URL` = `https://yvpfefatajcfptfjntkn.supabase.co`
   - `SUPABASE_KEY` = your Supabase service role key
3. Go to **Actions** tab and enable workflows if prompted

### Workflows

| Workflow | Schedule | What it does |
|----------|----------|-------------|
| `scrape_reddit.yml` | Every 6 hours | Scrapes r/shrinkflation + runs change detection |
| `scrape_sources.yml` | Every 12 hours | Google News RSS + Open Food Facts monitor + change detection |
| `detect_changes.yml` | Every 12 hours | Promotes staging entries + runs change detection |

All three can also be triggered manually from the **Actions** tab with `workflow_dispatch`.

### First run: seed historical data

Go to **Actions → Scrape Reddit → Run workflow** and select `backfill` mode. This pulls all historical r/shrinkflation posts (2017–2025) via the Pullpush archive.

---

## Running Locally (Optional)

```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run public Reddit scraper (no API key needed)
export SUPABASE_URL=https://yvpfefatajcfptfjntkn.supabase.co
export SUPABASE_KEY=<your-service-role-key>

python reddit_public_scraper.py --recent

# Run non-Reddit scrapers
python -m backend.scrapers.news_scraper
python -m backend.scrapers.openfoodfacts_scraper

# Run change detection
python -m backend.jobs.change_detector

# Promote staging entries
python -m backend.jobs.promote_staging

# Dry run (see what would happen)
python -m backend.jobs.change_detector --dry-run
python -m backend.jobs.promote_staging --dry-run
python -m backend.scrapers.news_scraper --dry-run
python -m backend.scrapers.openfoodfacts_scraper --dry-run
```
