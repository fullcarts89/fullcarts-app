# FullCarts Reports Engine Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a reusable reports engine (insights SQL views + frozen-issue model + auto-spine/human-Take generation flow + `/report`, `/dashboard`, `/admin/reports` surfaces) and ship the flagship **The Receipt** monthly report, delivered via the "Comment CAUGHT" CTA.

**Architecture:** New SQL views compute differentiated cuts on top of existing `/insights` views. A `report_issues` table stores immutable published issues (frozen `payload` JSONB + human `take_md` + sourced `external_facts`). A monthly GitHub Action assembles a `draft` from the views; an admin editor adds the Take + verifies external facts; publishing revalidates the public ISR pages. The dashboard is a separate live ISR surface.

**Tech Stack:** Next.js App Router (TS) · Supabase (Postgres + PostgREST) · ISR · GitHub Actions cron · Python 3.9 pipeline (pytest).

**Design doc:** `docs/plans/2026-06-17-reports-engine-design.md` (read first).

**Non-negotiable gotchas (from CLAUDE.md):**
- Admin mutations = **route handlers** (`web/src/app/api/admin/*/route.ts`) called via `fetch`, **never Server Actions** (auto-refresh bug).
- Every view/query filters `is_retracted` (entities + `published_changes`).
- Denormalized `published_changes.brand`/`product_name` invariant — sanity query must stay 0.
- **No new `claims.status` values.** Reports never touch claim status.
- Python 3.9: no `X | Y`, no `dict[...]`/`list[...]` annotations — use `typing`.

---

## PHASE 0 — Data-feasibility validation gates (DO FIRST; gates Phase 1 design)

These require live DB access (Supabase MCP authed, or `SUPABASE_URL`+`SUPABASE_KEY` env). **Do not write Phase 1 view code until V1/V2/V3 results are recorded in this plan.** Each gate has a decision rule + fallback.

### Task 0.1: Dump real schemas for the tables in question

**Step 1:** Run (MCP `list_tables` verbose, or SQL):
```sql
SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_name IN
  ('variant_observations','open_prices_data','pack_variants','product_entities',
   'corporate_tree','consumer_reports_findings','google_trends_data','usda_product_history')
ORDER BY table_name, ordinal_position;
```
**Step 2:** Paste the column lists into this plan under each gate below, then adjust the gate queries to the real column names (the queries below assume the columns documented in the design doc; verify before trusting).

### Task 0.2: Gate V1 — FullCarts Index density

**Step 1: Eligible-SKU count (matched-basket viability).**
```sql
SELECT COUNT(*) AS skus_ge_2_months FROM (
  SELECT variant_id
  FROM variant_observations
  WHERE price IS NOT NULL AND size > 0 AND price_per_unit IS NOT NULL
  GROUP BY variant_id
  HAVING COUNT(DISTINCT date_trunc('month', observed_date)) >= 2
) t;
```
**Step 2: Monthly depth (can we sustain a series?).**
```sql
SELECT date_trunc('month', observed_date) AS mo,
       COUNT(*) AS priced_obs, COUNT(DISTINCT variant_id) AS skus
FROM variant_observations
WHERE price IS NOT NULL AND size > 0
GROUP BY 1 ORDER BY 1;
```
**Step 3: Consecutive-month basket overlap (the actual index input).**
```sql
WITH m AS (
  SELECT variant_id, date_trunc('month', observed_date)::date AS mo
  FROM variant_observations
  WHERE price IS NOT NULL AND size > 0
  GROUP BY 1,2
)
SELECT a.mo AS month, COUNT(*) AS skus_in_both_consecutive_months
FROM m a JOIN m b ON a.variant_id = b.variant_id AND b.mo = a.mo - INTERVAL '1 month'
GROUP BY a.mo ORDER BY a.mo;
```
**Step 4: Unit families + retailer/source mix (normalization scope).**
```sql
SELECT lower(size_unit) AS unit, COUNT(*) FROM variant_observations WHERE price IS NOT NULL GROUP BY 1 ORDER BY 2 DESC;
SELECT source_type, retailer, COUNT(*) FROM variant_observations WHERE price IS NOT NULL GROUP BY 1,2 ORDER BY 3 DESC;
```
**Decision rule (record result here):**
- **BUILD the Index** if there are **≥30 SKUs with sustained consecutive-month overlap across ≥6 months** (Step 3 shows ≥30 for most recent 6+ months) → implement `fullcarts_index` as matched-basket Laspeyres in Task 1.2.
- **FALLBACK** otherwise → ship "tracked basket of N products, price-per-unit +X% YoY" (a labeled, honest subset metric), defer the "Index" headline. Mark `fullcarts_index` view as TODO.

