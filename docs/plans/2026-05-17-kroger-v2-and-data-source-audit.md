# Kroger v2 + Data Source Audit

**Date:** 2026-05-17
**Branch:** `claude/modest-ramanujan-b09990` (continuing the PR from yesterday)

## Part 1 — Kroger change analyzer hardening

### Step 1: Stop the bleeding

- Discarded the 29 pending `kroger-change-v1` claims directly (all noise from
  Kroger API size-toggling).
- Added a `kroger_change` rule to [auto_decline_pending.py](pipeline/scripts/auto_decline_pending.py):
  any claim stamped `kroger-change-v1` (or v0.x) is auto-discarded. Future v2+
  claims pass through untouched.

### Step 2: Harden the analyzer

[analyze_kroger_changes.py](pipeline/scripts/analyze_kroger_changes.py) rewritten
to v2 with four guards:

1. **Unit family stability** — `oz → fl oz` and other cross-family flips
   (mass→volume, volume→count) are skipped. Kroger's API toggles between
   representations for the same SKU; cross-family is a data-quality red flag,
   not real shrinkflation.
2. **Prior stability** — old size must hold for ≥3 consecutive observations
   before the change.
3. **Post stability + no revert** — new size must persist after the change
   AND the old size must not reappear later in the lookback window.
4. **New size unseen earlier** — if the post-change size already appeared
   before the transition, it's oscillation, not a one-way change.

`EXTRACTOR_VERSION` bumped to `kroger-change-v2`. New claims set
`raw_items.source_url = https://www.kroger.com/p/<upc>` and
`raw_payload.title = "<brand> <product>"` so the admin UI renders a working
link and title.

### Step 3: Admin UI

[web/src/app/admin/claims/page.tsx](web/src/app/admin/claims/page.tsx):
- Added a `kroger_change` entry to `SourceBadge` config (cyan).
- Added `new_date` fallback to `formatDate` so Kroger analyzer claims show a
  date in the card header.
- Title + link rendering already worked once the v2 analyzer started writing
  `payload.title` and `source_url`. No further changes needed there.

### Verification

- New unit tests at [pipeline/tests/test_analyze_kroger_changes.py](pipeline/tests/test_analyze_kroger_changes.py): 8 tests, all pass. Covers happy path,
  oscillation, revert, insufficient prior stability, cross-unit-family,
  cross-unit-same-family, new-size-seen-earlier, missing observations.
- Replayed v2 against the variant population that v1 flagged: **29 → 2**
  (93% noise reduction). The 2 residuals are still upstream Kroger
  size-parsing quality issues (Sculpey clay "8lb→3lb", Pillsbury Cinnamon
  Rolls "8lb→3lb") — not analyzer's fault but worth surfacing for manual
  review.
- Dev server compiles clean with the UI changes (no admin-password access to
  visually verify a v2 claim card yet — none exist until next scheduled
  analyzer run).

## Part 2 — Audit of other data sources

Total `raw_items` and downstream claims by source (estimated counts where
exact would have timed out):

| source_type | raw_items | claims (any status) | useful? |
|---|---:|---:|---|
| reddit | ~19.2K | (via haiku-v1: ~30K) | yes — primary signal |
| news | ~1.4K | (via haiku-v1) | yes — secondary |
| gdelt | ~7.4K | (via haiku-v1) | yes — bulk for events |
| openfoodfacts | ~43.8K | (via haiku-v1, mostly discarded) | low — catalog data |
| kroger_api | ~5.4K | n/a — observations not claims | input to analyzer |
| **kroger_change** | **81** | **81** | **broken (v1) — fixed in v2 this PR** |
| usda | ~5.3M | n/a — feeds usda_size_change | input |
| **usda_size_change** | **3,800** | **85 (all pending)** | **untapped — see below** |
| open_prices | ~2.5K | 0 | unused — price-only, no extraction wired |
| wayback | 0 | 0 | dormant |
| walmart_api (observations) | 0 | 0 | scraper not producing |
| usda_nutrition / community_tip / receipt / fred / bls (raw_items) | 0 each | 0 | use dedicated tables |
| fred_cpi_data (dedicated) | ~8.3K | n/a | context for charts |
| bls_shrinkflation (dedicated) | ~959 | n/a | context for charts |

### Critical findings

**1. 43 published_changes events on production were seeded by v1 noise claims.**

These got past v1's lax detection and were promoted. Sample of what's
currently sitting in `published_changes` and on the brand pages:

