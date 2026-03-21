# FullCarts Pipeline Fix Plan

**Audit date:** 2026-03-20
**Audited by:** Claude Code (claude-sonnet-4-6)

---

## Executive Summary

The FullCarts data pipeline has **one critical architectural gap** (approved claims never flow anywhere), **one bootstrapping problem** (two scrapers wait for data that doesn't exist yet), **one data quality bug** (BLS CPI values silently dropped), and **stale legacy data** to clean up. Everything is fixable. Prioritizing Fix 2 first unblocks the entire chain and enables your highest-value launch content.

---

## Data Flow Audit: What Actually Happens

### Scraper Data Flows (verified by reading source code)

| Scraper | Reads From | Writes To | Source Type | Rows Written |
|---------|-----------|-----------|-------------|--------------|
| `reddit_recent` | Arctic Shift / Reddit JSON API | `raw_items` | `reddit` | ~1–2/day |
| `reddit_backfill` | Arctic Shift API | `raw_items` | `reddit` | 16,503 loaded |
| `news_rss` | Google News RSS | `raw_items` | `news` | ~20–50/day |
| `gdelt` | GDELT document API | `raw_items` | `gdelt` | ~250/run |
| `off_discovery` | OFF search API | `raw_items` | `openfoodfacts` | 45,134 loaded |
| `kroger_discovery` | Kroger OAuth API | `raw_items` | `kroger_api` | 3,751 loaded |
| `off_daily` | `pack_variants.is_active=true` → OFF API | `raw_items` + `variant_observations` | `openfoodfacts` | **0 rows (see Fix 3)** |
| `kroger_weekly` | `pack_variants.is_active=true` → Kroger API | `raw_items` + `variant_observations` | `kroger_api` | **0 rows (see Fix 3)** |
| `usda_quarterly` | USDA FDC | `raw_items` + `variant_observations` | `usda` | 5.35M loaded |
| `bls_shrinkflation` | BLS .xlsx files | `bls_shrinkflation` (custom table, NOT raw_items) | n/a | counts loaded, CPI = NULL |
| `fred_cpi` | FRED CSV/JSON | `fred_cpi_data` (custom table, NOT raw_items) | n/a | ✓ |
| `open_prices` | Open Prices API | `raw_items` + `open_prices_data` | `open_prices` | ✓ |

### Claims Pipeline Flow (verified)

```
raw_items (reddit, news, gdelt)
  ↓ extract_claims.py — Claude Haiku extraction
claims table
  - 3,264 approved
  - 6,278 pending
  - ~14,156 discarded

Admin UI (web/src/app/admin/claims/actions.ts)
  updateClaimStatus(claimId, 'approved')
    → UPDATE claims SET status = 'approved' WHERE id = ?
    → NOTHING ELSE. No product creation. No downstream effect.
```

### What published_changes requires (full dependency chain)

```
product_entities (canonical product record)
  → pack_variants (specific UPC/SKU for that product)
    → variant_observations (size/price snapshots over time)
      → change_candidates (computed from observation pairs)
        → published_changes (the public record)
```

**None of this chain is populated from approved claims.** The bridge script does not exist.

### Legacy Pipeline A (promote_staging.py)

```
reddit_staging table (old schema, separate from raw_items/claims)
  ↓ backend/jobs/promote_staging.py
    → products (fake UPCs: REDDIT-{id[:8]})
    → product_versions (before/after pairs)
    → events (legacy change log)
```

This system is **completely disconnected** from the new pipeline. It still writes to the old schema tables. The 159 products it created have synthetic UPCs and are stale from before the website reset.

---

## Issues Identified

### Issue 1: Pipeline A Stale Data (Legacy System)

**What happened:** Before the rebuild, `promote_staging.py` ran against `reddit_staging` and created 159 products with fake UPCs (`REDDIT-XXXXXXXX` format) in the old `products` table. These have no real UPCs, no images, no verified sizes — they're fabricated records from a discarded system.

**Tables affected:** `products`, `product_versions`, `events`, possibly `news_articles`, `article_product_links`

**Root cause:** The old system and new system coexist in the same database. The old system ran before the reset.

---

### Issue 2 (CRITICAL): Approved Claims → Product Creation Gap

**What happened:** There is no code path from `claims.status = 'approved'` to any product record. The admin UI updates `claims.status` and stops. No script, no trigger, no job.

**Code evidence:**
- `web/src/app/admin/claims/actions.ts` — `updateClaimStatus()` only updates `claims` table
- No script in `pipeline/scripts/` processes approved claims
- `promote_staging.py` reads `reddit_staging`, not `claims`
- `product_entities` table has 0 rows
- `pack_variants` table has 0 rows
- `published_changes` table has 0 rows

**The gap:** A script needs to be written that:
1. Reads `claims WHERE status = 'approved'`
2. For each claim: creates or finds a matching `product_entities` row
3. Creates or finds a matching `pack_variants` row (with real UPC if available)
4. Creates `variant_observations` from the claim's old_size and new_size
5. Detects changes and writes `change_candidates`
6. Promotes approved `change_candidates` to `published_changes`

---

### Issue 3: OFF Daily and Kroger Weekly Write 0 Rows

**What happened:** Both `off_daily` and `kroger_weekly` scrapers call `_load_active_upcs()` which queries `pack_variants WHERE is_active = true`. Since `pack_variants` has 0 rows (blocked by Issue 2), neither scraper has any UPCs to fetch. They run successfully but produce no output.

**Code evidence:**
- `openfoodfacts.py:109` — `_load_active_upcs()` queries `pack_variants`
- `kroger.py:54` — same pattern
- Both log "Loaded 0 active UPCs from pack_variants"

**These scrapers are not broken — they're correctly waiting for data.** They will work automatically once `pack_variants` is populated by Fix 2.

---

### Issue 4: BLS Data — official_cpi and rcpi_sc Always NULL

**What happened:** The BLS scraper downloads two XLSX files:
- `r-cpi-sc-counts.xlsx` — downsizing/upsizing event counts (parsed correctly)
- `r-cpi-sc-data.xlsx` — official CPI and R-CPI-SC index values (parsed incorrectly or not at all)

The merge logic in `fetch()` (lines 136–168 of `bls_shrinkflation.py`) initializes every record with `official_cpi: None, rcpi_sc: None` from the counts data, then updates them from the data file via key matching on `(series_name, period_date)`.

**Root cause:** The `_parse_data_file()` → `_parse_wide_sheet()` path likely produces 0 matching rows because:

1. **Series name mismatch:** The counts file is "tall format" and hardcodes the series as `"All food"` (line 244). The data file uses category names read directly from sheet rows (e.g. `"All food"`, `"Cereals and bakery products"`, etc.). If the data file doesn't have a row called exactly `"All food"`, the merge key never matches the counts records.

2. **Possible alternative:** The data file `_find_header_row()` may fail to find date headers in the actual BLS XLSX layout as of 2025, causing `_parse_wide_sheet()` to return 0 rows silently.

**Net effect:** Counts-only rows get written with `official_cpi = NULL, rcpi_sc = NULL`.

---

### Issue 5: published_changes Has 0 Rows

**Root cause:** Depends entirely on Issue 2. `published_changes` requires:
1. `change_candidates` (0 rows) — requires variant_observations comparisons
2. `variant_observations` (0 rows from approved claims) — requires pack_variants
3. `pack_variants` (0 rows) — requires product_entities
4. `product_entities` (0 rows) — requires the claims→products bridge script

This is not a separate bug — it's a downstream consequence of Issue 2.

---

## Data to Delete: Pipeline A Cleanup

Before fixing the pipeline, delete stale data from the old system. These records are fake, pre-reset, and will confuse the new pipeline.

### Delete targets (in order to respect FK constraints)

```sql
-- Step 1: Remove article-product links for fake UPCs
DELETE FROM article_product_links
WHERE product_upc LIKE 'REDDIT-%';

-- Step 2: Remove legacy events for fake UPCs
DELETE FROM events
WHERE upc LIKE 'REDDIT-%';

-- Step 3: Remove product_versions for fake UPCs
DELETE FROM product_versions
WHERE product_upc LIKE 'REDDIT-%';

-- Step 4: Remove the fake products themselves
DELETE FROM products
WHERE upc LIKE 'REDDIT-%';

-- Step 5: (Optional) Clean reddit_staging entries that were "promoted"
-- Only run this if you want to reset the staging table for potential re-processing
-- UPDATE reddit_staging SET status = 'pending' WHERE status = 'promoted';
```

**Verification query after cleanup:**
```sql
SELECT COUNT(*) FROM products WHERE upc LIKE 'REDDIT-%';
-- Expected: 0
```

**What this does NOT affect:** `raw_items`, `claims`, `reddit_staging` — these are untouched. The new pipeline reads from `claims`, not `products`.

---

## Fix Plan (Priority Order)

---

### Fix 1: Clean Pipeline A Stale Data
**Effort:** 15 minutes
**Blocks:** Nothing (cleanup only)

Run the SQL above in Supabase SQL Editor. Verify 0 rows remain for fake REDDIT- UPCs. This is a prerequisite for a clean state before Fix 2.

**Content pillars unlocked:** None directly — but prevents fake data from polluting future brand rankings.

---

### Fix 2 (HIGHEST PRIORITY): Claims → Product Entities Bridge Script
**Effort:** 1–2 days
**Blocks:** Everything downstream (Fix 3 auto-resolves, Fix 5 resolves)

Write `pipeline/scripts/promote_claims.py`. This is the most important script in the codebase.

#### What it needs to do:

**Step 1: Load approved claims**
```python
claims = supabase.table("claims")
    .select("*")
    .eq("status", "approved")
    .is_("matched_entity_id", None)  # not yet promoted
    .execute()
```

**Step 2: For each claim, create/find product_entities**
```python
# Normalize: (lower(brand), lower(product_name)) → entity
# Check if entity exists first (fuzzy match on brand+name)
# If not found, INSERT new product_entity
entity_id = upsert_product_entity(brand, product_name, category)
```

**Step 3: Create/find pack_variants**
```python
# If claim.upc is not null → use UPC as the key
# If no UPC → generate a stable synthetic key: f"CLAIM-{claim.id[:8]}"
# (Better than REDDIT- but still temporary until a real UPC is known)
variant_id = upsert_pack_variant(entity_id, upc, variant_name, old_size, size_unit)
```

**Step 4: Create variant_observations (two rows: before and after)**
```python
# "before" observation: use observed_date - 365 days as estimate
# "after" observation: use observed_date (or today if not known)
insert_variant_observation(variant_id, before_date, old_size, size_unit, raw_item_id)
insert_variant_observation(variant_id, after_date, new_size, size_unit, raw_item_id)
```

**Step 5: Detect size change → change_candidates**
```python
delta_pct = (old_size - new_size) / old_size * 100
change_type = "shrinkflation" if delta_pct > 0 else "upsizing"
severity = "major" if abs(delta_pct) >= 10 else "moderate" if abs(delta_pct) >= 5 else "minor"
insert_change_candidate(variant_id, obs_before_id, obs_after_id, ...)
```

**Step 6: Auto-approve and publish change**
```python
# For claims approved by admin, also auto-approve the change candidate
# and write to published_changes
insert_published_change(candidate_id, variant_id, entity_id, ...)
```

**Step 7: Update claim with matched IDs**
```python
supabase.table("claims").update({
    "matched_entity_id": entity_id,
    "matched_variant_id": variant_id,
    "status": "matched"
}).eq("id", claim.id).execute()
```

#### Key considerations:
- **Deduplication:** Two claims about the same product (e.g. "Doritos" from two Reddit posts) should resolve to the same `product_entity`. Use brand + normalized product name as the dedup key.
- **UPC handling:** 97% of claims have no UPC. Synthetic keys are OK for now — they get replaced when a real UPC is matched later.
- **old_size = NULL:** Some approved claims have sizes extracted but units differ, or one size is missing. Skip variant_observations creation if either size is NULL; still create the entity and variant.
- **Idempotent:** Script should be re-runnable — always check if entity/variant exists before inserting.

**Content pillars unlocked:**
- **Pillar 1 (Gotcha Product Reveals)** — DIRECTLY ENABLED. Each promoted claim becomes a product with before/after sizes. You get brand name, product name, old size, new size, image (if archived), evidence URL (Reddit post). This is your most shareable content format.
- **Pillar 2 (Worst Offenders Rankings)** — ENABLED. Once products have entities, you can GROUP BY brand and rank by count of changes. After 3,264 claims are promoted, you'll have rankings immediately.
- **Pillar 6 (Restoration Wins)** — PARTIALLY ENABLED. Claims with new_size > old_size become "upsizing" candidates.

---

### Fix 3: OFF Daily + Kroger Weekly Scrapers (Auto-resolves after Fix 2)
**Effort:** 0 (no code changes needed)
**Depends on:** Fix 2

After Fix 2 populates `pack_variants`, the `off_daily` and `kroger_weekly` scrapers will automatically start working on their next scheduled run. They check `pack_variants WHERE is_active = true` and fetch current prices/sizes.

**What this adds:**
- Real UPCs for matched products (Kroger carries ~80% of mainstream brands)
- Current retail prices for every tracked product
- Weekly price snapshots enabling price-per-unit trends

**Content pillars unlocked after Fix 3:**
- **Pillar 4 (Price-Per-Unit Watchdog)** — ENABLED. Weekly Kroger price observations + size data = price per oz trend. This is quantitative evidence of real cost increases beyond the nominal price.

---

### Fix 4: BLS Data — Populate official_cpi and rcpi_sc
**Effort:** 2–4 hours (debugging + fix)
**Independent of other fixes**

#### Investigation steps (run in order until root cause found):

**Step 1: Check what the data file actually contains**
```python
# Add debug logging to _parse_data_file()
import openpyxl
wb = openpyxl.load_workbook("data.xlsx", read_only=True, data_only=True)
for sheet in wb.sheetnames:
    ws = wb[sheet]
    rows = list(ws.iter_rows(values_only=True))
    print(f"Sheet: {sheet}, rows: {len(rows)}")
    print("First 5 rows:", rows[:5])
```

**Step 2: Check series name matching**
```python
# After parsing both files, print the keys:
print("Counts keys:", list(counts_records.keys())[:5])
print("Data keys:", list(data_records.keys())[:5])
# If keys don't overlap, the series names differ between files
```

**Most likely fix:** The data file series names don't match `"All food"` because:
- Counts file: hardcoded as `"All food"` (line 244)
- Data file: may use `"All Food"` (capital F) or `"All Items"` or `"All food items"`

The fix is either:
1. Normalize series names to lowercase before merging: `key = (series.lower().strip(), period)`
2. OR: Don't merge by series name — merge by period only (simpler, since counts file only has "All food" anyway)

**Alternative fix if data file layout changed:**
The BLS may have reformatted their XLSX. Update `_parse_data_file()` to handle the 2025 layout. Consider adding a `--debug-bls` flag to print actual Excel cell values.

**Content pillars unlocked:**
- **Pillar 3 (By the Numbers Macro Trends)** — DIRECTLY ENABLED. BLS counts + R-CPI-SC vs CPI comparison = government-sourced validation that shrinkflation is real and measurable. "According to the BLS, 847 products shrank in Q3 2025." This is the authoritative macro content that makes all other claims credible.

---

### Fix 5: published_changes Population (Auto-resolves after Fix 2)
**Effort:** 0 (no additional code needed)
**Depends on:** Fix 2 (which creates both change_candidates AND published_changes as part of promotion)

Fix 2's `promote_claims.py` script directly creates `published_changes` rows. After Fix 2 runs, this table will have 3,264 rows (one per approved claim with size data).

**Content pillars unlocked:**
- All pillars depend on published_changes being populated. This is the public-facing data layer.

---

## Priority Order Summary

| Priority | Fix | Effort | Unlocks Content Pillars |
|----------|-----|--------|------------------------|
| 1 | Clean Pipeline A stale data | 15 min | Cleanup only |
| 2 | Claims → product_entities bridge | 1–2 days | **Pillars 1, 2, 6** (most important) |
| 3 | BLS CPI values fix | 2–4 hours | **Pillar 3** (macro credibility) |
| 4 | OFF daily + Kroger scrapers | 0 (auto after #2) | **Pillar 4** (price-per-unit) |
| 5 | published_changes | 0 (auto after #2) | All pillars (public data layer) |

---

## Content Pillar Mapping

### Pillar 1: "Gotcha" Product Reveals
**Needs:** product name, brand, old size, new size, image, evidence URL
**Blocked by:** Issue 2 (no products exist)
**Fixed by:** Fix 2 — `promote_claims.py` creates a product entity for each approved claim with before/after sizes and the original Reddit post URL as evidence. 3,264 approved claims = 3,264 potential "gotcha" posts. The ~2,624 claims with archived images are immediately post-ready.

### Pillar 2: "Worst Offenders" Rankings
**Needs:** Multiple size-change events per brand
**Blocked by:** Issue 2 (no product_entities, no brands to rank)
**Fixed by:** Fix 2 — once product_entities exist, `GROUP BY brand ORDER BY COUNT(*) DESC` on published_changes gives instant brand rankings. Top brands from 3,264 approved claims will likely be Lay's, Doritos, Oreos, etc.

### Pillar 3: "By the Numbers" Macro Trends
**Needs:** BLS downsizing counts, FRED CPI trends
**Blocked by:** Issue 4 (BLS CPI values NULL — counts are loaded correctly)
**Fixed by:** Fix 4 — counts data already exists. Fixing the data file parse adds official CPI comparison, making the stats more powerful ("products shrank but CPI said +3%").
**Note:** BLS downsizing COUNTS are already loaded and usable for "847 products shrank last quarter" content. Fix 4 adds the CPI comparison context.

### Pillar 4: Price-Per-Unit Watchdog
**Needs:** Price data + size data for same product over time
**Blocked by:** Issues 2 and 3 (pack_variants empty, Kroger not running)
**Fixed by:** Fix 2 → Fix 4 (Kroger auto-starts). First Kroger run after Fix 2 populates prices. Second run one week later enables trend analysis. Note: claims rarely have price data (old_price/new_price fields), so Kroger API is essential for this pillar.

### Pillar 5: Skimpflation Spotlight
**Needs:** Nutrition/ingredient data comparison over time
**Status:** Data already available in `usda_product_history` (3.1M rows, all 7 USDA releases with ingredients + nutrition). 254 products identified with realistic signals via `nutrition_skimp_results` table.
**Blocked by:** No blocking issue — this data is already queryable
**Action needed:** Create a display pipeline from `nutrition_skimp_results` → `published_changes` (as a new change_type: "skimpflation"). This is a separate Phase 3 task, but the underlying data exists.

### Pillar 6: Restoration Wins
**Needs:** Detected size increases
**Blocked by:** Issue 2
**Fixed by:** Fix 2 — `promote_claims.py` should also promote claims where `new_size > old_size` as `change_type = 'upsizing'` (or `'restoration'`). Community Reddit posts about brands increasing sizes are already in the approved claims queue.

---

## What to Build First (Recommended Sequence)

**Week 1:**
1. Run the Pipeline A cleanup SQL (15 min)
2. Write and run `promote_claims.py` (Fix 2) — this is the sprint
3. Verify: `SELECT COUNT(*) FROM published_changes` should return ~2,000–3,264 rows

**Week 2:**
4. Debug and fix BLS data file parsing (Fix 4)
5. Verify: `SELECT series, period, official_cpi, rcpi_sc FROM bls_shrinkflation LIMIT 5` should show non-NULL values

**Week 3:**
5. OFF daily and Kroger weekly run automatically on next schedule
6. After 2 Kroger runs (2 weeks apart), price-per-unit trends become available

**Phase 3 (separate planning):**
7. Skimpflation Spotlight pipeline from usda_product_history → published_changes

---

## What the Frontend Currently Shows

The public site (`web/src/app/page.tsx`) is a **Coming Soon page only**. It reads no database tables. No public-facing product or change data is currently displayed to users.

The admin UI (`/admin/claims`) reads from the `claims` table and displays the review queue. It does not read from `published_changes`.

**Implication:** Fix 2 produces real data but there is no public UI to display it yet. After Fix 2, a separate effort is needed to build the public product/change display pages that read from `published_changes`, `product_entities`, and `pack_variants`.

---

## Progress Update (2026-03-21)

### Completed:
- ✅ Pipeline A cleanup — stale data removed
- ✅ promote_claims.py — built, tested, ran on all approved claims (3,096 published_changes created)
- ✅ Views rewritten for new schema (shrinkflation_leaderboard, brand_scorecard, recent_changes, category_stats, restorations, dashboard_stats)
- ✅ Discovery scraper cursor bug fixed (next_cursor resets to 0)
- ✅ Multi-source extraction deployed (all 9 source types)
- ✅ Stretchflation evidence wall tag added
- ✅ Vercel connected to GitHub for auto-deploys
- ✅ Admin portal "matched" status tab added
- ✅ Anthropic API credits replenished ($47)
- ✅ Claim Extraction #4 triggered (500 items, running)

### Completed (session 2, 2026-03-21):
- ✅ Direct parser for OFF/Kroger/Open Prices (`pipeline/scripts/parse_catalog_claims.py`) — parses structured catalog data directly into claims without Anthropic API calls
- ✅ BLS CPI parser fix — added Excel serial date handling to `_parse_period()` in `bls_shrinkflation.py`

### Remaining:
- 🔧 Walmart scraper build (no API credentials in repo yet)
- 🔧 Product images (all NULL)
- 🔧 Extraction cost optimization

---

## Notes on What Is Already Working Correctly

- All text-based scrapers (reddit, news, gdelt) correctly write to `raw_items`
- `extract_claims.py` correctly extracts claims from raw_items
- Vision enrichment correctly archives images to Supabase Storage
- The admin claims review UI correctly reads and updates claim status
- FRED CPI data loads correctly into `fred_cpi_data`
- Open Prices data loads correctly into both `raw_items` and `open_prices_data`
- USDA product history (all 7 releases) is fully loaded and queryable
- BLS downsizing/upsizing counts load correctly (CPI index values are the only missing piece)
- Reddit, OFF discovery, and Kroger discovery scrapers are running on schedule
