# FullCarts Reports Engine — Design

**Date:** 2026-06-17
**Status:** Approved direction (brainstorm complete) → ready for implementation plan
**Related:** `docs/plans/2026-06-10-face-forward-content-strategy.md` · `docs/content/content-angles.md` (§5 Convergence Peg Library) · the CPI Take in `docs/content/batches/2026-06-14-batch.md` (the narrative model)

---

## 1. Purpose

Turn the FullCarts database into a **recurring, shareable report franchise** delivered as the payoff to
the "Comment CAUGHT" video CTA (see `content-rules.md` §5). Not one newsletter — a **shared engine** that
powers several reports + a live dashboard, all drawing on the same data + external sources.

Three layers:
1. **Insights layer** — SQL views computing differentiated cuts (the moat: not the size numbers, but how
   we slice them and fuse them with outside data).
2. **Report franchise** — multiple recurring reports on a shared template + generation flow.
3. **Dashboard** — a live metrics surface; a snapshot embeds in every report and doubles as a press/X asset.

**The flagship** is **The Receipt** (monthly, drops on the BLS CPI print day). Its narrative spine is the
proven CPI video arc — `HOOK → RECEIPT → COMPOUND → WHO IT HITS → TAKE → CTA` — expanded into a written
report with DB sections folded into the gaps the 85s video can't fit.

---

## 2. Decisions (locked)

| Decision | Choice |
|---|---|
| Flagship cadence | **Monthly**, anchored to the BLS CPI release day |
| Delivery | **Web page now** (`/report`), **email capture layered on later** — the page is also the signup landing |
| Authoring | **Auto spine + human Take** — DB sections generate; the Take + external-fact sections are human |
| Anchor insight cuts | **FullCarts Index** (validate first), **Illusion of Choice**, **Serial Shrinkers** |
| v1 external sources | **Consumer Reports**, **Google Trends**, **USDA product history** |
| Scope | Build the **engine** (insights layer + franchise + dashboard), flagship report first, others as fast-follows |

---

## 3. Data feasibility (verified structurally; two live gates remain)

Assessed from the schema (`db/migrations/`). Live row-count/density checks require DB credentials and are
**Phase 0** of the implementation plan.

| Cut | Structural verdict | Risk / live gate |
|---|---|---|
| **Serial Shrinkers** | ✅ self-join on `published_changes` by `entity_id` | none — safe |
| **FullCarts Index** | ✅ `variant_observations` has `price`, `size`, `size_unit`, generated `price_per_unit`, `observed_date`, `retailer`, `source_type`; `open_prices_data` is an independent feed | ⚠️ **density unknown** — need enough SKUs with ≥2 observations across enough months for a stable matched-basket index. **Gate V1.** |
| **Illusion of Choice** | ✅ `corporate_tree` view exists | ⚠️ **`corporate_tree` is empty until the Wikidata manufacturer backfill runs** (CLAUDE.md). **Gate V2.** |
| **CR corroboration** | ✅ `consumer_reports_findings` table | join hit-rate to entities unknown — **Gate V3** |
| **Trends vs reality** | ✅ `google_trends_data` table | coverage unknown — **Gate V3** |
| **USDA confirms** | ✅ `usda_product_history` (7 releases) | join hit-rate unknown — **Gate V3** |

### FullCarts Index — method (pending V1)
Compute a **matched-basket** price-per-unit index (Laspeyres-style): for each pair of periods, include only
SKUs (`variant_id`) observed in **both** periods, so the index measures price-per-unit change on a *fixed
basket*, not composition drift. This directly answers the CPI-video gate flag #5 ("our scrape counts are
coverage-biased") — the matched basket controls for it.
- **Filter:** US prices, non-discounted where flagged, sane unit normalization (oz/g/mL/L/count families).
- **Output:** a monthly index value + YoY %, plotted against `fred_cpi_data` (official CPI) — "the unofficial
  inflation number."
- **Fallback if density is thin (V1 fails):** report a coarser, honestly-scoped metric — "tracked basket of
  N products, price-per-unit up X%" — and defer the headline "Index" framing until coverage grows. Never
  publish an index thin enough to swing on one SKU.