### Task 0.3: Gate V2 — corporate_tree population (Illusion of Choice)
```sql
SELECT COUNT(*) AS parents, COALESCE(SUM(distinct_brands),0) AS brands_covered, COALESCE(SUM(events),0) AS events_covered FROM corporate_tree;
SELECT COUNT(*) AS entities_total,
       COUNT(*) FILTER (WHERE manufacturer IS NOT NULL) AS entities_with_mfr
FROM product_entities WHERE NOT is_retracted;
```
**Decision rule:** if `parents ≥ 10` and a few parents each carry ≥3 brands → BUILD `category_concentration`. Else → run `python3 -m pipeline.scripts.wikidata_manufacturer_backfill` first (separate effort), and **defer Illusion of Choice to Phase 4**; for Phase 1 swap the rotating Feature to **Serial Shrinkers** (no external dependency).

### Task 0.4: Gate V3 — external-source join hit-rates
```sql
SELECT 'consumer_reports' s, COUNT(*) rows FROM consumer_reports_findings
UNION ALL SELECT 'google_trends', COUNT(*) FROM google_trends_data
UNION ALL SELECT 'usda_history', COUNT(*) FROM usda_product_history;
```
Plus a join probe for each (adjust join keys to real schema from Task 0.1), e.g. CR→entities by brand:
```sql
SELECT COUNT(DISTINCT pe.id) AS entities_with_cr
FROM product_entities pe
JOIN consumer_reports_findings cr ON lower(cr.brand) = lower(pe.brand)
WHERE NOT pe.is_retracted;
```
**Decision rule:** any source with a non-trivial hit-rate → include its view in Task 1.2. A source that joins to <5 entities → defer it (note in plan), keep v1 lean.

### Task 0.5: Commit the recorded results
```bash
git add docs/plans/2026-06-17-reports-engine-plan.md
git commit -m "plan: record Phase 0 data-feasibility gate results (V1/V2/V3)"
```

---

## PHASE 1 — Engine foundation + The Receipt

### Task 1.1: Migration 072 — insights views

**Files:** Create `db/migrations/072_insights_views.sql`. Deploy via Supabase SQL Editor or Management API (set `User-Agent` header, per CLAUDE.md).

**Step 1:** Write `serial_shrinkers` (always safe — no gate):
```sql
CREATE OR REPLACE VIEW serial_shrinkers AS
SELECT pe.id AS entity_id, pe.brand, pe.canonical_name,
       COUNT(*) AS shrink_count,
       MIN(pc.observed_date) AS first_cut,
       MAX(pc.observed_date) AS last_cut,
       SUM(GREATEST(0, (pc.size_before - pc.size_after) / NULLIF(pc.size_before,0))) AS cumulative_cut_ratio
FROM published_changes pc
JOIN product_entities pe ON pe.id = pc.entity_id
WHERE NOT pc.is_retracted AND NOT pe.is_retracted
GROUP BY pe.id, pe.brand, pe.canonical_name
HAVING COUNT(*) >= 2;
```
**Step 2:** Add `fullcarts_index` (only if V1=BUILD; matched-basket monthly index) OR a `tracked_basket_ppu` fallback view. Add `category_concentration` only if V2=BUILD. Add `cr_corroboration` / `trends_vs_reality` / `usda_confirms` only for sources that passed V3. (Write each with `is_retracted` filters; adjust join keys to Task 0.1 schema.)
**Step 3:** Deploy the migration; verify each view returns rows:
```sql
SELECT COUNT(*) FROM serial_shrinkers;
```
**Step 4: Verify the denormalization invariant still holds (must be 0):**
```sql
SELECT COUNT(*) FROM published_changes pc JOIN product_entities pe ON pe.id=pc.entity_id
WHERE pc.brand <> pe.brand OR pc.product_name <> pe.canonical_name;
```
**Step 5: Commit.**
```bash
git add db/migrations/072_insights_views.sql
git commit -m "feat(db): 072 insights views (serial_shrinkers + gated cuts)"
```

