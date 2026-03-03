# FullCarts Shrinkflation Data Scraping Assessment

**Date:** March 3, 2026
**Scope:** Evaluate approaches to scrape Reddit and other internet sources for shrinkflation data, hosted in Supabase (PostgreSQL).

---

## 1. Current State

FullCarts already has a solid scraping foundation:

| Component | Status | Notes |
|-----------|--------|-------|
| `reddit_scraper.py` (PRAW) | Built, requires Reddit API credentials | Targets 8 subreddits, NLP parsing, confidence tiering, Supabase integration |
| `reddit_public_scraper.py` | Built, no API key needed | Reddit public JSON + Pullpush archive, backfill + recent modes |
| `reddit_staging` table | Schema exists in Supabase | Dedup via `source_url`, tier/status workflow, auto-promotion pipeline |
| Admin review queue | Built into frontend (`fullcarts.html`) | Approve/dismiss staged entries |
| NLP parser | Functional | Brand detection (120+ brands), regex size extraction, category guessing |

**What's working well:**
- The public scraper (`reddit_public_scraper.py`) is the most practical path — no API key needed
- Confidence tiering (auto/review/discard) prevents garbage data from polluting the database
- Auto-promotion pipeline moves high-confidence entries directly to `products` + `events`

**What needs attention:**
- Neither scraper has been deployed on a schedule (GitHub Actions workflow is commented out)
- Pullpush only has data through May 2025 — not current
- No scrapers exist yet for non-Reddit sources
- No image/OCR analysis (many Reddit posts are photos of labels, not text)

---

## 2. Reddit Data Access — Current Landscape (2026)

### Option A: Reddit Official API (PRAW) — Your `reddit_scraper.py`

| Aspect | Details |
|--------|---------|
| **Rate Limit** | 100 requests/min (OAuth), 10 req/min (unauth) |
| **Monthly Cap** | ~10,000 requests on free tier |
| **Authentication** | OAuth2 required — register app at reddit.com/prefs/apps |
| **Cost** | Free for non-commercial, personal, academic use |
| **Restrictions** | Cannot resell data; commercial use requires paid tier |
| **Reliability** | High — official API, well-maintained |

**Verdict:** Good for FullCarts since it's a non-commercial community project. The 100 QPM rate is more than enough for scheduled scraping. Register a Reddit app (script type), set the env vars, and your existing `reddit_scraper.py` will work.

### Option B: Reddit Public JSON — Your `reddit_public_scraper.py`

| Aspect | Details |
|--------|---------|
| **Rate Limit** | Unofficial — ~1 req/2 sec is safe |
| **Authentication** | None (just User-Agent header) |
| **Reliability** | Medium — Reddit can block/change without notice |
| **Data Depth** | Only ~1000 most recent posts per listing |

**Verdict:** Works today and requires zero setup. Good as a fallback but less reliable long-term since Reddit could restrict public JSON access at any time.

### Option C: Pullpush Archive API

| Aspect | Details |
|--------|---------|
| **Endpoint** | `https://api.pullpush.io/reddit/search/submission/` |
| **Data Coverage** | Up to May 2025 (not currently ingesting new data) |
| **Rate Limit** | ~1 req/sec recommended |
| **Best For** | Historical backfill of r/shrinkflation (2017–2025) |

**Verdict:** Excellent for one-time historical backfill. Your existing `--backfill` mode already handles this. Run it once to seed the database, then rely on Options A or B for ongoing data.

### Option D: Arctic Shift Archive

| Aspect | Details |
|--------|---------|
| **Endpoint** | `https://arctic-shift.photon-reddit.com/` |
| **Rate Limit** | ~2000 requests/min (much more generous than Pullpush) |
| **Data** | Full Reddit archive dumps + searchable API |
| **Best For** | High-volume historical queries, subreddit-specific search |
| **Python Wrapper** | `BAScraper` library supports both Pullpush and Arctic Shift |

**Verdict:** Better performance than Pullpush for subreddit-specific queries. Worth adding as a secondary archive source for backfill.

### Recommended Reddit Strategy

```
Phase 1: Historical backfill
  └─ Run reddit_public_scraper.py --backfill (Pullpush, one-time)
  └─ Optionally add Arctic Shift for additional historical coverage

Phase 2: Ongoing scraping (scheduled)
  └─ Primary: reddit_scraper.py (PRAW, every 6 hours via GitHub Actions)
  └─ Fallback: reddit_public_scraper.py --recent (no API key needed)

Phase 3: Review + promote
  └─ Auto-promoted entries go live immediately
  └─ Review-tier entries appear in admin queue in fullcarts.html
```