---

## 4. Architecture

Stack reuse: Next.js App Router + Supabase + ISR + GitHub Actions cron + existing views, mirroring current
admin/route-handler/cron patterns. **Reuse, don't duplicate** the `/insights` views (`brand_index`,
`category_stats`, `restorations`, `corporate_tree`, `shrinkflation_timeline`, `cpi_shrinkflation_context`,
`news_brand_mentions`, etc.); the insights layer *adds* new cuts alongside them.

### 4.1 Insights layer (new SQL views — migration ~072)
- `serial_shrinkers` — entities with ≥2 events; streak count, cumulative cut, last-cut date.
- `fullcarts_index` — monthly matched-basket price-per-unit index (+ YoY), method above. *(gated on V1)*
- `category_concentration` — extends `corporate_tree`: % of a category's events tracing to top-N parents. *(gated on V2)*
- `cr_corroboration` — `consumer_reports_findings` × `published_changes` by entity/brand.
- `trends_vs_reality` — `google_trends_data` × event volume, by month/brand.
- `usda_confirms` — `usda_product_history` size deltas × `product_entities` (third-party confirmation).
- `ahead_of_headline` — first `observed_date` vs `news_brand_mentions` spike (lead-time in months). *(fast-follow)*

All views must respect `is_retracted` filters (see CLAUDE.md gotchas) and the denormalized-brand invariant.

### 4.2 Report data model (migration ~073) — frozen issues + live dashboard (hybrid)
- **`report_issues`** — one row per published issue. Columns: `id`, `type` (enum: `receipt`,
  `hall_of_shame`, `hall_of_fame`, `fullcarts_index`, `aisle`, `illusion`, `watchlist`, `annual`),
  `period` (e.g. `2026-06`), `status` (`draft`→`published`), `payload` JSONB (the frozen auto-section data
  snapshot), `take_md` (the human Take), `external_facts` JSONB (sourced, with `source_url` per fact),
  `published_at`, audit cols. Issues are **immutable once published** so the archive + future email send a
  stable artifact; the dashboard stays live.
- Why frozen issues (not pure ISR): stores the human Take, lets you review/verify before publish, and gives
  email (Phase 2) a fixed payload to send. The **dashboard** is the opposite — a live ISR page.

### 4.3 Generation flow (the "auto spine + human Take")
1. **Monthly cron** (`.github/workflows/pipeline_report.yml`, runs on/after the CPI release date) → a
   `pipeline/scripts/generate_report_issue.py` pulls every auto section from the views → writes a `draft`
   `report_issues` row (`payload`), leaving `take_md` + `external_facts` empty.
2. **Admin review** at `/admin/reports/[id]` (SSR, behind `admin_session`) → write the Take, fill/verify the
   external-fact sections (Rockets & Feathers, profits, CEO quotes — each needs a `source_url`, three-bucket
   gate), preview.
3. **Publish** → `status='published'`, route handler `revalidatePath('/report', '/report/[period]')`
   (route handler, not server action — see CLAUDE.md gotcha).
4. **(Phase 2)** Email the published issue payload via an ESP.

### 4.4 Web surfaces (Next.js routes)
| Route | Type | Notes |
|---|---|---|
| `/report` | ISR | Latest published issue (the CAUGHT link target). |
| `/report/[period]` | SSG + ISR | Archive of past issues (e.g. `/report/2026-06`). |
| `/dashboard` | ISR | Live metric tiles across cuts; each tile links to the report that explains it. |
| `/admin/reports` + `/admin/reports/[id]` | SSR | Draft queue + per-issue editor (Take + external-fact verify + publish). |

All public routes render `<SiteNav />`; design matches `FULLCARTS_DESIGN_EXPORT.md` (dark graphite / Space
Grotesk / JetBrains Mono / alert red). Mockup in `web/public/mockups/` per existing convention.

