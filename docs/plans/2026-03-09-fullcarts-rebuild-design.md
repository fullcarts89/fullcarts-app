# FullCarts Rebuild Strategy

**Date:** March 9, 2026
**Status:** Reviewed — founder-approved with amendments
**Author:** Claude Code (architect session)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Target Architecture](#2-target-architecture)
3. [Data Model](#3-data-model)
4. [Ingestion Strategy](#4-ingestion-strategy)
5. [Data Quality Framework](#5-data-quality-framework)
6. [Security Model](#6-security-model)
7. [Website vs App Decision](#7-website-vs-app-decision)
8. [Monetization Readiness](#8-monetization-readiness)
9. [90-Day Implementation Roadmap](#9-90-day-implementation-roadmap)
10. [Risks & Tradeoffs](#10-risks--tradeoffs)
11. [Appendix A: Data Source Details](#appendix-a-data-source-details)
12. [Appendix B: Concrete Schemas](#appendix-b-concrete-schemas)
13. [Appendix C: API Endpoint Contracts](#appendix-c-api-endpoint-contracts)

---

## 1. Executive Summary

### What We're Building

FullCarts is being rebuilt from scratch as a **shrinkflation watchdog and intelligence platform** — a consumer-first system that detects, verifies, and publishes evidence of products getting smaller while prices stay the same (or go up). It serves everyday shoppers who want transparency, journalists who need defensible data, and holds brands accountable for packaging changes.

### Why Rebuild?

The current system was built fast and taught us a lot, but it has fundamental problems that can't be fixed incrementally:

- **Security holes**: The admin panel runs in your browser and talks directly to the database with full write access. Anyone who figures out the password can modify any record.
- **Bad data identity**: Products scraped from Reddit get fake IDs like `REDDIT-abc123` instead of real barcodes (UPCs). This means the same Doritos bag reported by three different people becomes three different "products."
- **Low extraction quality**: The AI only successfully processes 1.7% of scraped records. The other 98.3% need manual review, which doesn't scale.
- **No evidence trail**: If someone asks "how do you know Cheerios went from 15oz to 13.5oz?", we can point to a Reddit post, but we can't prove it with product photos, receipts, or database records taken at different times.
- **Schema drift**: 15 migration files have accumulated patches on patches, making the database hard to reason about.

### What the Rebuild Fixes

Think of the old system like a notebook where you jotted down rumors about shrinkflation. The new system is more like a **courtroom evidence locker**:

1. **Every claim has evidence.** When we say "Brand X shrunk Product Y from 16oz to 14oz," we can show exactly where that information came from, when we captured it, and who reviewed it.

2. **Products have real identities.** Instead of fake Reddit IDs, products are identified by their actual UPC barcodes. When we can't find a barcode, we use fuzzy matching to connect reports about the same product.

3. **We watch products proactively.** Instead of only reacting when someone posts on Reddit, we take regular "snapshots" of product databases (like Open Food Facts) and retail APIs (like Kroger) to detect size changes automatically.

4. **Security is real.** All sensitive operations go through a proper backend. Your browser never gets database admin access.

5. **Data is legally defensible.** Immutable raw records, timestamped evidence, and audit trails mean the data could withstand scrutiny from brands, journalists, or regulators.

### Key Decisions Made

| Decision | Choice | Why |
|----------|--------|-----|
| Database | Supabase (keep) | You know it, it's cheap, it works |
| Frontend | Next.js on Vercel free tier | SEO for consumers, API routes for security, free hosting |
| Backend logic | Next.js API routes + Python workers | API routes for admin actions, Python for scrapers |
| Data sources | OFF + USDA + Kroger API + Reddit + News + GDELT | Free/cheap, reliable, complementary |
| Auth | Supabase Auth with Google OAuth | Real login, roles, row-level security |
| Storage | Supabase Storage | Evidence images, screenshots, receipts |
| CI/CD | GitHub Actions (keep) | Free, already set up |
| Budget target | ~$50/month steady state | Supabase Pro ($25) + Vercel free + LLM (~$25) |
| Scope | Size/quantity shrinkflation only | Measurable, defensible. Skimpflation deferred. |
| Primary UI focus | Brand-centric | Brand pages are first-class. 5 shrinkflation events = 5 on the brand. |
| Community features | Tips only (no upvotes) | Light crowdsourcing. Users can report but not vote. |
| Design system | Existing (`FULLCARTS_DESIGN_EXPORT.md`) | "Investigative Journalism meets Modern Product Design" — Space Grotesk, Inter, JetBrains Mono, dark graphite theme |
| Evidence standard | 3 levels (Verified/Confirmed/Reported) | Based on r/shrinkflation mod flowchart. Multi-source cross-referencing. |
| Data migration | Start fresh | Old Supabase project preserved but not migrated. |

---

## 2. Target Architecture

### The Big Picture (Non-Technical)

Imagine a factory assembly line for information:

```
[Raw Materials]  →  [Quality Check]  →  [Assembly]  →  [Inspection]  →  [Showroom]
  (scrapers)      (AI extraction)     (matching)     (human review)    (website)
```

**Raw Materials**: Scrapers pull in reports from Reddit, news articles, and food databases. These go into a "raw materials warehouse" (the `raw_items` table) and are **never modified** — like keeping the original receipt.

**Quality Check**: An AI reads each raw item and tries to extract specific claims: "Brand X changed Product Y from Size A to Size B." Each claim gets a confidence score. Low-confidence claims get flagged.

**Assembly**: The system tries to match claims to known products. "Is this the same Doritos bag someone else reported?" This is called "entity resolution" — figuring out that two different reports are talking about the same thing.

**Inspection**: You (and eventually community moderators) review the assembled evidence and either approve or reject it. Every decision is logged.

**Showroom**: Approved changes appear on the public website, with full evidence trails.

### Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                             │
│                                                                 │
│  Reddit      News/RSS    Open Food    Kroger     USDA    User   │
│  (scraper)   (scraper)   Facts API    API        API     Tips   │
│                                                                 │
└──────┬──────────┬──────────┬──────────┬─────────┬────────┬──────┘
       │          │          │          │         │        │
       ▼          ▼          ▼          ▼         ▼        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION LAYER                               │
│              (Python workers on GitHub Actions)                  │
│                                                                 │
│  • Idempotent writes (skip duplicates automatically)            │
│  • Cursor-based pagination (remembers where it left off)        │
│  • Writes to raw_items table via service_role                   │
│  • Never modifies raw data after initial write                  │
│                                                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   PROCESSING LAYER                               │
│              (Python workers on GitHub Actions)                  │
│                                                                 │
│  STEP 1: Extract Claims                                         │
│  • NLP + LLM reads raw_items                                    │
│  • Produces structured claims (brand, product, old_size,        │
│    new_size, price, evidence_url)                                │
│  • Each claim gets a confidence score (0-100)                   │
│                                                                 │
│  STEP 2: Resolve Entities                                       │
│  • Match claims to known products (by UPC, or fuzzy match)      │
│  • Create new product_entities when no match found              │
│  • Link claims to specific pack_variants                        │
│                                                                 │
│  STEP 3: Detect Changes                                         │
│  • Compare current variant observations against history         │
│  • Generate change_candidates for review                        │
│                                                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API LAYER                                     │
│              (Next.js API routes on Vercel)                      │
│                                                                 │
│  PUBLIC (no auth required):                                      │
│  • GET /api/products — browse products                          │
│  • GET /api/products/:id — product detail + timeline            │
│  • GET /api/changes — recent verified changes                   │
│  • GET /api/leaderboard — worst offenders                       │
│  • GET /api/stats — dashboard numbers                           │
│  • POST /api/tips — submit a tip (light crowdsourcing)          │
│                                                                 │
│  AUTHENTICATED (Supabase Auth required):                         │
│  • GET /api/admin/queue — review queue                          │
│  • POST /api/admin/review — approve/reject/edit                 │
│  • POST /api/admin/retract — mark false positive                │
│  • GET /api/admin/audit — audit log                             │
│                                                                 │
│  All writes use service_role key server-side.                    │
│  Frontend NEVER gets service_role access.                        │
│                                                                 │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND                                      │
│              (Next.js on Vercel free tier)                       │
│                                                                 │
│  PUBLIC PAGES (server-rendered for SEO):                         │
│  • Homepage — stats, recent changes, trending                   │
│  • Product pages — /products/:slug with timeline chart          │
│  • Brand pages — /brands/:slug with all products                │
│  • Leaderboard — worst offenders ranked                         │
│  • News — shrinkflation articles                                │
│  • About — methodology, data sources                            │
│                                                                 │
│  ADMIN PAGES (client-side, behind auth):                         │
│  • Review queue — approve/reject/edit staged claims             │
│  • Evidence viewer — photos, screenshots, source links          │
│  • Audit log — who changed what, when                           │
│                                                                 │
│  INTERACTIVE FEATURES:                                           │
│  • Search — full-text product search                            │
│  • QR scanner — scan barcode → product page                     │
│  • Tip submission — report shrinkflation (no account needed)    │
│  • Upvoting — confirm a report (session-based)                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Trust Boundaries

**Think of trust boundaries like security checkpoints.** Different parts of the system have different levels of access, and data must pass through a checkpoint to move between them.

```
┌─────────────────────────────────────────────────────┐
│  TRUSTED ZONE (service_role — full database access)  │
│                                                     │
│  • Python scrapers (run on GitHub Actions)          │
│  • Next.js API routes (run on Vercel server-side)   │
│  • Supabase Edge Functions (run on Supabase)        │
│                                                     │
│  These are the ONLY things that can write to the    │
│  database. They run on servers you control, not     │
│  in anyone's browser.                               │
│                                                     │
├─────────────── SECURITY CHECKPOINT ─────────────────┤
│                                                     │
│  AUTHENTICATED ZONE (user has logged in)             │
│                                                     │
│  • Admin dashboard (your browser, after login)      │
│  • Reviewer dashboard (wife's browser, after login) │
│  • Future: community moderators                     │
│                                                     │
│  Can READ review queue and submit review decisions  │
│  via API routes. Cannot write directly to database. │
│                                                     │
├─────────────── SECURITY CHECKPOINT ─────────────────┤
│                                                     │
│  PUBLIC ZONE (anyone on the internet)                │
│                                                     │
│  • Website visitors                                 │
│  • API consumers (future)                           │
│                                                     │
│  Can READ published data only.                      │
│  Can submit tips and upvotes (rate-limited).        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Failure Modes & Recovery

| What breaks | Impact | Auto-recovery | Manual fix |
|-------------|--------|---------------|------------|
| Scraper can't reach Reddit | No new Reddit data | Retries with backoff, runs again next scheduled cycle | Check API status, adjust source |
| Kroger API rate limited | No new retail snapshots | Backs off automatically, resumes next day | Reduce polling frequency |
| LLM extraction API down | Claims don't get extracted | Queue builds up, processes when API returns | Check Anthropic status |
| Supabase down | Entire site offline | Supabase handles recovery | Contact Supabase support |
| Vercel down | Frontend offline, APIs offline | Supabase data safe, Vercel auto-recovers | Check Vercel status |
| Bad data promoted | Incorrect info on public site | — | Admin retracts via audit trail |
| GitHub Actions quota hit | Scrapers stop running | Wait for monthly reset | Optimize runner time usage |

---

## 3. Data Model

### The Core Concept (Non-Technical)

Think of the data model like a filing system at a law firm:

- **Evidence Locker** (`raw_items`): The original documents. Never altered. If a Reddit post says "Doritos went from 9.5oz to 9.25oz", that exact text is preserved forever.

- **Case Notes** (`claims`): What the lawyer (AI) extracted from the evidence. "Brand: Doritos, Old Size: 9.5oz, New Size: 9.25oz, Confidence: 72%". These are interpretations, not raw evidence.

- **Client Files** (`product_entities` + `pack_variants`): The actual products being tracked. "Doritos Nacho Cheese" is the entity. "Doritos Nacho Cheese 9.25oz bag" is a specific pack variant.

- **Observation Log** (`variant_observations`): What we've seen about each pack variant over time. "On Jan 2024, Kroger listed this as 9.5oz for $4.29. On Mar 2024, Kroger listed it as 9.25oz for $4.49."

- **Change Reports** (`change_candidates`): Detected differences that need human review. "This product appears to have shrunk 2.6%."

- **Published Record** (`published_changes`): Changes that passed review and are shown on the website. These are the "verdicts."

### Why This Structure Matters

The old system jumped straight from "Reddit post" to "product record." If the Reddit post had bad information, the product record was wrong, and there was no way to trace back to figure out what went wrong.

The new system keeps every step separate:
1. We always have the original evidence (raw_items)
2. We can see exactly what the AI extracted (claims) and how confident it was
3. We can see how we matched the claim to a product (entity resolution)
4. We can see every observation over time (the timeline that proves shrinkflation)
5. We can see who approved each change and when (audit trail)

If a brand challenges our data, we can walk them through the entire chain: "Here's the original source. Here's what our AI extracted. Here's the corroborating evidence from 3 other sources. Here's when our reviewer verified it."

### Entity-Relationship Diagram

```
raw_items (immutable evidence)
    │
    │ 1 raw_item → many claims
    ▼
claims (AI-extracted, per-field confidence)
    │
    │ many claims → 1 product_entity (via entity resolution)
    ▼
product_entities (canonical products, e.g. "Doritos Nacho Cheese")
    │
    │ 1 entity → many pack_variants
    ▼
pack_variants (specific SKUs, e.g. "Doritos Nacho Cheese 9.25oz bag")
    │
    │ 1 variant → many observations
    ▼
variant_observations (time-series snapshots: size, price, date, source)
    │
    │ compared over time → change_candidates
    ▼
change_candidates (detected size/price changes, pending review)
    │
    │ approved by reviewer → published_changes
    ▼
published_changes (verified, public-facing shrinkflation events)

Supporting tables:
  evidence_files → attached to raw_items, claims, or observations
  review_actions → audit trail of every reviewer decision
  tips → community-submitted reports (go into raw_items)
  upvotes → community confirmation of published changes
```

### Table Definitions

#### raw_items — The Evidence Locker

This table stores the original, unmodified source material. Once a row is inserted, it is **never updated or deleted.** This is the foundation of data defensibility.

```sql
CREATE TABLE raw_items (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    source_type     TEXT NOT NULL,
        -- 'reddit', 'news', 'openfoodfacts', 'kroger_api',
        -- 'usda', 'community_tip', 'receipt'
    source_id       TEXT NOT NULL,
        -- Unique ID from the source (Reddit post ID, article URL,
        -- OFF barcode, Kroger product ID, etc.)
    source_url      TEXT,
        -- Link to the original source (Reddit post URL, article URL)
    captured_at     TIMESTAMPTZ DEFAULT now() NOT NULL,
        -- When WE captured this data
    source_date     TIMESTAMPTZ,
        -- When the SOURCE created it (post date, article publish date)
    raw_payload     JSONB NOT NULL,
        -- The complete, unmodified source data as JSON.
        -- For Reddit: {title, selftext, score, subreddit, author, url, ...}
        -- For OFF: {product_name, brands, quantity, nutriments, ...}
        -- For Kroger: {description, brand, size, price, upc, storeId, ...}
    content_hash    TEXT NOT NULL,
        -- SHA-256 hash of raw_payload for deduplication
    scraper_version TEXT NOT NULL,
        -- Version of the scraper that captured this (e.g. "reddit-v2.1")
        -- Enables reproducibility: you know which code processed this

    UNIQUE (source_type, source_id)
        -- Prevents ingesting the same source item twice
);

CREATE INDEX idx_raw_items_source_type ON raw_items (source_type);
CREATE INDEX idx_raw_items_captured_at ON raw_items (captured_at);
CREATE INDEX idx_raw_items_content_hash ON raw_items (content_hash);
```

**What goes in raw_payload?** Everything. The full Reddit post with title, body, score, subreddit, images. The full Open Food Facts product record. The full Kroger API response. We never throw away source data.

#### claims — What the AI Extracted

Each raw_item can produce zero or more claims. A claim is a structured assertion like "Brand X changed Product Y from Size A to Size B."

```sql
CREATE TABLE claims (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    raw_item_id         UUID NOT NULL REFERENCES raw_items(id),
    extractor_version   TEXT NOT NULL,
        -- Version of the extraction code (e.g. "nlp-v3.0", "claude-haiku-v1")
        -- If we improve extraction later, we can re-run on old raw_items
    extracted_at        TIMESTAMPTZ DEFAULT now() NOT NULL,

    -- The extracted fields (all nullable — we only fill what we find)
    brand               TEXT,
    product_name        TEXT,
    category            TEXT,
    old_size            NUMERIC,
    old_size_unit       TEXT,        -- oz, g, ml, ct, etc.
    new_size            NUMERIC,
    new_size_unit       TEXT,
    old_price           NUMERIC,
    new_price           NUMERIC,
    retailer            TEXT,
    upc                 TEXT,        -- If a barcode was found/mentioned
    observed_date       DATE,        -- When the change was observed
    change_description  TEXT,        -- Free-text summary of the change

    -- Per-field confidence scores (0.0 to 1.0)
    -- This replaces the single "confidence_score" from the old system.
    -- Now we know WHICH fields are reliable and which are guesses.
    confidence          JSONB NOT NULL DEFAULT '{}',
        -- Example: {
        --   "brand": 0.95,
        --   "product_name": 0.80,
        --   "old_size": 0.70,
        --   "new_size": 0.85,
        --   "overall": 0.72
        -- }

    -- Processing status
    status              TEXT NOT NULL DEFAULT 'pending',
        -- 'pending' → awaiting entity resolution
        -- 'matched' → linked to a product_entity
        -- 'unmatched' → couldn't match, needs manual help
        -- 'discarded' → too low quality to use

    matched_entity_id   UUID REFERENCES product_entities(id),
    matched_variant_id  UUID REFERENCES pack_variants(id),

    UNIQUE (raw_item_id, extractor_version)
        -- One extraction per raw_item per extractor version.
        -- If we re-extract with a new version, it creates a new claim.
);

CREATE INDEX idx_claims_raw_item ON claims (raw_item_id);
CREATE INDEX idx_claims_status ON claims (status);
CREATE INDEX idx_claims_brand ON claims (lower(brand));
CREATE INDEX idx_claims_upc ON claims (upc) WHERE upc IS NOT NULL;
```

**Why per-field confidence?** The old system had one number (0-100) for the whole record. But sometimes the AI is 95% sure about the brand but only 30% sure about the old size. Per-field confidence lets us accept the parts we trust and flag the parts we don't.

#### product_entities — Canonical Products

This is the "phone book" of products. Each entity represents a distinct product regardless of pack size.

```sql
CREATE TABLE product_entities (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    canonical_name  TEXT NOT NULL,
        -- The "official" name: "Doritos Nacho Cheese Tortilla Chips"
    brand           TEXT NOT NULL,
    category        TEXT,
    manufacturer    TEXT,
        -- Parent company (e.g., "PepsiCo" for Doritos)
    image_url       TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL,

    -- Search optimization
    name_tokens     TSVECTOR GENERATED ALWAYS AS (
        to_tsvector('english', canonical_name || ' ' || brand)
    ) STORED
);

CREATE INDEX idx_entities_brand ON product_entities (lower(brand));
CREATE INDEX idx_entities_name_search ON product_entities USING GIN (name_tokens);
```

**Why separate from pack_variants?** Because "Doritos Nacho Cheese" comes in a 1oz bag, a 9.25oz bag, a 14.5oz bag, and a party size. These are different SKUs of the same product. Shrinkflation happens at the variant level (the 9.5oz bag becomes 9.25oz), but we want to show all variants on one product page.

#### pack_variants — Specific SKUs

A pack variant is a specific purchasable item with a UPC barcode.

```sql
CREATE TABLE pack_variants (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    entity_id       UUID NOT NULL REFERENCES product_entities(id),
    upc             TEXT UNIQUE,
        -- The real barcode. NULL if we don't have it yet.
    variant_name    TEXT NOT NULL,
        -- Descriptive: "Doritos Nacho Cheese 9.25oz Bag"
    current_size    NUMERIC,
    size_unit       TEXT,
    item_count      INTEGER,
        -- For multi-packs: "12-pack of 1oz bags" → item_count = 12
    is_active       BOOLEAN DEFAULT true,
        -- False if this variant has been discontinued
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_variants_entity ON pack_variants (entity_id);
CREATE INDEX idx_variants_upc ON pack_variants (upc) WHERE upc IS NOT NULL;
```

#### variant_observations — Time-Series Snapshots

This is where the "recurring monthly snapshots" happen. Every time we see a product's size or price, we record it here. Over time, this builds a history that reveals shrinkflation.

```sql
CREATE TABLE variant_observations (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    variant_id      UUID NOT NULL REFERENCES pack_variants(id),
    observed_date   DATE NOT NULL,
    source_type     TEXT NOT NULL,
        -- Where this observation came from:
        -- 'openfoodfacts', 'kroger_api', 'usda', 'reddit_claim',
        -- 'community_tip', 'receipt', 'manual'
    source_ref      TEXT,
        -- Reference to the source (OFF barcode, Kroger product ID, etc.)

    -- What we observed
    size            NUMERIC,
    size_unit       TEXT,
    price           NUMERIC,
    price_per_unit  NUMERIC GENERATED ALWAYS AS (
        CASE WHEN size > 0 THEN price / size ELSE NULL END
    ) STORED,
    retailer        TEXT,
    store_location  TEXT,
        -- For retailer observations: which specific store

    -- Evidence
    evidence_url    TEXT,
        -- Link to source (product page, receipt photo, etc.)
    evidence_file_id UUID REFERENCES evidence_files(id),
    raw_item_id     UUID REFERENCES raw_items(id),
        -- Link back to the raw evidence, if applicable

    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (variant_id, observed_date, source_type, retailer)
        -- One observation per variant, per date, per source, per retailer
);

CREATE INDEX idx_observations_variant ON variant_observations (variant_id);
CREATE INDEX idx_observations_date ON variant_observations (observed_date);
```

**This is the heart of the "Product Observatory" concept.** Every month, our scrapers check Open Food Facts, Kroger, and USDA for the latest product sizes and prices. Each check creates a new observation row. When an observation shows a different size than the previous one for the same variant — that's a shrinkflation signal.

#### change_candidates — Detected Changes Pending Review

When the system detects that a variant's size changed between observations, it creates a change candidate.

```sql
CREATE TABLE change_candidates (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    variant_id          UUID NOT NULL REFERENCES pack_variants(id),
    observation_before  UUID NOT NULL REFERENCES variant_observations(id),
    observation_after   UUID NOT NULL REFERENCES variant_observations(id),

    -- Computed deltas
    size_before         NUMERIC NOT NULL,
    size_after          NUMERIC NOT NULL,
    size_delta_pct      NUMERIC NOT NULL,
        -- e.g., -5.26 means the product shrunk 5.26%
    price_before        NUMERIC,
    price_after         NUMERIC,
    ppu_delta_pct       NUMERIC,
        -- Price-per-unit change percentage

    -- Classification
    change_type         TEXT NOT NULL,
        -- 'shrinkflation' — size down, price same or up
        -- 'downsizing' — size down, price also down (proportionally)
        -- 'upsizing' — size up
        -- 'price_hike' — size same, price up
        -- 'restoration' — size went back up (brand did the right thing)
    severity            TEXT NOT NULL,
        -- 'minor' (< 5%), 'moderate' (5-15%), 'major' (> 15%)
    is_shrinkflation    BOOLEAN NOT NULL,

    -- Review status
    status              TEXT NOT NULL DEFAULT 'pending',
        -- 'pending' → awaiting review
        -- 'approved' → verified, will be published
        -- 'rejected' → not a real change (reviewer determined)
        -- 'false_positive' → was approved, later found incorrect
    reviewed_by         UUID REFERENCES auth.users(id),
    reviewed_at         TIMESTAMPTZ,
    review_notes        TEXT,

    -- Supporting evidence
    supporting_claims   UUID[] DEFAULT '{}',
        -- Array of claim IDs that corroborate this change
    evidence_count      INTEGER DEFAULT 0,
        -- Number of independent sources confirming this

    created_at          TIMESTAMPTZ DEFAULT now() NOT NULL,

    UNIQUE (observation_before, observation_after)
);

CREATE INDEX idx_candidates_variant ON change_candidates (variant_id);
CREATE INDEX idx_candidates_status ON change_candidates (status);
CREATE INDEX idx_candidates_created ON change_candidates (created_at);
```

#### published_changes — The Public Record

Only approved changes make it here. This is what the website shows.

```sql
CREATE TABLE published_changes (
    id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    candidate_id        UUID NOT NULL REFERENCES change_candidates(id) UNIQUE,
    variant_id          UUID NOT NULL REFERENCES pack_variants(id),
    entity_id           UUID NOT NULL REFERENCES product_entities(id),

    -- Snapshot of the key facts (denormalized for fast reads)
    brand               TEXT NOT NULL,
    product_name        TEXT NOT NULL,
    size_before         NUMERIC NOT NULL,
    size_after          NUMERIC NOT NULL,
    size_unit           TEXT NOT NULL,
    size_delta_pct      NUMERIC NOT NULL,
    change_type         TEXT NOT NULL,
    severity            TEXT NOT NULL,
    observed_date       DATE NOT NULL,

    -- Evidence summary
    evidence_summary    JSONB NOT NULL DEFAULT '[]',
        -- Array of evidence references:
        -- [{source: "reddit", url: "...", date: "..."},
        --  {source: "openfoodfacts", snapshot_date: "...", old_qty: "...", new_qty: "..."},
        --  {source: "kroger_api", store: "...", old_size: "...", new_size: "..."}]

    -- Retraction support
    is_retracted        BOOLEAN DEFAULT false,
    retracted_at        TIMESTAMPTZ,
    retracted_by        UUID REFERENCES auth.users(id),
    retraction_reason   TEXT,

    -- Community engagement
    upvote_count        INTEGER DEFAULT 0,

    published_at        TIMESTAMPTZ DEFAULT now() NOT NULL,
    published_by        UUID REFERENCES auth.users(id)
);

CREATE INDEX idx_published_entity ON published_changes (entity_id);
CREATE INDEX idx_published_brand ON published_changes (lower(brand));
CREATE INDEX idx_published_date ON published_changes (published_at);
CREATE INDEX idx_published_severity ON published_changes (severity);
CREATE INDEX idx_published_type ON published_changes (change_type);
```

#### evidence_files — Stored Evidence

Images, screenshots, and other files stored in Supabase Storage.

```sql
CREATE TABLE evidence_files (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    storage_path    TEXT NOT NULL,
        -- Path in Supabase Storage bucket
    file_type       TEXT NOT NULL,
        -- 'image', 'screenshot', 'receipt', 'document'
    mime_type       TEXT NOT NULL,
    file_hash       TEXT NOT NULL,
        -- SHA-256 of file content for integrity verification
    file_size_bytes INTEGER NOT NULL,
    caption         TEXT,
    uploaded_by     TEXT,
        -- 'scraper:reddit-v2', 'user:anonymous', 'admin:reviewer1'
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);
```

#### review_actions — Complete Audit Trail

Every reviewer action is logged here. This is separate from the review fields on change_candidates because we want to track the full history of reviews, not just the latest one.

```sql
CREATE TABLE review_actions (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    target_type     TEXT NOT NULL,
        -- 'claim', 'change_candidate', 'published_change', 'tip'
    target_id       UUID NOT NULL,
    action          TEXT NOT NULL,
        -- 'approve', 'reject', 'edit', 'retract', 'escalate', 'reassign'
    reviewer_id     UUID NOT NULL REFERENCES auth.users(id),
    previous_state  JSONB,
        -- Snapshot before the action (for undo/audit)
    new_state       JSONB,
        -- Snapshot after the action
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_review_actions_target ON review_actions (target_type, target_id);
CREATE INDEX idx_review_actions_reviewer ON review_actions (reviewer_id);
CREATE INDEX idx_review_actions_created ON review_actions (created_at);
```

#### tips — Community Submissions

Light crowdsourcing: users can submit tips without creating an account.

```sql
CREATE TABLE tips (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id      TEXT NOT NULL,
        -- Anonymous session tracking (no PII)
    brand           TEXT,
    product_name    TEXT,
    description     TEXT NOT NULL,
    evidence_url    TEXT,
    evidence_file_id UUID REFERENCES evidence_files(id),
    status          TEXT NOT NULL DEFAULT 'pending',
        -- 'pending', 'converted' (became a raw_item), 'dismissed'
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL,
    ip_hash         TEXT
        -- Hashed IP for rate-limiting, not stored as PII
);
```

#### upvotes — Community Confirmation (DEFERRED)

Upvoting is deferred to a post-90-day phase. The `published_changes.upvote_count` field is kept in the schema for future use but will default to 0.

### Key Views

```sql
-- Product detail page: full history for one product
CREATE VIEW product_timeline AS
SELECT
    pe.id AS entity_id,
    pe.canonical_name,
    pe.brand,
    pv.id AS variant_id,
    pv.variant_name,
    pv.upc,
    vo.observed_date,
    vo.size,
    vo.size_unit,
    vo.price,
    vo.price_per_unit,
    vo.source_type,
    vo.retailer
FROM product_entities pe
JOIN pack_variants pv ON pv.entity_id = pe.id
JOIN variant_observations vo ON vo.variant_id = pv.id
ORDER BY pe.id, pv.id, vo.observed_date;

-- Leaderboard: worst offenders ranked by cumulative shrinkage
CREATE VIEW shrinkflation_leaderboard AS
SELECT
    pe.id AS entity_id,
    pe.canonical_name,
    pe.brand,
    COUNT(pc.id) AS shrinkflation_count,
    SUM(pc.size_delta_pct) AS total_shrinkage_pct,
    MIN(pc.observed_date) AS first_detected,
    MAX(pc.observed_date) AS last_detected
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE pc.is_retracted = false
  AND pc.change_type = 'shrinkflation'
GROUP BY pe.id, pe.canonical_name, pe.brand
ORDER BY total_shrinkage_pct ASC;  -- Most negative = most shrunk

-- Brand scorecard: primary UI view — all shrinkflation events for a brand
CREATE VIEW brand_scorecard AS
SELECT
    pe.brand,
    COUNT(DISTINCT pe.id) AS product_count,
    COUNT(pc.id) AS total_events,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'shrinkflation') AS shrinkflation_events,
    COUNT(pc.id) FILTER (WHERE pc.change_type = 'restoration') AS restoration_events,
    SUM(pc.size_delta_pct) FILTER (WHERE pc.change_type = 'shrinkflation') AS total_shrinkage_pct,
    MIN(pc.observed_date) AS first_detected,
    MAX(pc.observed_date) AS last_detected
FROM product_entities pe
JOIN published_changes pc ON pc.entity_id = pe.id
WHERE pc.is_retracted = false
GROUP BY pe.brand
ORDER BY shrinkflation_events DESC;

-- Good news: restorations (brands that reversed shrinkflation)
CREATE VIEW restorations AS
SELECT
    pc.id,
    pc.brand,
    pc.product_name,
    pc.size_before,
    pc.size_after,
    pc.size_unit,
    pc.observed_date,
    pc.evidence_summary,
    pc.published_at
FROM published_changes pc
WHERE pc.change_type = 'restoration'
  AND pc.is_retracted = false
ORDER BY pc.published_at DESC;

-- Dashboard stats
CREATE VIEW dashboard_stats AS
SELECT
    (SELECT COUNT(*) FROM product_entities) AS total_products,
    (SELECT COUNT(*) FROM published_changes WHERE NOT is_retracted) AS total_changes,
    (SELECT COUNT(*) FROM published_changes
     WHERE NOT is_retracted AND change_type = 'shrinkflation') AS shrinkflation_events,
    (SELECT COUNT(*) FROM change_candidates WHERE status = 'pending') AS pending_review,
    (SELECT COUNT(*) FROM claims WHERE status = 'pending') AS pending_claims,
    (SELECT COUNT(*) FROM raw_items
     WHERE captured_at > now() - INTERVAL '7 days') AS items_ingested_7d;
```

---

## 4. Ingestion Strategy

### The Core Principle: Separate Collection from Interpretation

The old system did everything in one step: scrape a Reddit post, extract data from it, and insert a product record — all in the same script. This meant:
- If the AI extracted wrong data, the product record was wrong
- There was no way to re-process old posts with a better extraction algorithm
- Different sources (Reddit, news, OFF) used different code paths

The new system **strictly separates collection from interpretation**:

1. **Collection** (scrapers) puts raw data into `raw_items`. Period. No interpretation.
2. **Extraction** (a separate process) reads `raw_items` and creates `claims`.
3. **Resolution** (another process) matches `claims` to `product_entities`.

This means we can always re-run extraction on old data if we improve the AI, without re-scraping.

### Source-by-Source Ingestion

#### Reddit Scraper (keep and simplify)

The current scraper is solid for fetching posts. What changes:
- **Output**: Instead of writing to `reddit_staging`, write to `raw_items` with `source_type='reddit'`
- **No extraction**: The scraper just saves the raw post. A separate job extracts claims.
- **Deduplication**: `UNIQUE(source_type, source_id)` with `source_id = post_id` prevents re-ingestion.
- **Cursor**: Track last-processed timestamp in a `scraper_state` table, not a file artifact.

```python
# Simplified flow:
# 1. Fetch posts from Arctic Shift / Reddit JSON
# 2. For each post, insert into raw_items (skip if exists)
# 3. Update cursor in scraper_state
# That's it. No NLP, no confidence scoring, no tiering.
```

**Schedule**: Daily via GitHub Actions (same as now)

#### Open Food Facts Snapshotter (new approach)

Instead of checking specific products, take monthly snapshots of the entire relevant database:

```python
# Monthly job:
# 1. Download OFF daily CSV export (~2GB)
# 2. Filter to US products with barcodes
# 3. For each product, compare quantity field against last snapshot
# 4. If quantity changed → insert into raw_items with source_type='openfoodfacts'
# 5. Store the snapshot hash for next comparison
```

For daily monitoring of tracked products:
```python
# Daily job:
# 1. For each UPC in pack_variants table
# 2. Query OFF API: GET /api/v2/product/{upc}.json
# 3. Compare product_quantity against latest variant_observation
# 4. If different → insert raw_item + create observation directly
```

**Schedule**: Daily spot-checks + monthly full snapshot
**Rate limits**: OFF asks for <100 req/min. With 500 tracked products, daily checks take ~5 minutes.
**Cost**: Free

#### Kroger API Poller (new)

This is the "monthly snapshot of products at a real retailer" you described.

```python
# Weekly job:
# 1. For each UPC in pack_variants table
# 2. Query Kroger API: GET /v1/products?filter.term={upc}&filter.locationId={store}
# 3. Record: price, size description, availability
# 4. Insert into raw_items with source_type='kroger_api'
# 5. Also insert directly into variant_observations
```

**Schedule**: Weekly (enough to catch changes, won't burn rate limits)
**Rate limits**: 10,000 req/day free tier. 500 products × 2 stores = 1,000 req/week.
**Cost**: Free (requires developer registration)

#### USDA FoodData Central (new)

Quarterly snapshot of branded food products:

```python
# Quarterly job:
# 1. Download USDA Branded Foods bulk data (~1.5GB JSON)
# 2. Filter to products with UPCs matching our pack_variants
# 3. Compare packageWeight against our records
# 4. If different → create raw_item
# 5. Cross-reference ingredients for quality-shrinkflation detection
```

**Schedule**: Quarterly (USDA updates in bulk releases)
**Cost**: Free

#### News Scraper (keep and enhance)

```python
# Every 12 hours:
# 1. Query GDELT API for recent shrinkflation articles (free, no auth)
# 2. Query Google News RSS (current approach, keep)
# 3. For each article, insert into raw_items with source_type='news'
# 4. Extraction job will later pull product mentions from article text
```

**New addition**: GDELT gives us global coverage and sentiment scoring for free.

#### Community Tips (new)

When a user submits a tip through the website:
```
POST /api/tips
Body: { brand, product_name, description, evidence_url }
→ Inserts into tips table
→ Auto-converts to raw_item with source_type='community_tip'
→ Goes through same extraction pipeline as everything else
```

### Idempotency & Cursors

Every scraper uses the same pattern:

```
1. Check scraper_state table for last cursor (timestamp, page number, etc.)
2. Fetch new data since cursor
3. For each item:
   a. Compute content_hash = SHA-256(raw_payload)
   b. INSERT INTO raw_items ... ON CONFLICT (source_type, source_id) DO NOTHING
   c. If inserted (not a duplicate), log it
4. Update cursor in scraper_state
```

The `ON CONFLICT DO NOTHING` clause means the same item can never be inserted twice. The content_hash lets us detect if the same source_id has different content (meaning the source was updated).

```sql
CREATE TABLE scraper_state (
    scraper_name    TEXT PRIMARY KEY,
        -- 'reddit_recent', 'reddit_backfill', 'off_daily', 'kroger_weekly', etc.
    last_cursor     JSONB NOT NULL DEFAULT '{}',
        -- Flexible cursor: {timestamp: "2026-03-09T00:00:00Z", page: 5}
    last_run_at     TIMESTAMPTZ,
    last_run_status TEXT,
        -- 'success', 'partial', 'failed'
    items_processed INTEGER DEFAULT 0,
    updated_at      TIMESTAMPTZ DEFAULT now()
);
```

### Source Priority for Observations

When the same product is observed by multiple sources, we prioritize:

| Priority | Source | Why |
|----------|--------|-----|
| 1 | Kroger API | Real retail data with exact pricing |
| 2 | Open Food Facts | Community-verified product data with barcodes |
| 3 | USDA FoodData Central | Government-verified, but updated slowly |
| 4 | Reddit claims | Anecdotal but often first to spot changes |
| 5 | News articles | Usually reporting what's already known |
| 6 | Community tips | Unverified, lowest confidence |

Changes corroborated by multiple sources get higher evidence scores.

---

## 5. Data Quality Framework

### The Fundamental Problem with the Current System

The current LLM extraction auto-approves only 1.7% of records. This isn't a tuning problem — it's an **architecture problem**. The system tries to do too much in one step:

1. Read a Reddit post
2. Extract brand, product, old size, new size, price
3. Score confidence
4. Decide whether to auto-approve

Steps 2-4 are unreliable because Reddit posts are messy, ambiguous, and inconsistent. "Doritos bag is smaller now smh" has no sizes at all, but it's still a valid shrinkflation signal.

### The New Approach: Tiered Confidence

Instead of a single pass/fail threshold, the new system uses **three quality tiers** with different evidence requirements:

#### Tier 1: Automated Detection (high confidence, no human review needed)

These are changes detected by comparing structured data sources — not from social media.

**Example**: Open Food Facts shows that UPC 028400090858 (Doritos Nacho Cheese) had `product_quantity: "277.1 g"` in January and `product_quantity: "262.2 g"` in March.

**Evidence requirements**:
- Size change detected in a structured database (OFF, USDA, or Kroger)
- At least 2 observations at the old size AND 2 at the new size
- No conflicting data from other sources

**Action**: Auto-publish with a "database-verified" badge. No human review needed.

This is how the monthly snapshots become powerful: when we see the same product at the same size for months, then suddenly it changes, we know with near-certainty that shrinkflation happened.

#### Tier 2: Corroborated Claims (medium confidence, quick review)

These are changes supported by multiple independent sources.

**Example**: A Reddit post says "Cheerios went from 15oz to 13.5oz." A news article confirms this. Open Food Facts doesn't show the change yet.

**Evidence requirements**:
- At least 2 independent sources mentioning the same change
- Brand and product name extraction confidence > 0.7
- Size extraction confidence > 0.5 in at least one source

**Action**: Goes to review queue with a "likely real" flag. Reviewer just confirms — minimal effort.

#### Tier 3: Single-Source Claims (low confidence, full review needed)

These are claims from a single source, typically Reddit.

**Example**: A Reddit post says "I think my chips bag got smaller."

**Evidence requirements**: Anything with extracted data goes here if it doesn't meet Tier 1 or Tier 2 requirements.

**Action**: Goes to review queue. Reviewer must verify all fields and may need to do their own research.

### Confidence Scoring (Per-Field)

Instead of one number for the whole record, we score each field independently:

```json
{
    "brand": {
        "value": "General Mills",
        "confidence": 0.95,
        "source": "nlp_brand_list_match"
    },
    "product_name": {
        "value": "Cheerios Original",
        "confidence": 0.80,
        "source": "nlp_context_extraction"
    },
    "old_size": {
        "value": 15,
        "confidence": 0.70,
        "source": "regex_pattern_match",
        "pattern": "used to be {X}oz"
    },
    "new_size": {
        "value": 13.5,
        "confidence": 0.85,
        "source": "regex_pattern_match",
        "pattern": "now it's {X}oz"
    },
    "overall": 0.72
}
```

**Why this matters for your review workflow**: When you open a claim in the review queue, you can see at a glance which fields the AI is confident about (green) and which it's unsure about (yellow/red). You only need to verify the uncertain fields, not everything.

### Evidence Requirements by Source

| Source | Minimum Evidence for Publication |
|--------|----------------------------------|
| Structured DB (OFF, USDA, Kroger) | 2+ observations at old size, 2+ at new size |
| Reddit + corroboration | Reddit claim + 1 other source agreeing |
| Reddit alone | Full human review + admin marks "verified" |
| News article | Link to article + extracted product matches known entity |
| Community tip | Human review required, must have supporting evidence |

### Reviewer Workflow

**The Review Queue** shows pending change_candidates, prioritized by:
1. Evidence count (more evidence = review first, because it's easier to confirm)
2. Severity (major changes first — they're most newsworthy)
3. Age (older items bubble up to prevent staleness)

**For each item, the reviewer sees**:
- The detected change (before/after sizes, calculated shrinkage %)
- All supporting evidence (raw sources, claims, observations)
- Confidence scores per field
- Suggested action (approve/reject) based on evidence tier

**Reviewer actions**:
- **Approve** → change moves to `published_changes`, shown on website
- **Reject** → change is dismissed with reason logged
- **Edit & Approve** → reviewer corrects any fields, then approves
- **Escalate** → flag for deeper investigation (e.g., verify with brand)
- **Merge** → combine with another change_candidate for the same product

**After publication, retractions are supported**:
- **Retract** → mark as false positive with reason. Not deleted — flagged as retracted and hidden from public views. Full audit trail preserved.

### Fixing the 1.7% Auto-Approve Rate

The extraction quality problem has three root causes, and fixing them dramatically reduces the review workload:

1. **Reddit posts are messy.** "My chips are smaller now" contains no extractable sizes. This is expected — not every post is a data point. The fix: **don't try to extract structured data from every post.** Instead, classify posts first:
   - Type A: Explicit size comparison ("went from 16oz to 14oz") → extract with regex
   - Type B: Product mention with photo → use vision API to read label
   - Type C: General complaint → save as raw_item but don't expect structured claims
   - Type D: Off-topic / meme → discard

2. **The NLP parser tries to do too much.** Instead of one big regex-based parser, use a pipeline:
   - Step 1: Simple keyword filter ("smaller", "shrunk", "less", "reduced", brand names)
   - Step 2: If keywords found, try regex extraction for explicit patterns
   - Step 3: If regex fails, try Claude Haiku for structured extraction (it's $0.25 per million input tokens — very cheap for this)
   - Step 4: If Claude also unsure, save with low confidence for human review

3. **The confidence threshold is wrong.** The old system auto-approves at fields_found >= 3 + brand + explicit pattern. This is too strict for auto-approval but too loose for quality. The fix: **don't auto-approve Reddit claims at all.** Auto-approve only when structured databases (OFF, Kroger, USDA) confirm the change. Reddit claims that corroborate an already-detected change are auto-linked as additional evidence.

### Review Workload: Why It's Manageable

**You will NOT be reviewing 17,000 records.** Here's the realistic math:

| Stage | Records | What happens |
|-------|---------|-------------|
| Raw Reddit posts ingested | ~17,000 | Stored as raw_items. No review needed. |
| After classification (Type D removed) | ~12,000 | Off-topic/memes auto-discarded |
| After classification (Type C removed) | ~4,000 | General complaints stored but don't produce claims |
| Claims with extractable data (Types A+B) | ~3,000 | These enter the claims pipeline |
| Claims corroborated by OFF/Kroger/USDA | ~500-1,000 | Auto-promoted (no review needed) |
| **Claims needing manual review** | **~2,000-2,500** | Your actual review queue |

At a pace of **10-20 reviews per day** (streamlined with batch review UI), you'd clear the initial backlog in 4-6 months while new items trickle in slowly.

**Batch review** further reduces effort: when 5 Reddit posts all mention "Cheerios went from 15oz to 13.5oz", they appear as **one grouped review item**, not five separate ones. You approve once, and all 5 claims are linked.

**The long-term steady state** is even lighter: once structured sources (OFF, Kroger) are taking regular snapshots, most changes are auto-detected. Reddit mostly corroborates what's already known. Your daily review queue might be 2-5 items.

### False-Positive and Retraction Handling

When a published change turns out to be wrong:

1. Reviewer clicks "Retract" and enters a reason
2. The `published_changes` row gets `is_retracted = true`
3. A `review_actions` row logs the retraction
4. The change disappears from all public views
5. The change stays in the database for audit purposes
6. If the product only had this one change, it drops off the leaderboard

When a brand disputes our data:
1. We can show them the complete evidence chain (raw_items → claims → observations → change)
2. If their evidence is compelling, we retract
3. If it's debatable, we add their response to the evidence_summary
4. All interactions logged in review_actions

### Evidence Standard: Three Trust Levels

Every published change carries one of three trust levels, displayed as a badge on the website.

#### Level 1: "Verified" (highest trust — green badge)

Requires **at least TWO** of these independent evidence types:
- Photo showing the old product label with size printed
- Photo showing the new product label with size printed
- Structured database record at the old size (OFF, Kroger, USDA)
- Structured database record at the new size
- News article from a credible Tier 1 or Tier 2 outlet reporting the specific change with numbers

**Key rule (from r/shrinkflation moderators)**: There must be evidence of BOTH the old AND new sizes. Not just one. This matches the community's own standard for valid shrinkflation reporting.

#### Level 2: "Confirmed" (solid trust — blue badge)

Requires **ONE** of these:
- Structured database shows size change (OFF/Kroger/USDA)
- News article from a credible outlet with specific sizes
- Photo evidence showing clear before/after labels
- Two or more independent social media posts agreeing on specific before/after sizes

#### Level 3: "Reported" (signal-level trust — amber badge)

Requires:
- At least one source with specific product name and at least one size
- Human reviewer approved it
- Labeled: "Based on community reports. Awaiting additional verification."

Items can be **upgraded** over time: a "Reported" item gets upgraded to "Confirmed" when a structured source corroborates it, and to "Verified" when multiple sources confirm both old and new sizes.

#### What Does NOT Get Published
- "It looks/feels smaller" without specific sizes
- Comparing different product varieties (regular vs. party size)
- Single anonymous tip with no evidence
- Memes, jokes, or general complaints about prices

#### Credible News Source Tiers

**Tier 1**: AP, Reuters, NYT, WSJ, Washington Post, Consumer Reports, BBC, NPR, Bloomberg

**Tier 2**: Local TV/newspaper, Business Insider, Fortune, Forbes, Vox, food industry pubs (Food Dive, Grocery Dive)

**Tier 3 (treated as community reports)**: Blog posts, personal Substacks, YouTube videos, influencer content

#### Shrinkflation Validation Rules (from r/shrinkflation moderators)

Based on the community's own flowchart for valid posts:

1. **Both old and new product must exist** — evidence of BOTH versions required
2. **Same variety and size class** — must be the exact same SKU, not different sizes
3. **Printed weights/volumes differ** — labels must show different numbers
4. **Photo proof of both** — for "Verified" level, photographic or database evidence of both sizes

These rules are encoded into the extraction pipeline and review workflow.

### Data Quality Risks by Source

| Source | Risk | Mitigation |
|--------|------|-----------|
| **Open Food Facts** | Community-edited; typos or vandalism could look like shrinkflation | Never trust single observation. Cross-reference with other sources. Track edit recency. |
| **Kroger API** | Size field is text; parsing errors possible. Temporary inventory glitches. | Strict unit parsing. Ignore >50% changes (likely parsing error). Require 2 consecutive polls. |
| **USDA** | Updated quarterly; changes appear months late | Use as corroborating source, not primary detection. |
| **Reddit** | Anecdotal. Memory errors. Regional variations confused with shrinkflation. | Never auto-publish. Always goes to review queue. |
| **News** | Articles may lack specific sizes or cite each other (circular sourcing) | Require specific numbers in the article. Track original source, not syndications. |

---

## 6. Security Model

### What Changes from the Old System

| Old System | New System |
|------------|-----------|
| Admin password stored as hash in `app_settings` table | Supabase Auth with Google OAuth |
| Browser uses `service_role` key (full access) | Browser only uses `anon` key (public reads) |
| Admin actions happen directly in browser JS | Admin actions go through API routes (server-side) |
| No session management | Proper JWT-based sessions via Supabase Auth |
| Single admin account | Role-based: admin, reviewer, public |
| No audit log of admin sessions | Full audit trail of every action |
| Admin at hidden URL (long-press logo) | Admin at `/admin` (public URL, behind Google OAuth) |

### Role Model

```
┌─────────────────────────────────────────────────┐
│                    ROLES                         │
│                                                 │
│  anon (public):                                 │
│    ✓ Read published_changes, product_entities,  │
│      pack_variants, variant_observations        │
│    ✓ Read dashboard_stats, leaderboard views    │
│    ✓ Submit tips (rate-limited)                 │
│    ✓ Submit upvotes (one per session)           │
│    ✗ Cannot read raw_items, claims,             │
│      change_candidates, review_actions          │
│    ✗ Cannot write to any core table             │
│                                                 │
│  authenticated (logged-in user):                 │
│    ✓ Everything anon can do                     │
│    ✓ Submit tips with higher priority           │
│    ✗ Cannot access review queue                 │
│                                                 │
│  reviewer (you, your wife, future mods):         │
│    ✓ Everything authenticated can do            │
│    ✓ Read review queue (change_candidates)      │
│    ✓ Read claims, raw_items (for evidence)      │
│    ✓ Approve/reject/edit change_candidates      │
│    ✗ Cannot modify published_changes directly   │
│    ✗ Cannot modify scraper_state or settings    │
│                                                 │
│  admin (you only):                               │
│    ✓ Everything reviewer can do                 │
│    ✓ Retract published changes                  │
│    ✓ Manage user roles                          │
│    ✓ Access audit log                           │
│    ✓ Modify system settings                     │
│                                                 │
│  service_role (server-side only, NEVER in browser):│
│    ✓ Full database access                       │
│    ✓ Used by: scrapers, API routes, Edge Funcs  │
│    ✗ NEVER exposed to any client-side code      │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Row-Level Security (RLS) Strategy

RLS means the database itself enforces access rules. Even if someone found a way around the frontend, the database would still block unauthorized actions.

```sql
-- Example: published_changes is readable by everyone,
-- but only service_role can insert/update
ALTER TABLE published_changes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Public can read non-retracted changes"
    ON published_changes FOR SELECT
    USING (NOT is_retracted);

CREATE POLICY "Service role can do anything"
    ON published_changes FOR ALL
    USING (auth.role() = 'service_role');

-- Example: change_candidates readable only by reviewers+
ALTER TABLE change_candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Reviewers can read candidates"
    ON change_candidates FOR SELECT
    USING (
        auth.role() = 'service_role'
        OR (
            auth.role() = 'authenticated'
            AND auth.jwt() ->> 'user_role' IN ('reviewer', 'admin')
        )
    );
```

### API Boundaries

**All privileged writes go through Next.js API routes, never directly from the browser.**

The browser sends requests like:
```
POST /api/admin/review
Authorization: Bearer <supabase_jwt_token>
Body: { candidate_id: "...", action: "approve", notes: "Looks correct" }
```

The API route:
1. Verifies the JWT token with Supabase
2. Checks the user has the `reviewer` or `admin` role
3. Uses `service_role` to update the database
4. Logs the action in `review_actions`
5. Returns success/failure

**The browser never sees the `service_role` key.** It only has the `anon` key, which can only read public data.

### How to Set Up Roles

Supabase Auth doesn't have built-in roles beyond `anon` and `authenticated`. We add custom roles using JWT claims:

```sql
-- Custom claims stored in auth.users metadata
-- When you invite your wife as a reviewer:
UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"user_role": "reviewer"}'
WHERE email = 'wife@example.com';

-- This role appears in the JWT, so RLS policies can check it
```

For community moderators later, you'd create a simple admin panel to assign roles.

---

## 7. Website vs App Decision

### Recommendation: Website-first with PWA

**PWA** stands for Progressive Web App. It means your website can be "installed" on a phone like an app, but it's still just a website under the hood. The user taps "Add to Home Screen" and gets an app icon.

### Why Website First

| Factor | Website | Native App |
|--------|---------|-----------|
| Cost to build | 1 codebase | 2 codebases (iOS + Android) or React Native |
| Time to build | Weeks | Months |
| Distribution | Instant — just share a URL | App Store review process (1-2 weeks) |
| Updates | Deploy and everyone gets it | App Store approval for each update |
| SEO | Google indexes everything | App content is invisible to Google |
| Sharing | Share a product page link on Twitter/Reddit | Have to deep-link, often broken |
| Your audience | Consumers + journalists = link-driven | — |
| Cost to maintain | Near zero (Vercel free tier) | $99/year Apple + $25 Google |

For a platform where **journalists linking to product pages** is a key growth channel, SEO and shareable URLs are essential. Native apps are invisible to Google.

### PWA Features You Get for Free

A PWA gives you most of what a native app would:

- **Home screen icon** — looks like an app
- **Offline support** — cached pages work without internet
- **Push notifications** (if you ever need them)
- **Full-screen mode** — no browser chrome
- **QR code scanner** — works in browsers via camera API (you already have this)

### When to Build a Native App (Explicit Triggers)

Build a native app **only if** one or more of these happen:

| Trigger | Why Native Helps | Threshold |
|---------|-----------------|-----------|
| Receipt scanning becomes core | Native camera + ML Kit is smoother than browser | >1,000 monthly receipt scans |
| You need push notifications at scale | PWA push is unreliable on iOS | >10,000 active users wanting alerts |
| Offline-first barcode scanning in stores | Native is needed for real-time in-store use | Users request "scan while shopping" |
| App Store presence becomes a growth channel | Discovery via App Store search | Brand recognition is established |
| Investor/partner requires it | "Do you have an app?" | Active fundraising/partnerships |

**Until at least 2 of these triggers fire, building a native app is a waste of time and money.**

### What to Build Instead

The PWA version of FullCarts should feel great on mobile:
- **Mobile-first design** (you already do this at 430px max-width)
- **Bottom navigation** (you already have this)
- **QR scanner** (you already have this)
- **"Add to Home Screen" prompt** — shown after 2+ visits
- **Offline caching** — product pages work without internet
- **Share buttons** — easy sharing to Twitter, Reddit, iMessage

---

## 8. Monetization Readiness

### Principle: Build for Defensibility Now, Monetize Later

The goal isn't to make money today. It's to build a data asset that's **worth paying for** when the time comes. This means:

1. **Data quality > data quantity.** 100 verified, evidence-backed shrinkflation events are more valuable than 10,000 unverified claims.
2. **Provenance is the moat.** Anyone can scrape Reddit. Only FullCarts has timestamped observations from multiple structured sources with human verification.
3. **Trust is the brand.** If consumers, journalists, and eventually brands trust FullCarts data, that trust is the monetization engine.

### Future Revenue Streams (Design for Now, Build Later)

#### 1. Data API (Premium Access)

**What it is**: A paid API that gives businesses access to FullCarts data — product histories, change events, brand scorecards, category trends.

**Who would pay**: CPG analytics firms, consumer advocacy groups, media companies, academic researchers, competitor intelligence tools.

**What to build now**:
- Clean, consistent API contracts (the `/api/products`, `/api/changes` endpoints we're already building)
- Rate limiting infrastructure (track usage per API key)
- Data export in standard formats (JSON, CSV)
- A `data_licenses` table to track API keys and access levels

**What to build later**: Paid tier with higher rate limits, historical data access, bulk export, webhook notifications for new changes.

**Pricing model** (when ready): Freemium
- Free: 100 API calls/day, last 30 days of data
- Pro ($49/mo): 10,000 calls/day, full history, CSV export
- Enterprise ($299/mo): Unlimited, webhook, custom integrations

#### 2. Brand Intelligence Reports

**What it is**: Reports that show brands how their packaging changes are being perceived by consumers. "Your Cheerios downsizing was detected on Reddit 3 days after launch, covered by 4 news outlets, and received 1,200 negative social mentions."

**Who would pay**: CPG companies who want early warning on PR risk from packaging changes.

**What to build now**:
- `brand_signal_counts` view (you already have this concept)
- Evidence provenance tracking (so reports cite sources)
- Sentiment data from GDELT news monitoring

**What to build later**: Automated brand report generation, email alerts, dashboard for brand managers.

**Integrity guardrail**: Brand reports show facts, not opinions. A brand paying for intelligence doesn't influence how their products are rated or displayed. This firewall must be explicit and public.

#### 3. Media Licensing

**What it is**: News organizations pay to use FullCarts data in articles, graphics, and TV segments.

**Who would pay**: Consumer affairs journalists, TV news producers, inflation explainer writers.

**What to build now**:
- Shareable product pages with embeddable timelines
- "Cite this data" feature with proper attribution format
- High-quality data visualizations (before/after charts)

**What to build later**: Press page, media kit, licensing agreement, premium embeds.

#### 4. Restoration Recognition (Positive Incentive)

**What it is**: Brands that reverse shrinkflation get positive recognition. "Brand X restored Cheerios to 15oz in March 2026."

**Why it matters**: This makes FullCarts useful to brands (not just threatening), creates a positive feedback loop, and is more sustainable than pure naming-and-shaming.

**What to build now**:
- The `change_type = 'restoration'` field (already in the schema)
- A "Good News" section on the website
- Press-friendly "restoration announcements"

### Sponsor-Safe Integrity Guardrails

These rules ensure FullCarts data can be trusted regardless of who's paying:

1. **No sponsor influence on data.** Paying for API access or brand reports does not affect how products are rated, ranked, or displayed. Ever.

2. **Methodology is public.** The "About" page explains exactly how data is collected, scored, and verified. Readers can audit the process.

3. **Evidence is transparent.** Every published change links to its evidence sources. Nothing is asserted without proof.

4. **Retractions are visible.** If a change is retracted, the retraction and reason are shown publicly. We don't hide mistakes.

5. **No advertising on product pages.** Product pages are editorial, not commercial. Ads (if ever added) go on non-editorial pages only.

6. **Firewall between editorial and business.** Data collection, verification, and publication are independent of revenue relationships.

### What to Track Now for Monetization Later

```sql
-- API usage tracking (build this from day 1)
CREATE TABLE api_usage (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    api_key_id      UUID,  -- NULL for public/anonymous access
    endpoint        TEXT NOT NULL,
    method          TEXT NOT NULL,
    status_code     INTEGER NOT NULL,
    response_time_ms INTEGER,
    created_at      TIMESTAMPTZ DEFAULT now() NOT NULL
);

-- Track what data is most accessed
-- This tells you what people would pay for
CREATE INDEX idx_api_usage_endpoint ON api_usage (endpoint, created_at);
```

---

## 9. 90-Day Implementation Roadmap

### Phase 0: Foundation (Days 1-7)

**Goal**: New project scaffolding. Nothing visible to users yet.

**Deliverables**:
- [ ] Create new Supabase project (or reset existing one)
- [ ] Create all tables from Section 3 (data model)
- [ ] Set up RLS policies from Section 6 (security)
- [ ] Set up Supabase Auth with your admin account
- [ ] Scaffold Next.js project with Supabase integration
- [ ] Deploy to Vercel (even if just a "Coming Soon" page)
- [ ] Set up GitHub repo structure (or clean existing one)

**Acceptance criteria**: Database schema is live. Next.js app deploys to Vercel. You can log in via Supabase Auth.

**Non-technical explanation**: We're building the foundation — like pouring concrete before building a house. Nothing looks different yet, but everything that follows depends on this being right.

### Phase 1: Ingestion Pipeline (Days 8-21)

**Goal**: Raw data flowing into the new database from all sources.

**Deliverables**:
- [ ] Refactor Reddit scraper to write to `raw_items` (no extraction)
- [ ] Refactor news scraper to write to `raw_items`
- [ ] Build OFF daily snapshotter (write to `raw_items` + `variant_observations`)
- [ ] Register for Kroger API; build weekly poller
- [ ] Register for USDA API; build quarterly snapshot job
- [ ] Build `scraper_state` cursor management
- [ ] Set up GitHub Actions workflows for all scrapers
- [ ] Build GDELT news monitor (free, simple HTTP)

**Acceptance criteria**: All 5 data sources are writing to `raw_items` on schedule. `scraper_state` tracks cursors. No duplicate records. You can see raw_items growing in the Supabase dashboard.

**Non-technical explanation**: We're building the "ears" of the system — the parts that listen to Reddit, food databases, grocery stores, and news. They just collect raw information and store it. No interpretation yet.

### Phase 2: Extraction & Resolution (Days 22-35)

**Goal**: AI extracts structured claims from raw items and matches them to products.

**Deliverables**:
- [ ] Build extraction pipeline (NLP + Claude Haiku for Reddit/news)
- [ ] Build OFF/Kroger/USDA direct observation pipeline (structured data, no AI needed)
- [ ] Build entity resolution: match claims to product_entities by UPC or fuzzy name
- [ ] Build change detection: compare observations over time, create change_candidates
- [ ] Build confidence scoring (per-field)
- [ ] Set up GitHub Actions for extraction/detection jobs

**Acceptance criteria**: Raw items are being processed into claims. Claims are matching to product entities. Change candidates are being generated. You can see the review queue filling up in the database.

**Non-technical explanation**: We're building the "brain" — the parts that read the raw information and figure out "this Reddit post is talking about Doritos Nacho Cheese going from 9.5oz to 9.25oz." It also figures out that three different reports are all talking about the same product.

### Phase 3: Admin Dashboard & Review Workflow (Days 36-50)

**Goal**: You can review, approve, and publish changes through a secure admin interface.

**Deliverables**:
- [ ] Build admin login flow (Supabase Auth)
- [ ] Build review queue page (list change_candidates, sorted by evidence/priority)
- [ ] Build review detail page (show all evidence, confidence, source links)
- [ ] Build approve/reject/edit actions (via API routes)
- [ ] Build retraction flow (for corrections)
- [ ] Build audit log view
- [ ] Add your wife as a reviewer (Supabase Auth + role)

**Acceptance criteria**: You can log in, see the review queue, review items, and approved items appear in `published_changes`. All actions are logged in `review_actions`.

**Non-technical explanation**: We're building your "control room" — the place where you review what the system found and decide what goes public. Every decision you make is logged, so there's always a record of who approved what.

### Phase 4: Public Website (Days 51-70)

**Goal**: The public-facing website is live with real data.

**Deliverables**:
- [ ] Build homepage (stats, recent changes, trending products)
- [ ] Build product detail pages (/products/:slug) with timeline charts
- [ ] Build brand pages (/brands/:slug) — **primary UI focus** with brand scorecard
- [ ] Build leaderboard (worst offenders — brand-centric ranking)
- [ ] Build "Good News" section (restorations — brands that reversed shrinkflation)
- [ ] Build search (full-text product and brand search)
- [ ] Build QR scanner (barcode → product page)
- [ ] Build tip submission form (light crowdsourcing, no account required)
- [ ] Build "About" page with methodology and evidence standard
- [ ] Evidence badges on all published changes (Verified/Confirmed/Reported)
- [ ] SEO optimization (meta tags, Open Graph, structured data)
- [ ] Responsive design (mobile-first, following FULLCARTS_DESIGN_EXPORT.md)
- [ ] DNS cutover: fullcarts.org → new Vercel deployment

**Testing approach**: During Phases 0-3, the new site is accessible at a Vercel preview URL (e.g., `fullcarts-rebuild.vercel.app`). The current fullcarts.org stays live until Phase 4 is ready. When satisfied with the new site, switch DNS to point to Vercel.

**Acceptance criteria**: fullcarts.org shows real, verified shrinkflation data. Brand pages show all events per brand. Products have timeline charts. Evidence badges visible on every change. Leaderboard works. Search works. Good News section shows restorations. Pages are indexed by Google.

**Non-technical explanation**: This is when the "showroom" opens. Real users can visit fullcarts.org, search for products and brands, see shrinkflation timelines, and submit tips. Each change shows how trustworthy the evidence is. Brands that do the right thing get credit in the Good News section.

### Phase 5: Polish & Launch Prep (Days 71-90)

**Goal**: Production-ready quality, monitoring, and soft launch.

**Deliverables**:
- [ ] Error monitoring (Sentry free tier or similar)
- [ ] Uptime monitoring (UptimeRobot free tier)
- [ ] Performance optimization (lighthouse score > 90)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] PWA manifest + service worker (installable on mobile)
- [ ] Rate limiting on public API endpoints
- [ ] API usage tracking (`api_usage` table)
- [ ] Data quality dashboard (how many raw_items → claims → published)
- [ ] Write documentation: data methodology, API docs
- [ ] Soft launch: share with r/shrinkflation community for feedback

**Acceptance criteria**: Site is fast, accessible, and monitored. You know immediately if something breaks. API usage is tracked. Community feedback is being collected.

**Non-technical explanation**: We're doing the final quality checks — making sure the site is fast, works for people with disabilities, and won't break without you knowing about it. Then we do a soft launch with the Reddit shrinkflation community to get real feedback before a wider announcement.

### Post-90-Day Priorities

After the 90-day rebuild, these are the next things to consider (in rough priority order):

1. **Community moderation features** — invite moderators, reputation system
2. **Receipt scanning** — let users upload grocery receipts for structured data
3. **Newsletter** — weekly "shrinkflation report" email
4. **Social media presence** — automated posting of new findings
5. **API documentation** — for future data licensing
6. **Brand response system** — let brands respond to findings
7. **Internationalization** — expand beyond US products

---

## 10. Risks & Tradeoffs

### Risk Matrix

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| **Solo builder burnout** | High | Critical | Phase strictly. Each phase delivers value independently. Take breaks. |
| **Kroger API access denied** | Medium | Medium | Walmart Affiliate API as backup. OFF + USDA still provide snapshots. |
| **LLM extraction costs spike** | Low | Medium | Use Claude Haiku ($0.25/M tokens). Cap monthly spend. Batch processing. |
| **Open Food Facts data quality issues** | Medium | Low | Cross-reference with USDA. Flag discrepancies for manual review. |
| **Supabase free tier limits hit** | Medium | Medium | $25/mo Pro tier is budgeted. Generous limits for this scale. |
| **Legal challenge from a brand** | Low | High | Evidence chain is defensible. Fair use of factual data. Consult lawyer if it happens. |
| **Reddit API changes** | Medium | Medium | Arctic Shift as backup. Diversified sources reduce Reddit dependency. |
| **Scope creep** | High | High | Stick to the 90-day plan. Say "post-90-day" to new ideas. |
| **Data migration regret** | Low | Low | Old Supabase project is preserved. Can always pull specific records if needed. |

### Key Tradeoffs

#### 1. Starting Fresh vs. Migrating Data
**Chose**: Start fresh
**Tradeoff**: We lose 17,000 raw Reddit posts and ~300 reviewed records.
**Why it's worth it**: The old data has fake UPCs (REDDIT-xxx), mixed quality, and doesn't fit the new schema cleanly. Migrating would add 2+ weeks of work and import data quality problems. The Reddit posts still exist on Reddit — we can re-scrape the good ones.
**Fallback**: The old Supabase project stays live. If you find a specific record you need, you can manually copy it.

#### 2. Next.js vs. Single HTML File
**Chose**: Next.js
**Tradeoff**: Requires a build step, Node.js knowledge, and Vercel hosting (vs. GitHub Pages).
**Why it's worth it**: SEO (server-side rendering), security (API routes), and maintainability (components vs. 5,800-line file). Vercel free tier covers hosting.
**Fallback**: If Next.js feels too complex, Astro is a simpler alternative that still deploys to GitHub Pages.

#### 3. Multiple Data Sources vs. Reddit Only
**Chose**: Multiple sources (OFF, Kroger, USDA, Reddit, News)
**Tradeoff**: More scrapers to build and maintain. More API registrations.
**Why it's worth it**: Reddit-only data is anecdotal. Structured databases (OFF, Kroger) provide the hard evidence that makes the data defensible and automatable. This is what turns FullCarts from "a Reddit aggregator" into "an intelligence platform."
**Fallback**: Build Reddit + OFF first (Phase 1). Add Kroger and USDA only if Phase 1 goes well.

#### 4. Separate raw_items → claims → entities (3-step) vs. Direct ingestion (1-step)
**Chose**: 3-step pipeline
**Tradeoff**: More complex. More tables. Harder to debug initially.
**Why it's worth it**: Reproducibility (re-extract with better AI without re-scraping), auditability (trace any published fact back to its source), and quality (per-field confidence, evidence requirements).
**Fallback**: Start with 2 steps (raw_items → product + observation) and add the claims layer later if the simpler approach works well enough.

#### 5. Supabase Auth vs. Simple Password
**Chose**: Supabase Auth
**Tradeoff**: More setup work. Users need real accounts.
**Why it's worth it**: Real security. Role-based access. Audit trails. Scales to community moderation.
**Fallback**: None needed. Supabase Auth is straightforward to set up and the right choice.

### Solo Builder Survival Guide

Building this alone is ambitious. Here's how to avoid burnout:

1. **Each phase stands alone.** If you stop after Phase 1, you have a data collection system. After Phase 2, you have extraction. After Phase 3, you have review. Each phase delivers value even if you never build the next one.

2. **Automate relentlessly.** Every minute spent on automation saves hours of manual work. Scrapers run themselves. Change detection runs itself. You only intervene for review.

3. **Don't build what you don't need yet.** Community moderation? Post-90-day. Receipt scanning? Post-90-day. Native app? Probably never. Stay focused.

4. **Use Claude Code to build everything.** Every component in this plan can be built by Claude Code with clear prompts. You're the architect; Claude Code is the builder.

5. **Ship ugly, improve later.** The admin dashboard doesn't need to be pretty. The public site should be clean but doesn't need to be perfect. Get data flowing first.

---

## Appendix A: Data Source Details

### Tier 1: Primary Sources (Free, Integrate in Phase 1)

| Source | API | Rate Limit | Data Available | Cost |
|--------|-----|-----------|---------------|------|
| **Open Food Facts** | `world.openfoodfacts.org/api/v2/` | 100 req/min | Product name, brand, quantity, nutrition, images, barcode | Free (ODbL license) |
| **USDA FoodData Central** | `api.nal.usda.gov/fdc/v1/` | 3,600 req/hr | Product name, brand, UPC, serving size, package weight, nutrition, ingredients | Free (public domain) |
| **Kroger API** | `developer.kroger.com` | 10,000 req/day | Product name, UPC, brand, size, price, images, store availability | Free (OAuth2 registration) |
| **Reddit (Arctic Shift)** | `arctic-shift.photon-reddit.com` | 2,000 req/min | Full post data: title, body, score, subreddit, images | Free |
| **GDELT** | `api.gdeltproject.org` | Generous | News articles, sentiment, source countries | Free |
| **Google News RSS** | RSS feeds | No limit | Article titles, URLs, dates | Free |
| **BLS CPI API** | `api.bls.gov` | 500 req/day (with key) | Food price indices, quantity adjustments | Free |

### Tier 2: Future Additions (Low Cost, Post-90-Day)

| Source | What It Adds | Cost | When to Add |
|--------|-------------|------|-------------|
| **Walmart Affiliate API** | Pricing/sizing from largest US retailer | Free (affiliate approval) | When you want a second retailer |
| **YouTube Data API** | Video mining for product mentions | Free (10K units/day) | When you want social media signals |
| **Bluesky API** | Social media monitoring | Free | When platform grows |
| **UPCitemdb** | Barcode lookup for unknown products | Free (100/day) | When you need UPC resolution |
| **Receipt OCR (Veryfi)** | Crowdsourced purchase data | Free (50/mo) | When you add receipt scanning |

### Tier 3: Enterprise (When Funded)

| Source | What It Adds | Cost | When to Add |
|--------|-------------|------|-------------|
| **NielsenIQ** | Gold-standard retail scanner data | $50K+/year | Grant funding or data partnership |
| **Circana** | Alternative retail scanner data | $50K+/year | Same |
| **Datasembly** | Real-time grocery price monitoring | Custom | Same |

### Monthly Snapshot Strategy

This is the "recurring monthly snapshots" approach you asked about. Here's how it works:

```
WEEK 1 of each month:
├─ Download OFF daily CSV export (full database, ~2GB)
├─ Diff quantity fields against last month's snapshot
├─ Flag products where quantity decreased → raw_items
└─ Update variant_observations for all tracked UPCs

WEEKLY (every Sunday):
├─ Query Kroger API for all tracked UPCs at 2 reference stores
├─ Record size + price → variant_observations
└─ Flag any size changes → raw_items → change detection

QUARTERLY:
├─ Download USDA Branded Foods bulk data
├─ Cross-reference UPCs with pack_variants
├─ Compare packageWeight against our records
└─ Flag discrepancies for review

DAILY:
├─ Reddit scraper → raw_items (for community signals)
├─ News scraper → raw_items (for media coverage)
├─ OFF API spot-check for top 100 tracked products
└─ Process extraction queue (raw_items → claims)
```

**The key insight**: By taking regular snapshots from authoritative sources, we don't need Reddit to tell us about shrinkflation. We can detect it ourselves from the data. Reddit becomes a *signal* that something might have changed, but the *proof* comes from structured databases.

---

## Appendix B: Concrete Schemas

### Complete SQL Migration (Ready to Run)

The table definitions in Section 3 are the complete schema. To run them:

1. Create a new Supabase project (or use SQL editor on existing)
2. Run the CREATE TABLE statements in order:
   - `evidence_files` (no dependencies)
   - `raw_items` (no dependencies)
   - `product_entities` (no dependencies)
   - `pack_variants` (depends on product_entities)
   - `variant_observations` (depends on pack_variants, evidence_files, raw_items)
   - `claims` (depends on raw_items, product_entities, pack_variants)
   - `change_candidates` (depends on pack_variants, variant_observations)
   - `published_changes` (depends on change_candidates, pack_variants, product_entities)
   - `review_actions` (depends on auth.users)
   - `tips` (depends on evidence_files)
   - `upvotes` (depends on published_changes)
   - `scraper_state` (no dependencies)
   - `api_usage` (no dependencies)
3. Create views (product_timeline, shrinkflation_leaderboard, dashboard_stats)
4. Create RLS policies

### Index Strategy

The indexes defined in the schema cover the primary access patterns:

| Query Pattern | Index |
|--------------|-------|
| "Show me product X" | `idx_entities_name_search` (GIN full-text) |
| "All variants for entity Y" | `idx_variants_entity` |
| "Observations for variant Z" | `idx_observations_variant` + `idx_observations_date` |
| "Pending review items" | `idx_candidates_status` |
| "Brand leaderboard" | `idx_published_brand` |
| "Recent changes" | `idx_published_date` |
| "Find raw item by source" | `idx_raw_items_source_type` + UNIQUE(source_type, source_id) |
| "Find claims for a raw item" | `idx_claims_raw_item` |
| "Look up by UPC" | `idx_variants_upc` + `idx_claims_upc` |

---

## Appendix C: API Endpoint Contracts

### Public Endpoints (No Auth Required)

#### GET /api/products
Search and browse products.

```
Query params:
  q         - Search query (full-text)
  brand     - Filter by brand name
  category  - Filter by category
  page      - Page number (default: 1)
  limit     - Results per page (default: 20, max: 100)

Response: {
  data: [{
    id: "uuid",
    canonical_name: "Doritos Nacho Cheese Tortilla Chips",
    brand: "Doritos",
    category: "Snacks",
    variants: [{
      id: "uuid",
      variant_name: "Doritos Nacho Cheese 9.25oz Bag",
      upc: "028400090858",
      current_size: 9.25,
      size_unit: "oz"
    }],
    change_count: 2,
    latest_change: {
      size_before: 9.5,
      size_after: 9.25,
      size_delta_pct: -2.63,
      observed_date: "2026-02-15"
    }
  }],
  pagination: { page: 1, limit: 20, total: 342 }
}
```

#### GET /api/products/:id
Product detail with full timeline.

```
Response: {
  entity: { id, canonical_name, brand, category, image_url },
  variants: [{
    id, variant_name, upc, current_size, size_unit,
    observations: [
      { date: "2024-01", size: 10, price: 4.29, source: "kroger_api" },
      { date: "2024-06", size: 9.5, price: 4.29, source: "openfoodfacts" },
      { date: "2025-01", size: 9.25, price: 4.49, source: "kroger_api" }
    ]
  }],
  changes: [{
    id, size_before, size_after, size_delta_pct, change_type,
    severity, observed_date, evidence_summary, upvote_count
  }]
}
```

#### GET /api/changes
Recent verified changes (the "feed").

```
Query params:
  change_type  - Filter: shrinkflation, upsizing, restoration
  severity     - Filter: minor, moderate, major
  since        - ISO date, changes after this date
  page, limit

Response: {
  data: [{
    id, brand, product_name, size_before, size_after, size_unit,
    size_delta_pct, change_type, severity, observed_date,
    evidence_count, upvote_count
  }],
  pagination: { ... }
}
```

#### GET /api/leaderboard
Worst offenders ranked by cumulative shrinkage.

```
Query params:
  category  - Filter by category
  limit     - Top N (default: 50)

Response: {
  data: [{
    entity_id, canonical_name, brand,
    shrinkflation_count, total_shrinkage_pct,
    first_detected, last_detected
  }]
}
```

#### GET /api/stats
Dashboard numbers.

```
Response: {
  total_products: 1234,
  total_changes: 567,
  shrinkflation_events: 432,
  pending_review: 23,
  items_ingested_7d: 89,
  sources: { reddit: 45, openfoodfacts: 30, kroger: 10, news: 4 }
}
```

#### POST /api/tips
Submit a community tip.

```
Body: {
  brand: "General Mills",
  product_name: "Cheerios",
  description: "Box looks smaller than last month",
  evidence_url: "https://..."  // optional
}

Response: { id: "uuid", status: "pending" }

Rate limit: 5 per hour per IP
```

### Admin Endpoints (Auth Required, reviewer+ Role)

#### GET /api/admin/queue
Review queue.

```
Headers: Authorization: Bearer <jwt>

Query params:
  status    - Filter: pending, approved, rejected (default: pending)
  sort      - evidence_count, severity, created_at
  page, limit

Response: {
  data: [{
    id, variant_id, brand, product_name,
    size_before, size_after, size_delta_pct,
    change_type, severity, evidence_count,
    supporting_claims: [{ raw_source_type, confidence, extracted_brand, ... }],
    created_at
  }],
  pagination: { ... }
}
```

#### POST /api/admin/review
Review a change candidate.

```
Headers: Authorization: Bearer <jwt>

Body: {
  candidate_id: "uuid",
  action: "approve" | "reject" | "edit",
  edits: {               // only if action = "edit"
    size_before: 15,
    size_after: 13.5,
    // ... any field corrections
  },
  notes: "Verified against OFF database"
}

Response: { success: true, published_change_id: "uuid" }
```

#### POST /api/admin/retract
Retract a published change.

```
Headers: Authorization: Bearer <jwt>
Required role: admin

Body: {
  published_change_id: "uuid",
  reason: "Brand provided evidence this was a regional test, not a permanent change"
}

Response: { success: true }
```

---

*This document is a living plan. It will be updated as decisions are made and as we learn from implementation.*