---

## 3. Non-Reddit Data Sources

### 3a. The Shrink List (theshrinklist.com)

A community-driven shrinkflation tracking site with 170K+ users.

| Aspect | Details |
|--------|---------|
| **Data** | Product database with brand, old/new sizes, % reduction |
| **API** | No public API available |
| **Approach** | Web scraping (HTML) or contact for data partnership |
| **Legal** | Check their ToS before scraping |

**Implementation idea:** A lightweight Python scraper using `requests` + `BeautifulSoup` to pull their `/products/` and `/brands/` pages. Map their data to your `products` + `events` tables.

### 3b. Bureau of Labor Statistics (BLS) CPI Data

The BLS tracks package size changes as part of CPI measurements.

| Aspect | Details |
|--------|---------|
| **API** | Free public API at `api.bls.gov/publicAPI/v2/` |
| **Data** | CPI frequency data on product downsizing/upsizing by month |
| **Registration** | API key recommended (higher rate limits) |
| **Format** | JSON responses |

**Implementation idea:** Query BLS series data for food and household goods CPI categories. Cross-reference size-change frequency data to identify trending product categories.

### 3c. GAO Reports & Government Data

The GAO released a comprehensive shrinkflation analysis (report GAO-25-107451) in 2025 using BLS and NielsenIQ retail scanner data.

| Aspect | Details |
|--------|---------|
| **Key Finding** | Shrinkflation contributed ~0.06 ppt to overall inflation (2019-2024) |
| **Top Categories** | Paper goods (3.0 ppt), cereal (1.6 ppt), snacks, beverages, dairy |
| **Data Access** | Report is public; underlying NielsenIQ data is proprietary |

**Use case:** Reference data for category-level trends, not individual product scraping.

### 3d. Open Food Facts (Already Integrated)

You already use this for UPC lookups. It can also be mined for historical product weight data.

| Aspect | Details |
|--------|---------|
| **API** | Free, public, no auth |
| **Data** | Product weights, barcodes, brands, images, nutrition |
| **Shrinkflation angle** | Compare historical weight entries for the same barcode |

**Implementation idea:** For products in your database, periodically query Open Food Facts to check if the listed weight has changed. Flag discrepancies as potential shrinkflation events.

### 3e. News Article Scraping

Major news outlets frequently publish shrinkflation stories with specific product examples.

| Source | Approach |
|--------|----------|
| **Google News RSS** | Search "shrinkflation" via Google News RSS feed |
| **NewsAPI.org** | Structured API for news articles ($0 for dev tier, 100 req/day) |
| **Common Crawl** | Free web archive, search for shrinkflation articles |

**Implementation idea:** A `news_scraper.py` that fetches shrinkflation headlines and uses NLP to extract product/brand/size mentions, similar to the Reddit parser.

### 3f. Social Media Beyond Reddit

| Platform | Approach | Difficulty |
|----------|----------|-----------|
| **X (Twitter)** | Official API ($100/mo basic tier) or Nitter instances | Medium-High |
| **TikTok** | No practical API for text data | High |
| **YouTube** | YouTube Data API (free, generous limits) — search for shrinkflation videos | Medium |
| **Facebook Groups** | No practical API access | Very High |

**Recommendation:** YouTube Data API is the most accessible. Search for "shrinkflation" videos, pull titles/descriptions, and run through the same NLP parser.

---

## 4. Biggest Opportunities for Improvement

### 4a. Deploy the Existing Scrapers on a Schedule

This is the lowest-hanging fruit. Your scrapers are built but not running.

**Recommended approach — GitHub Actions workflow:**

```yaml
# .github/workflows/reddit_scraper.yml
name: FullCarts Reddit Scraper

on:
  schedule:
    - cron: "0 */6 * * *"   # Every 6 hours
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install requests supabase
      - name: Run public scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: python reddit_public_scraper.py --recent
```

**Cost:** $0 (GitHub Actions free tier gives 2,000 min/month for public repos).

### 4b. Add a Multi-Source Scraper

Create a new `scraper_sources.py` that aggregates data from multiple non-Reddit sources:

```
scraper_sources.py
  ├── GoogleNewsScraper   — RSS feed for "shrinkflation" articles
  ├── BLSScraper          — BLS CPI size-change frequency data
  ├── OpenFoodFactsMonitor— Track weight changes on known UPCs
  └── YouTubeScraper      — Search shrinkflation videos for product mentions
```

