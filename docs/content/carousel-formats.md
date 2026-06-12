# FullCarts Carousel Formats — the shelf of repeatable templates

**Date:** June 12, 2026
**Parent:** `docs/content/posting-schedule.md` (the "Repeatable Series (Carousels)" section) + the
face-forward strategy. **Purpose:** the **single source of truth** for the repeatable carousel
templates. Pick a format off this shelf → drop in this week's datapoint(s) → render the stills. Do
**not** improvise a new structure each week — that's how the lineup/hook/gate mistakes creep in.

Every carousel is **1080×1350 (4:5)**, **one slide per frame** (render stills `0..N`), and must clear
the three gates (`content-rules.md`): data-driven · approved-claims (§1 only) · three-bucket evidence.

## How to render (sandbox + laptop)
```bash
cd video && npm install   # first time
# Per slide (one frame = one slide):
npx remotion still <CompId> out/<slug>/slide-NN.png --frame=N --props=src/props/<slug>.json
```
- **First render downloads Chrome Headless Shell** (host `remotion.media`). If your network policy
  blocks it (the cloud sandbox does — 403), pass a local Chromium:
  `--browser-executable=/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell`.
- **Product photos / brand logos are fetched at render time** and most hosts 403 in the sandbox —
  image slides render on a **network-open machine**; in-sandbox they fall back to bars/monograms.
- Round the banner number **down** ("2,229 → 2,200+"), and re-pull `approved-claims.md` §1 each batch.

---

## 1. Guess the Cut — gamified quiz ⭐ *(weekly)*
**Composition:** `GuessTheCut` · **Props:** `src/props/carousel-guess-the-cut.json` · `durationInFrames = items*2 + 2`

- **Swipe mechanic:** a per-product **Q→A open loop** — slide shows the *before* size with the *after*
  withheld behind a red "?"; the **next** slide reveals the −%. The answer is never on the same slide.
- **Structure:** cover → for each item `[Q, A]` (ranked **ascending**, biggest cut last) → CTA.
- **Images:** every Q/A slide reserves a right-hand **product-photo panel**. Set `item.image` to the
  real `product_entities.image_url` (Bucket-1); absent → a labelled placeholder marks the reserved zone.
  Photos fetch at render time (sandbox 403s them → render with images on a network-open machine).
- **Bucket:** entertainment / gamified.
- **Cover:** "Guess the cut — same price, less inside. Most people lowball every one. swipe →"
- **🚩 Gate watch-out:** every `equiv` must be **arithmetic, not embellishment** — 32→28 fl oz is
  "half a cup", **NOT** "a full glass". Keep the lineup **category-coherent** *or* drop cross-product
  analogies entirely. Order ascending so the climax (e.g. oats −50%) lands on the final reveal.

```sql
-- High-magnitude AND well-evidenced (credibility), recognizable brands; order ASC at render time.
SELECT brand, product_name, size_before, size_after, size_unit,
       round((1 - size_after/NULLIF(size_before,0))*100,1) AS pct, evidence_count
FROM published_changes
WHERE COALESCE(is_retracted,false)=false
  AND size_before IS NOT NULL AND size_after IS NOT NULL AND size_after < size_before
  AND size_after/NULLIF(size_before,0) BETWEEN 0.4 AND 0.9
  AND evidence_count >= 15
ORDER BY pct DESC LIMIT 12;
```
**Worked example (shipped):** Gatorade −12.5% → Gaviscon −16.7% → Cadbury Freddo −18.9% →
Aquafresh −25% → Sainsbury's Oats −50%. Equivalences: "half a cup" · "a sixth of the bottle" ·
"nearly a fifth of the egg" · "1 in every 4 tubes" · "half. the. bag." (all arithmetic).

## 2. Monthly Shrink List — ranked countdown *(monthly, on the CPI print)*
**Composition:** `Carousel` (the ranked engine) · **Props:** `src/props/carousel-monthly-shrink-list.json` · `durationInFrames = items + 2`

