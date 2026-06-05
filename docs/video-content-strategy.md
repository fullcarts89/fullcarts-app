# FullCarts Faceless Video Content Strategy

A repeatable faceless (no on-camera presenter) short-form video system built
directly on top of the FullCarts shrinkflation database. Designed for vertical
platforms (YouTube Shorts, TikTok, Instagram Reels) with a monthly long-form
crossover for YouTube proper.

## Core thesis

The moat is **not** "shrinkflation content" — anyone with a phone can rant about
a smaller cereal box. The moat is the database: **~8,900 source-cited events**,
before/after evidence, time-series observations, and a corporate ownership tree,
all refreshed daily by the scrapers. The format must do the one thing a lone
creator can never do at scale: **receipts, on demand, with proof.**

Every beat of every video maps to a named field in an existing view or RPC, so
videos can be generated from a query rather than hand-authored. That is what
makes this repeatable.

---

## The flagship format: "The Shrink Report"

A 30–45s vertical video built from a single `content_candidates` row. That view
already scores rows 0–60 for image quality + delta magnitude + recency, so it is
literally a "what should I post today" feed.

### The 6-beat skeleton

| Beat | Time | On screen | Data source |
|---|---|---|---|
| **1. The Hook** | 0–3s | One product photo, snap-zoom, red number slams in | `content_candidates.image_url`, `size_delta_pct` |
| **2. The Reveal** | 3–10s | Before→after size animates (e.g. "19.3oz → 16.5oz") | `size_before`, `size_after`, `size_unit` |
| **3. The Receipt** | 10–18s | The actual Reddit post / news headline that caught it, with author + excerpt | `event_evidence_summary.sources[]` (`author`, `body_excerpt`, `domain`, `date`) |
| **4. The Pattern** | 18–28s | "This is [Brand]'s Nth shrink" + their worst delta | `brand_index` (`shrinkflation_events`, `worst_delta_pct`) |
| **5. The Boss** | 28–36s | "And [Brand] is owned by [Parent], who've shrunk N products" | `corporate_tree` (`manufacturer`, `total_shrinkflation_events`, `top_brands`) |
| **6. The Loop / CTA** | 36–45s | "We've documented 8,947 of these. Full receipts at fullcarts.org" | `dashboard_stats()` |

**Why the escalation matters:** a normal shrinkflation video stops at beat 2
("look, smaller!"). This format escalates — *here's who noticed → here's the
brand's rap sheet → here's the conglomerate behind it.* That escalation is only
possible because of the database, and it is what drives stitches, duets, and
"do my cereal next" comments.

---

## The viral hook bank (rotate the first 3 seconds)

The hook is the whole game in faceless short-form. Maintain ~10 templates and
fill them from data:

1. **The accusation** — "Did you notice [Brand] just shrank this 22%?" (`worst_delta_pct`)
2. **The receipt drop** — "A Reddit user counted the chips. They were right." (`sources.author` + `body_excerpt`)
3. **The streak** — "This is the 7th time [Brand] has done this." (`shrinkflation_events`)
4. **The conglomerate** — "One company owns these 12 brands. All of them shrank." (`corporate_tree.top_brands`)
5. **The macro betrayal** — "Food prices 'only' rose 2%. Here's the part the CPI doesn't show." (`cpi_shrinkflation_context`)
6. **The restoration twist** — "A brand actually gave the size BACK. (Rarer than you think.)" (`restoration_events`)
7. **The skimp** — "Same size. Less protein. More filler." (`skimpflation_events.nutrient_deltas`)
8. **The cost-of-air** — "If you spend $150/week on groceries, $X of it is now literally air." (basket calculator)
9. **The CR cosign** — "Consumer Reports flagged it too." (`consumer_reports_findings`)
10. **The leaderboard** — "The 5 worst offenders of 2026 so far." (`brand_rankings`)

---

## The series lineup

Run a *channel of recurring segments*, not one format, so the audience builds
appointment habits. Each maps to a data asset → effectively infinite episodes,
all regenerable from a query.

- **"Shrink of the Day"** (daily) → top `content_candidates` row. The bread and butter.
- **"Repeat Offenders"** (weekly leaderboard) → `brand_rankings` top 8. Highly stitchable.
- **"Who Owns Your Cart?"** (weekly) → `corporate_tree`. The conglomerate angle
  reframes individual gripes into a system. **Most defensible series** — nobody
  else has the ownership graph wired to the events.
- **"The Air Tax"** (interactive) → basket calculator, "X% of your $Y is air."
- **"Skimpflation Court"** → `nutrient_deltas` before/after macro charts. Health-angle crossover audience.
- **"They Gave It Back"** → `restoration_events`. Rare, positive, pattern-breaking
  (the algorithm rewards variety) and it proves the channel is *data*, not just outrage.
- **"The Receipts"** → `event_evidence_summary.sources` montages. "You said it. We documented it." Community flywheel.
- **"CPI vs Reality"** (monthly, long-form) → the 4-line macro chart
  (`shrinkflation_timeline` + BLS + FRED + Google Trends). The credible YouTube-proper piece.

---

## The visual system

Faceless means the data *is* the talent. Lock a rigid template so production is
copy-paste and the brand is instantly recognizable. Reuse the existing design
language (`FULLCARTS_DESIGN_EXPORT.md`: dark graphite, Space Grotesk, JetBrains
Mono, alert red).