Each source feeds into a unified `source_staging` table (similar pattern to `reddit_staging`), then goes through the same confidence tiering and promotion pipeline.

### 4c. Image/OCR Analysis for Reddit Posts

Many Reddit shrinkflation posts are photos of product labels, not text posts. Adding image analysis would dramatically increase data extraction.

**Approach:** Use a vision model (Claude API, GPT-4o, or open-source like LLaVA) to:
1. Download image from Reddit post
2. Extract text from product label photo
3. Parse old/new sizes from the extracted text
4. Feed into the existing NLP pipeline

This is higher effort but would capture a significant portion of posts that currently get classified as "discard" because they have no text content.

### 4d. Generalized Staging Table

Currently `reddit_staging` is Reddit-specific. Consider a generalized staging table:

```sql
CREATE TABLE IF NOT EXISTS source_staging (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source_type      text NOT NULL,  -- 'reddit', 'news', 'bls', 'youtube', etc.
  source_url       text UNIQUE,
  source_metadata  jsonb,          -- Platform-specific fields
  scraped_utc      timestamptz,
  tier             text,
  status           text DEFAULT 'pending',
  -- Extracted fields (same as reddit_staging)
  title            text,
  brand            text,
  product_hint     text,
  old_size         numeric,
  new_size         numeric,
  old_unit         text,
  new_unit         text,
  old_price        numeric,
  new_price        numeric,
  fields_found     integer,
  created_at       timestamptz DEFAULT now()
);
```

---

## 5. Prioritized Roadmap

| Priority | Task | Effort | Impact |
|----------|------|--------|--------|
| **P0** | Deploy `reddit_public_scraper.py` via GitHub Actions (every 6h) | Low | High — starts populating data immediately |
| **P0** | Run `--backfill` once to seed historical Reddit data | Low | High — instant database of 2017-2025 posts |
| **P1** | Register Reddit API app and activate `reddit_scraper.py` (PRAW) | Low | Medium — broader subreddit coverage |
| **P1** | Add Google News RSS scraper for shrinkflation articles | Medium | Medium — catches mainstream product reports |
| **P2** | Add Open Food Facts weight-change monitor | Medium | Medium — automated detection without user reports |
| **P2** | Add BLS CPI data integration for category trends | Medium | Low-Medium — macro-level data |
| **P3** | Add image/OCR pipeline for Reddit photo posts | High | High — unlocks majority of Reddit content |
| **P3** | Generalize staging table for multi-source ingestion | Medium | Medium — cleaner architecture |
| **P3** | Add YouTube Data API scraper | Medium | Low — supplementary source |

---

## 6. Summary

Your existing infrastructure is well-designed. The most impactful next step is simply **deploying what you already have** — the public Reddit scraper via GitHub Actions and running the historical backfill. After that, expanding to news RSS feeds and Open Food Facts monitoring would give you the broadest coverage with the least effort.

The Reddit scraping approach (public JSON + Pullpush for history, PRAW for ongoing) is sound and legal for a non-commercial community project. Non-Reddit sources like BLS data and news articles add credibility and breadth without depending on social media.

---

## Sources

- [Reddit API Rate Limits 2026 Guide](https://painonsocial.com/blog/reddit-api-rate-limits-guide)
- [Reddit API Cost Guide 2025](https://rankvise.com/blog/reddit-api-cost-guide/)
- [Reddit 2025 API Pre-Approval Changes](https://replydaddy.com/blog/reddit-api-pre-approval-2025-personal-projects-crackdown)
- [PullPush — Pushshift Successor](https://pullpush-io.github.io/)
- [Arctic Shift GitHub](https://github.com/ArthurHeitmann/arctic_shift)
- [BAScraper — Python wrapper for PullPush + Arctic Shift](https://github.com/maxjo020418/BAScraper)
- [Best Reddit API Alternatives 2026](https://www.xpoz.ai/blog/comparisons/best-reddit-api-alternatives-2026/)
- [GAO Report: Consumer Prices and Shrinking Product Sizes](https://www.gao.gov/products/gao-25-107451)
- [The Shrink List — Shrinkflation Tracker](https://theshrinklist.com/)
- [Shrinkflation Statistics 2025 — Capital One Shopping](https://capitaloneshopping.com/research/shrinkflation-statistics/)
- [CivicScience: Shrinkflation Consumer Trends 2025](https://civicscience.com/shrinkflation-in-2025-quality-is-key-for-loyal-customers/)
