# FullCarts Posting Schedule & Carousel System

**Date:** June 12, 2026
**Parent:** `docs/plans/2026-06-10-face-forward-content-strategy.md` (this expands its schedule section).
**Purpose:** the standing weekly operating plan — what to post, when, and how most of it gets made
**without filming**, plus the carousel/story template system that auto-generates from fullcarts.org data.

---

## The model: 1 film day + auto-generated data content + light daily posting
The unlock is that **most of the week is data, and the data is already in the database** — so it
doesn't need a camera. Two streams:

**① Film day (one dedicated day, ~2–3 hrs)** — batch-film all talking-head content in one sitting:
the hero *Caught:* episode **plus** 2–3 short clips (the 30s reveal, a hot-take, the vlog). One setup,
many clips. Then the SRT-synced loop (`production-playbook.md`) turns them into finished videos.

**② Operator auto-generates the rest from the DB — zero filming:** the carousels and story slides are
rendered from live data (the `Carousel` / `TierList` Remotion templates), drafts the hero script +
short-reel scripts, and hands over a dated **"week-of" post queue**.

**③ You, daily (~15 min):** post the next queued item, add captions in-app for the videos, fire a
story, engage.

---

## The weekly schedule (TikTok-led, cross-post Reels; IG for carousels/stories)

| Day | Format | FullCarts content | Pillar | Effort |
|---|---|---|---|---|
| **Mon** | 30s reel | A *Caught:* reveal — one product, the Snap + a quick overlay | Reveal | Medium |
| **Tue** | Carousel + Q&A stories | Data carousel (5 Stealth Shrinks / Before-After); stories: "comment a product, I'll check the DB" | Data + Engagement | Low-Med |
| **Wed** | 1-min **signature series** | **THE flagship *Caught:* episode** (full SRT-synced composite) | Series anchor | **Hero** |
| **Thu** | 7–15s reel + polls | Quick hot-take/newsjack; polls ("did your box shrink? Y/N") | Newsjack | Low |
| **Fri** | Break / short | Rest, or a reactive newsjack if news breaks | Newsjack | Low/None |
| **Sat** | Carousel | Tier List / Worst Offenders / By the Numbers | Rankings | Low-Med |
| **Sun** | 1-min vlog-style | The **persona**: "tired dad" BTS, "how I verify a claim," why I built it | Personal | Medium |

Only **Wed is a hero**; Mon/Sun are medium (mostly talk-to-camera); Tue/Thu/Sat/Fri + stories are light.
Maps to the content mix (educational / newsjack / personal / entertainment) and every pillar gets a slot.

### Effort tiers
- **Hero** (~2–3 hrs): the Wed *Caught:* — full pipeline (film + SRT + composite).
- **Medium**: Mon reveal, Sun vlog — talk-to-camera, minimal/no graphics.
- **Light** (auto/instant): carousels (operator-rendered from DB), hot-takes (talk + in-app captions), stories (native).

### Phased ramp (don't start at 7 days)
- **Phase 1 (sustainable):** Wed hero + Mon reveal + Sun vlog + one carousel (Tue *or* Sat) + stories when you can.
- **Phase 2 (daily):** add Thu hot-takes, the 2nd carousel, daily stories, trial reels for hook-testing.

### Stories (the low-effort glue, IG-led)
2–5×/week to start: polls ("noticed your cereal shrink?"), "is X shrinking?" Q&A from the DB, reshares,
"how I verify a claim" BTS, reaction to a news/CPI drop. (Optional IG "story reset" = skip a day.)

---

## The carousel/story template system (auto-generated from fullcarts.org)

Branded, data-driven Remotion compositions; the operator queries the DB → renders slides (PNG) → queue.

### Templates built (`video/src/compositions/`)
- **`Carousel`** (4:5, 1080×1350) — multi-slide: cover → ranked product slides (before/after bars, −X%,
  optional product image + brand logo) → CTA with the persona line. First set: **"5 Stealth Shrinks."**
  One slide per frame: render stills `0..N+1`.
- **`TierList`** (4:5) — **swipe-reveal**: cover → tiers **bottom-up D…S** (one per swipe, progress dots +
  "it gets worse → swipe") → **the full list as the payoff LAST slide.** Brand pills with logo/monogram icons.

### The "slice and dice" variant menu (all from the same engine — query + render)
- **5 Stealth Shrinks** (top magnitude) · **Worst Offenders** ranking · **Before/After [Brand]**
- **Shrinkflation Tier List** (worst brands graded S–D) · **US-only** versions of any
- **Worst shrinkflation this month** (filter `observed_date`) · **Beverages / [category] with the worst shrinks**
- **Biggest shrinks vs. CPI** ("official inflation says +X%… reality:") · **By the Numbers** (one stat)
- **Restoration / good news** (the rare ones that came back)

### The swipe-through principle (engineer the swipe — applies to EVERY carousel)
- **Cover** = a hook + "swipe →" (a question, a withheld payoff).
- **Middle** = reveal/withhold — countdown to the worst, or one tier per slide (build tension).
- **Last** = the payoff — the full list / the #1 worst / the screenshot-able recap.
The TierList does this (D→S→full list); the 5-Things counts down 5→1 to the worst.