- **The slam number** — `size_delta_pct` in giant alert-red mono, animates in on
  the beat drop. This is the signature shot; make it as recognizable as a
  countdown timer.
- **Before/after morph** — product image with a shrinking outline + size labels animating down.
- **The receipt card** — a styled "screenshot" of the source (`author`, `domain`,
  `body_excerpt`, `date`). Looks like proof, *is* proof.
- **The rap sheet** — brand scorecard (`worst_delta_pct`, `shrinkflation_events`,
  `first_detected`→`last_detected` span).
- **The ownership tree** — animated org-chart from `corporate_tree.top_brands`
  (thumbnails are included in the JSON array).
- **The step-chart** — reuse the existing SVG step-chart component from
  `/products/[id]` as an animated trajectory.

---

## Why this is a moat (the framework)

Position the channel as **"the world's receipt drawer for shrinkflation."** Three
structural advantages competitors cannot copy:

1. **Volume + freshness** — ~8,900 events, refreshed daily by the scrapers. Never
   run out of episodes; react to *today's* shrink within an hour (ISR). A solo
   creator posts when they happen to notice something; FullCarts posts when the
   data says.
2. **Proof, not vibes** — every claim has cited sources, archived images, and a
   public permalink. Each video is an ad for a page that *substantiates the
   claim*, which earns trust, backlinks, and press (news + Consumer Reports
   cross-refs are already tracked).
3. **The escalation graph** — product → brand pattern → corporate parent → macro
   CPI context. No competitor has all four layers wired together. This is the
   "and beyond" stats layer.

### The flywheel

video → "see full receipt at fullcarts.org/products/[id]" → site visit → user
submits a tip / spots a new one → feeds `raw_items` → becomes the next video.
The audience generates the content supply. "We documented YOUR find"
(`sources.author`) is the strongest community loop available — feature
commenters' catches.

---

## Making it repeatable (production pipeline)

Build a thin **content-pack generator**: given a `content_candidates` row, emit a
JSON spec (hook text + the 6 beats' data + asset URLs) and feed it into a
template-based video tool (Remotion / After Effects template, or an automated
faceless tool). Because every beat maps to named fields, one template + the
daily top-scored row = a video a day with near-zero manual work.

Suggested home: `pipeline/scripts/build_content_pack.py`, next to the existing
pipeline scripts.

### Content-pack JSON shape (proposed)

```json
{
  "event_id": "…",
  "entity_id": "…",
  "hook": { "template": "accusation", "text": "Did you notice Brand X shrank this 22%?" },
  "beats": {
    "reveal":  { "size_before": 19.3, "size_after": 16.5, "size_unit": "oz", "delta_pct": -14.5, "image_url": "…" },
    "receipt": { "author": "u/…", "domain": "reddit.com", "body_excerpt": "…", "date": "2026-05-30", "url": "…" },
    "pattern": { "brand": "…", "shrinkflation_events": 7, "worst_delta_pct": -22.0, "first_detected": "…", "last_detected": "…" },
    "boss":    { "manufacturer": "…", "total_shrinkflation_events": 134, "top_brands": [ { "brand": "…", "thumbnail": "…" } ] },
    "cta":     { "total_changes": 8947, "brands": 1167, "url": "https://fullcarts.org/products/…" }
  }
}
```

---

## Data asset → visual reference

Quick map of which queryable assets power which visuals.

| Visual | Backing asset | Key fields |
|---|---|---|
| Stat cards / counters | `dashboard_stats()`, `brand_rankings`, `category_stats` | `total_changes`, `shrinkflation_events`, `worst_shrink_pct` |
| Time-series macro chart | `shrinkflation_timeline`, `cpi_shrinkflation_context`, `google_trends_data`, `bls_shrinkflation` | monthly `events`, CPI MoM %, trends 0–100, BLS downsizing counts |
| Product galleries | `biggest_shrinks`, `recent_changes`, `content_candidates` | `size_delta_pct`, `image_url`, `content_score` |
| Brand scorecards | `brand_index` | `worst_delta_pct`, `shrinkflation_events`, `thumbnail`, `primary_category` |
| Evidence walls / receipts | `event_evidence_summary.sources[]` | `author`, `body_excerpt`, `domain`, `title`, `image`, `date` |
| Leaderboards | `brand_rankings`, `corporate_tree` | event counts, `top_brands` |
| Restoration stories | `published_changes` (change_type='restoration') | `size_before/after`, `observed_date` |
| Skimpflation nutrition | `skimpflation_events.nutrient_deltas` | `nutrient`, `before`, `after`, `delta_pct`, `bad_direction` |
| News / CR badges | `news_brand_mentions`, `consumer_reports_findings` | `news_mentions`, `source_url`, `excerpt` |
| Cost-of-air widget | `published_changes` basket aggregation | `size_delta_pct` across a basket |

---

## Recommended cadence

- **Daily:** 1× "Shrink of the Day" (flagship format).
- **Weekly:** 1× "Repeat Offenders" + 1× "Who Owns Your Cart?".
- **Monthly:** 1× "CPI vs Reality" long-form for YouTube.
- **Reactive:** post within the hour when a high-`content_score` event lands.

Always close with the permalink CTA to keep the site flywheel turning.