- Charmin Ultra Soft Toilet Paper: 33.4 oz → 12 fl oz (toilet paper isn't in fl oz)
- Sculpey Bake Shop polymer clay: 8 lb → 3 lb (clay isn't in pounds)
- Home Depot Holiday string lights: 14 oz → 8 oz (not even a Kroger product)
- Gain detergent: 33.4 oz → 12 fl oz (unit family flip)
- Bath & Body Works Lipgloss: 33.4 oz → 12 fl oz
- Procter & Gamble Ariel laundry detergent: 14 oz → 8 oz (P&G is the parent, not the brand)
- Target Seasonal/Scented Candle: 5 lb → 3 lb

**This is brand-page pollution.** Most of these have `evidence_count=1` or `2`
(no other sources corroborating). A handful share an event with a real news
claim — for those we'd want to strip the v1 claim from `evidence_summary`
without nuking the whole event.

This PR does **not** delete them yet — that's destructive on public-facing
data and needs your explicit OK first. When you're ready, a one-off
`cleanup_kroger_v1_events.py` could:
- Find all `published_changes` where `evidence_summary` references a
  `claim_id` whose `extractor_version='kroger-change-v1'`.
- Strip the v1 claim entry and decrement `evidence_count`.
- If `evidence_count` drops to 0, mark the event `is_retracted=true`
  (don't delete — keep the audit trail).

**2. 85 USDA size-change claims sitting in `pending`, never reviewed.**

The `usda-size-change-v1` analyzer compares the same UPC across USDA FoodData
Central releases (quarterly). It found 85 candidate shrinkflation events,
none of which have been triaged. Sample of plausible-looking ones:

- MACRINA BAKERY Ciabatta Burger Buns: 14 oz → 12.8 oz (-8.6%)
- Udi's Vanilla Granola: 12 oz → 11 oz (-8.3%)
- California Pizza Kitchen Crispy Thin Crust Pepperoni Pizza: 13.6 oz → 12.9 oz (-5.1%)
- Chobani Key Lime Greek Yogurt: 5.3 oz → 4.5 oz (-15.1%)
- Arizona Iced Tea: 23 fl oz → 22 fl oz (-4.3%)
- Catallia Flour Tortillas: 34.6 oz → 31 oz (-10.4%)

These are exactly the kind of subtle CPG shrinkflation FullCarts exists to
detect. They're blocked from auto-approval because `auto_approve_claims.py`
hard-requires `image_storage_path` and USDA doesn't have product images.

Three options to unblock them:
- **(a) Manual triage** — you batch-approve in admin. ~85 claims is doable in
  one sitting.
- **(b) Relax image requirement for USDA** — modify `auto_approve_claims.py`
  to skip the image check when `extractor_version='usda-size-change-v1'`,
  because the cross-USDA-release diff *is* the evidence. Other guards
  (sub-scores, CPG-unit allowlist) still apply.
- **(c) Add visual evidence from USDA's hosted product images.** USDA FDC
  has product photos for many SKUs — could backfill them. More work.

My recommendation: (b) for speed, but only after also adding a noise filter
for USDA (kill <-50% shrinks and giant upsizes — there are 9+ of those in
the current 85, likely SKU swaps where one UPC was reused for a different
product).

**3. `open_prices` is dead weight in current form.**

2,533 raw_items pulled, zero downstream claims. The Open Prices project is
price-only data; we don't have an analyzer that detects size changes from
it (size data is sparse). Either:
- Wire up an analyzer that uses Open Prices for cross-corroboration of
  Kroger prices, or
- Pause the scraper. The data sits idle and isn't influencing brand pages.

**4. `wayback` and `walmart` scrapers are dormant.**

Both have 0 raw_items / 0 observations. The Wayback feature was scoped but
never produced data; Walmart appears to have been disabled or is failing
silently. Neither blocks anything, but the GitHub Actions cron is still
running them. Worth turning off cron schedules until/unless they're revived.

### Sources that are healthy

- **reddit + news + gdelt via haiku-v1**: the main pipeline is producing
  4,205 matched + 709 evidence claims. After yesterday's stuck-approved
  cleanup, 0 claims are stuck.
- **openfoodfacts**: `auto_decline_pending` correctly culls catalog rows
  without before/after sizes. The ones that survive are real shrinkflation
  signals from OFF product history.
- **fred_cpi_data + bls_shrinkflation**: dedicated tables, used for chart
  context. ~8.3K + ~959 rows.

## Recommended next steps

In priority order:

1. **Re-enable the kroger_change cron** with v2 — should produce ~0-2 high-
   quality claims per week instead of dozens of noise.
2. **Decide on the 43 polluted published_changes** — give the OK to write
   `cleanup_kroger_v1_events.py`.
3. **Triage the 85 USDA pending claims** — either bulk approve via admin or
   add the USDA bypass to `auto_approve_claims.py`.
4. **Pause or fix dormant scrapers** — open_prices, wayback, walmart.