### Images & logos
- **Product images** — `product_entities.image_url` (clean `.webp`s) → the product photo on the slide.
- **Brand logos** — pass a `logo` per brand (a curated transparent PNG in `video/public/logos/<brand>.png`,
  recommended, or `logo.clearbit.com/<domain>`). **Monogram fallback** (brand initial) renders when absent —
  a slide never breaks. *(DB `brand_index.thumbnail` is a product photo, not a logo — don't use it for icons.)*
- ⚠️ **Sandbox can't fetch image/logo hosts (403)** — product photos + logos render on a **network-open
  machine** (your laptop / the operator). In-sandbox previews show bars / monograms.

### Story templates (planned — same approach)
Single branded slides: poll ("did your [product] get smaller? 👆/👇"), "is [X] shrinking?" (before/after from
DB), a quick stat, "search any product → fullcarts.org," "how I verify a claim" BTS.

---

## Repeatable Series (Carousels)

The "slice and dice" menu above covers the **ranked/data** formats (5 Stealth Shrinks, Worst Offenders,
Before/After [Brand], Tier List, Biggest-shrinks-vs-CPI, By the Numbers) — all the *same engine* (query +
render). The formats below are **net-new** and extend that menu with distinct *swipe mechanics*, not just new
filters. Each runs on infinite DB fuel and clears the three gates.

### 1. Guess the Cut (gamified — the quiz) ⭐
- **Mechanic:** a per-product **Q→A open loop** — one slide shows the *before* size and asks "how much did
  they cut?"; the **next** slide reveals the −%. The answer is never on the same slide, so the curiosity
  *forces* the swipe.
- **Structure:** cover (challenge) → Q/A pairs climbing to the worst → CTA ("you lowballed it too, didn't you?").
- **Data:** high-magnitude, well-evidenced rows (`evidence_count ≥ ~15`), ordered **ascending** so the biggest
  cut lands last (e.g. … → Sainsbury's Scottish Oats 1000→500 g, −50%).
- **Gate watch-out:** every tangible equivalence must be **arithmetic, not embellishment** — 32→28 fl oz is
  "half a cup," NOT "a full glass"; keep the lineup **category-coherent** or drop the cross-product analogy.
- **Cover:** "Same price. Less inside. Guess how much each one shrank — I lowballed every one. swipe →"
- **Cadence:** weekly. **Build:** new `GuessTheCut` composition (hidden-after → reveal layout).

### 2. It's Not You (emotional cold open)
- **Mechanic:** open on the **feeling**, not a number (Emotional Lock-In — `content-angles.md` §4) → name the
  unspoken thought → receipts → the "it's not you" resolution. Swipe driver = emotional cliffhanger.
- **Structure:** "You're not crazy — that box really did get smaller." → "you swore it was bigger, then felt
  silly for noticing." → 3 documented receipts → "You're being quietly robbed, and they built it so you'd
  blame yourself." → persona CTA.
- **Data:** any well-evidenced reveal(s) paired with a §4 feeling. **Cadence:** as fits. **Build:** new
  `ItsNotYou` composition (mostly type).

### 3. Tier List — rotate the axis (this is what keeps it repeatable)
The `TierList` template already ships; its **repeatability is the axis you slice on**, so it's never the same
brands twice:
- **By category (default):** chocolate, soda, cereal, chips, coffee, toothpaste, ice cream… (15+ clean buckets
  in `brand_index.primary_category` — **normalize case** in the query; `snacks`/`Snacks` and `dairy`/`Dairies`
  are currently split).
- **By season (convergence overlay):** Halloween candy · back-to-school lunchbox · Super Bowl snacks · holiday
  tins — run *over* the category default when the calendar lines up.
- **By parent company:** "every brand Mondelez owns, ranked" (ties to `corporate_tree`).

### 4. They Did It Again — the staircase *(benched)*
- **Mechanic:** one product, its cuts **stacked across the years** — each swipe is another year ("…and again"),
  ending on the **cumulative** loss. Timeline tension.
- **⚠️ Benched until deduped:** `published_changes` re-records the *same* change at multiple dates (Gatorade
  shows "12.5%" ×8 — one cut re-scraped, **not** a staircase). Needs a per-product pass to confirm a **clean
  monotonic size sequence** (100→90→80→75) before it can render honestly. Candidates worth the pass: Crest,
  Pringles, Cadbury Dairy Milk.

---

## Brand-safety note
Showing brand names/logos to identify the products you're *factually documenting* is standard
editorial / nominative use in this genre. Keep the framing factual (the data does the indicting),
cite sources, no fabricated visuals — same as the video evidence policy.

## Next builds (open)
1. Curated **logo set** (`public/logos/`) + brand→logo map so tier lists ship with real logos.
2. **Shrinks-vs-CPI** carousel · **US-brands tier list** · **Story templates**.
3. **Wire the carousel/story generation into the `fullcarts-content` operator** → one-command weekly drop
   (query DB → render carousels + stories + hero script → dated post-queue folder).