### Task 1.2: Migration 073 — report_issues table

**Files:** Create `db/migrations/073_report_issues.sql`.

**Step 1:** Write:
```sql
CREATE TYPE report_type AS ENUM
  ('receipt','hall_of_shame','hall_of_fame','fullcarts_index','aisle','illusion','watchlist','annual');
CREATE TYPE report_status AS ENUM ('draft','published');

CREATE TABLE report_issues (
  id            UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  type          report_type NOT NULL,
  period        TEXT NOT NULL,                 -- e.g. '2026-06'
  status        report_status NOT NULL DEFAULT 'draft',
  payload       JSONB NOT NULL DEFAULT '{}',   -- frozen auto-section snapshot
  take_md       TEXT,                          -- human Take
  external_facts JSONB NOT NULL DEFAULT '[]',  -- [{key, value, source_url}] (three-bucket gate)
  published_at  TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT now() NOT NULL,
  updated_at    TIMESTAMPTZ DEFAULT now() NOT NULL
);
CREATE UNIQUE INDEX idx_report_issues_type_period ON report_issues (type, period);
CREATE INDEX idx_report_issues_status ON report_issues (status, published_at DESC);
```
**Step 2:** Deploy; confirm `SELECT * FROM report_issues LIMIT 1;` runs.
**Step 3: Commit** `feat(db): 073 report_issues frozen-issue model`.

### Task 1.3: Generation script (pipeline) — TDD

**Files:** Create `pipeline/scripts/generate_report_issue.py`; Test `pipeline/tests/test_generate_report_issue.py`.

**Step 1: Write the failing test** (fake client returns canned view rows; assert payload shape):
```python
from pipeline.scripts.generate_report_issue import build_receipt_payload

class FakeClient:
    def __init__(self, tables): self._t = tables
    def fetch(self, view, **kw): return self._t.get(view, [])

def test_build_receipt_payload_has_required_sections():
    client = FakeClient({
        "published_changes_recent": [{"brand": "Folgers", "pct": -14.7}],
        "serial_shrinkers": [{"brand": "Gatorade", "shrink_count": 3}],
        "restorations": [{"brand": "X"}],
        "dashboard_stats": [{"total_events": 2228}],
    })
    p = build_receipt_payload(client, period="2026-06")
    assert set(["print","gap","receipts","compound","who_it_hits",
                "feature","restoration","community","snapshot"]).issubset(p.keys())
    assert p["receipts"][0]["brand"] == "Folgers"
    assert p["snapshot"]["total_events"] == 2228
```
**Step 2: Run, verify it fails** — `cd pipeline && python -m pytest tests/test_generate_report_issue.py -v` → FAIL (import error).
**Step 3: Implement `build_receipt_payload`** (pure function: takes a client abstraction + period, returns a dict; the real Supabase fetch lives behind the client so the function is unit-testable). Use `typing` (`Dict`, `List`). A separate `main()` wires the real Supabase client + upserts a `draft` row into `report_issues` (status stays `draft`; never publishes).
**Step 4: Run, verify pass.**
**Step 5: Commit** `feat(pipeline): report issue generation (build_receipt_payload + draft upsert)`.

### Task 1.4: Monthly GitHub Action

**Files:** Create `.github/workflows/pipeline_report.yml`.