### 4.5 Dashboard tiles (v1)
Total documented (growing) · this month's new cuts · **FullCarts Index vs CPI** *(or fallback)* · restoration
rate · worst category this period · top parent company (Illusion of Choice) · serial-shrinker count · search-
interest spark (Google Trends). A `<DashboardSnapshot>` component renders a compact subset for embedding in
reports + screenshotting for X.

---

## 5. The report franchise (engine reuse)

The flagship ships first; the rest are `report_issues.type` variants on the same template + flow, differing
only in section composition + cadence.

| Report | Cadence | Core source |
|---|---|---|
| **The Receipt** (flagship) | Monthly (CPI day) | full stack |
| **Hall of Shame** (tier list S/A/B/C) | Quarterly | `brand_index` severity (reuse Tier List carousel format) |
| **Hall of Fame / Restoration Report** | Quarterly | `restorations` |
| **The FullCarts Index** | Monthly | `fullcarts_index` *(post-V1)* |
| **The Aisle Report** (rotating category) | Monthly | `category_stats` + one category |
| **Illusion of Choice** (one parent co.) | Quarterly | `corporate_tree` *(post-V2)* |
| **The Watchlist** (predictions + seasonal) | Seasonal | `content_candidates` + calendar (peg F) |
| **Year in Shrinkflation** | Annual | everything |

---

## 6. The Receipt — section map (flagship v1)

Spine = the CPI video arc; ✅ = auto from views, ✍️ = human, 🔎 = external-fact (sourced, three-bucket gate).

1. **The Print** — this month's CPI (headline AND food-at-home, named separately) + real BLS screenshot. 🔎
2. **The Gap** — same price, less inside, +%/oz; the visible-vs-hidden thesis. ✅ (evergreen mechanic)
3. **This Month's Receipts** — new cuts logged this month, ranked by %. ✅ `published_changes` ≤30d
4. **The Compound** — family-of-four projection, labeled @headline rate. ✅ (arithmetic, labeled projection)
5. **Who It Hits** — regressive impact + "it's not you." ✅ + a budget-share stat
6. **The Feature** (rotating peg) — Illusion of Choice / Serial Shrinkers / How They Hid It / Rockets &
   Feathers. ✅ or 🔎 per peg
7. **The Take** — the prediction/POV (the moat, §6). ✍️
8. **The Restoration Corner** — "~1 in 100 ever comes back." ✅ `restorations`
9. **You Caught These** — featured reader submissions. ✅ `raw_items` `source_type='community_tip'`
10. **Dashboard snapshot** + **CTA** (submit / share / next issue). ✅

Gate discipline from the CPI script carries over verbatim: name headline vs food-at-home separately, label
the projection, no politics, real BLS screenshot, external facts sourced not asserted.

---

## 7. Cross-promotion loop

The monthly CPI video's CTA becomes *"I put the full breakdown — every receipt, the compound math, who got
caught this month — in this month's report. Comment CAUGHT and I'll send it."* Video sells the report; report
deepens the video; both anchor to the same CPI print.

---

## 8. Phasing

- **Phase 0 — Validation gates (do first):** V1 FullCarts Index density (decide method or fallback) · V2
  `corporate_tree` population (run `wikidata_manufacturer_backfill` or defer Illusion) · V3 external-source
  join hit-rates (CR / Trends / USDA).
- **Phase 1 — Engine + flagship:** insights views (072) · `report_issues` (073) · generation script + cron ·
  `/report` + `/report/[period]` · `/admin/reports` editor · `<DashboardSnapshot>`.
- **Phase 2 — Dashboard + franchise:** `/dashboard` live page · Hall of Shame + Restoration Report types.
- **Phase 3 — Email:** ESP integration, signup on `/report`, send published issues; ManyChat CAUGHT → link.
- **Phase 4 — More cuts/reports:** FullCarts Index report (post-V1), Illusion (post-V2), Aisle, Watchlist, Annual.

## 9. Out of scope (YAGNI for v1)
Email send (Phase 3) · personalization/alerts · per-user dashboards · the full franchise (Phase 4) · any cut
that fails its Phase 0 gate (fall back, don't fabricate).