- **Swipe mechanic:** count **5→1** to the worst (the #1 reveal is the payoff).
- **Data:** top 5 by `pct` with `observed_date` in the last ~30–45 days (filter the query below by date).
- **Bucket:** recency / ranked. **Cover:** "5 things that quietly got smaller in [Month] 👀 swipe →"

## 3. Worst Offenders Hall of Fame — repeat shrinkers *(monthly)*
**Composition:** `Carousel` (same engine, **different sort key**) · `durationInFrames = items + 2`

- **Swipe mechanic:** climb the ranking; #1 worst last. **Bucket:** ranked / "it's the whole store".
- **Data:** brands ranked by **count** of shrink events; show each brand's *signature worst single cut*
  on its slide (the `Carousel` slide needs a before/after, so use the brand's biggest documented cut).
```sql
SELECT brand, count(*) AS events FROM published_changes
WHERE COALESCE(is_retracted,false)=false AND size_after < size_before
GROUP BY brand HAVING count(*) >= 3 ORDER BY events DESC LIMIT 5;
```
> **Note:** Monthly Shrink List and Hall of Fame are the **same `Carousel` composition** with a
> different ranking — don't build a new composition for either; just swap the props/sort.

## 4. Tier List — graded S–D *(bi-weekly; rotate the axis)*
**Composition:** `TierList` (swipe-reveal, already built) · `durationInFrames = tiers + 2`

- **Swipe mechanic:** reveal **bottom-up D→S** (one tier per swipe), the **full list as the LAST slide**.
- **Repeatability = the axis you slice on** (this is the whole point — never the same brands twice):
  - **By category (default):** chocolate, soda, cereal, chips, coffee, toothpaste, ice cream…
    (`brand_index.primary_category` — **normalize case**, `snacks`/`Snacks` & `dairy`/`Dairies` split).
  - **By season (overlay):** Halloween candy · back-to-school lunchbox · Super Bowl snacks · holiday tins.
  - **By parent company:** "every brand Mondelez owns, ranked" (`corporate_tree`).
- **Cover:** "I graded every [category] brand on shrinkflation. Swipe to the S-tier 🚩"
```sql
SELECT brand, primary_category, worst_delta_pct FROM brand_index
WHERE lower(primary_category) = lower(:category) AND NOT is_retracted
ORDER BY worst_delta_pct DESC;  -- bucket into S/A/B/C/D by pct bands
```

## 5. CPI vs. Reality — macro newsjack *(monthly, CPI release day)* — STUB
**Composition:** `CPIvsReality` (stub — functional, polish TODO) · `durationInFrames = items + 2`

- **Swipe mechanic:** cover = the official CPI number → per-product "official +X% / box −Y%" → CTA.
- **Bucket:** newsjack / macro. Borrows institutional authority; picks a credible, scheduled fight.
- **🚩 Gate guardrail:** CPI measures **price up**; our number measures **size down** — two *different*
  hidden hikes. Frame as "the half inflation barely counts," **NEVER** "CPI is wrong by Y%."
```sql
-- Real YoY CPI per category (latest vs 12 months prior) from fred_cpi_data; pair with our category shrink.
SELECT series_name, category, observation_date, value FROM fred_cpi_data
WHERE category = :cat ORDER BY observation_date DESC LIMIT 13;
```

## 6. Caught Before/After — single-product deep dive *(weekly, video companion)* — STUB
**Composition:** `CaughtBeforeAfter` (stub) · `durationInFrames = 5`

- **Swipe mechanic:** cover ("notice anything?") → the cut → the per-unit price math → the receipt → CTA.
- **Bucket:** single-product; **cross-format reinforcement** with that week's Wednesday `Caught:` video.
- **Bucket-1 dependency:** `image` = real `product_entities.image_url` (renders on a network-open
  machine; falls back to a typographic panel). The price-math slide needs a unit price — thin in the
  DB, so it's optional (omitted → a qualitative "price-per-unit went up" slide renders instead).

## — They Did It Again — the staircase *(BENCHED)*
**Composition:** none yet. **Why benched:** `published_changes` re-records the *same* change at multiple
dates (Gatorade shows "12.5%" ×8 — one cut re-scraped, **not** a staircase). A true staircase needs a
**verified monotonic size sequence** (100→90→80→75). Build only after a per-product dedup pass. Good
candidates: Crest, Pringles, Cadbury Dairy Milk.

---

## Composition ↔ format map (quick reference)
| Composition | Formats it serves | Status |
|---|---|---|
| `GuessTheCut` | Guess the Cut | **built** |
| `Carousel` | Monthly Shrink List · Worst Offenders · 5 Stealth Shrinks · before/after presets | built (pre-existing) |
| `TierList` | Tier List (category / season / parent) | built (pre-existing) |
| `ItsNotYou` | It's Not You (emotional) | **built** |
| `CPIvsReality` | CPI vs. Reality | **stub** |
| `CaughtBeforeAfter` | Caught Before/After | **stub** |

> **It's Not You** (`ItsNotYou`, `durationInFrames = receipts + 4`): opener (the feeling, not a number)
> → the unspoken thought → receipts → "it's not you" resolution → persona CTA. Emotional bucket; pulls
> the feeling from `content-angles.md` §4. Cover: "You're not crazy. That box really did get smaller."