**Step 1:** Schedule for a few days after the BLS CPI release (e.g. `cron: '0 13 13 * *'` — adjust to the actual release calendar; the script is idempotent on `(type, period)`). Job: `pip install -r pipeline/requirements.txt` → `python3 -m pipeline.scripts.generate_report_issue --type receipt`. Markdown summary in job output (mirror `pipeline_promote.yml`).
**Step 2:** Validate YAML: `python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/pipeline_report.yml'))"`.
**Step 3: Commit** `ci: monthly report-issue draft generation`.

### Task 1.5: Public `/report` + `/report/[period]` (ISR)

**Files:** Create `web/src/app/report/page.tsx`, `web/src/app/report/[period]/page.tsx`, `web/src/app/report/lib.ts`, `web/src/app/report/_components/*`, `web/src/app/report/styles.module.css`. Optional mockup `web/public/mockups/report.html`.

**Step 1:** `lib.ts` server queries the latest `published` issue (and by `period`) via the server Supabase client. `/report` renders latest; `/report/[period]` renders the archived issue; both `export const revalidate = 3600`.
**Step 2:** Section components render from `payload` (one per section in the design §6). Render `<SiteNav />`. Match `FULLCARTS_DESIGN_EXPORT.md` aesthetic.
**Step 3:** Build check — `cd web && npm run build` succeeds; visit `/report` (draft-only DB → friendly "first issue coming" empty state).
**Step 4: Commit** `feat(web): /report + /report/[period] ISR pages`.

### Task 1.6: `<DashboardSnapshot>` component

**Files:** Create `web/src/app/report/_components/DashboardSnapshot.tsx` (shared; later reused by `/dashboard`).
**Step 1:** Renders compact tiles from `payload.snapshot` (total documented, this-month cuts, restoration rate, top parent or serial-shrinker count, Index-or-fallback). Pure presentational (props in).
**Step 2:** Embed in `/report`. `npm run build` + `npm run lint` clean.
**Step 3: Commit** `feat(web): DashboardSnapshot tiles`.

### Task 1.7: Admin editor + publish route handler

**Files:** Create `web/src/app/admin/reports/page.tsx` (draft/published list), `web/src/app/admin/reports/[id]/page.tsx` (editor), `web/src/app/api/admin/reports/[id]/route.ts` (PATCH: save take/external_facts; POST: publish). Reuse `web/src/lib/admin-auth.ts`; `middleware.ts` already guards `/admin`.

**Step 1:** Editor: textarea for `take_md`, repeatable `external_facts` rows (`key`, `value`, **required `source_url`** — enforce the three-bucket gate in the route handler), live preview, Publish button.
**Step 2:** **Route handler, NOT a server action** (CLAUDE.md gotcha). On publish: set `status='published'`, `published_at=now()`, then `revalidatePath('/report')` + `revalidatePath('/report/'+period)` (revalidating OTHER routes is fine from a route handler). Reject publish if any `external_facts` row lacks `source_url`.
**Step 3:** Manual test: generate a draft (run the script locally against a test period), edit, publish, confirm `/report` shows it.
**Step 4: Commit** `feat(web): admin report editor + publish route handler`.

### Task 1.8: Phase 1 wrap

**Step 1:** Update CLAUDE.md (web routes table + migrations list + a "Reports engine" architecture note). **Step 2:** Sanity-invariant query = 0. **Step 3: Commit + push** `docs: document reports engine (routes, migrations, flow)`.

---

## PHASE 2+ (scoped — separate plans when reached)
- **Phase 2:** `/dashboard` live ISR page (full tile set) · Hall of Shame (tier list) + Restoration Report `type`s on the same engine.
- **Phase 3:** ESP integration + email signup on `/report` + send published issues; ManyChat CAUGHT→link wiring (human-run).
- **Phase 4:** FullCarts Index report (post-V1), Illusion of Choice (post-V2), Aisle, Watchlist, Annual.

## Testing notes
- Pipeline: `cd pipeline && python -m pytest tests/` — keep `build_receipt_payload` a pure function behind a client abstraction so it tests without network.
- Web: `cd web && npm run build && npm run lint` after each web task.
- DB: after every migration, re-run the denormalization sanity query (must be 0) and `is_retracted` spot-checks.
