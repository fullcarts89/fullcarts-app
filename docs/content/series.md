# FullCarts Series Strategy — Bingeability Engine

**Date:** June 11, 2026
**Parent:** `docs/plans/2026-06-10-face-forward-content-strategy.md`
**Why this exists:** the missing growth flywheel. Standalone posts don't compound; a **series**
creates connective tissue so one view becomes many in a session — and bingeing is what converts
to a follow. (Rule of thumb from creators who've done it: ~4–5 of your videos watched back-to-back
= ~10× more likely to follow. Your job is to get them to that 4–5 before they bounce.)

We run a **soft series** (consistent theme/format/cold-open, not a daily-numbered "hard" series)
because we post **3–5×/week, not daily** — a hard daily series is the #1 burnout trap and we have a
day job. Soft series gets the bingeability without the treadmill.

---

## PRIMARY SERIES — "Caught:" (the platform builder)

The channel's spine. Every episode is one brand caught shrinking a product, documented and sourced.

**The fixed cold-open (connective tissue — never changes):**
> "Caught: **[Brand]**." *(said to camera, on-screen `CAUGHT: [BRAND]` in the alert-red brand style)*

That identical open is what makes a stranger who lands on episode #37 recognize it as part of a
series and binge backward. It also bakes in **cult-hopping** — opening on a famous brand/logo gives
instant relatability (the brain relaxes when it sees something it knows), which we get **for free**
because every episode features a recognizable brand.

**Episode structure (30–60s — house template + Snap hook + Emotional Lock-In):**
```
COLD-OPEN (0–1s):  "Caught: [Brand]."                          → on-screen CAUGHT: [BRAND]
HOOK (1–4s):       The Snap — context → lean → reversal         → see hooks.md
LOCK-IN (4–10s):   name the unspoken truth (they feel SEEN)     → content-angles.md §4
PROOF (10–20s):    real before/after image + FullCarts entry; resolves → ShrinkOverlay (before→after)
                   the lock-in: "it's not you — here's the receipt"
TRICK (20–40s):    how they hid it + (1-in-5) day-job signature → data-viz overlay
PAYOFF (40–52s):   the kicker (price-per-unit gut-punch)
CTA (52–57s):      "Follow — I catch the next one. fullcarts.org"
```

**Worked example — "Caught: Cadbury"** (with the lock-in beat):
```
COLD-OPEN: "Caught: Cadbury."
HOOK:      "Same egg, same price as two years ago — except a fifth of the chocolate is gone."
LOCK-IN:   "And if you grabbed it for your kid and thought 'huh, this feels small' — then felt a
           little silly for noticing — you're not imagining it, and you're not being cheap."
PROOF:     "Freddo Faces went 122 grams to 99 — that's 18.9%, documented, sourced." [ShrinkOverlay]
TRICK:     "Same mold, same wrapper, less inside — the cut you can't see on the shelf."
PAYOFF:    "You didn't get worse at noticing. They got better at hiding it."
CTA:       "Follow — I catch the next one. Search Cadbury at fullcarts.org. 🍫"
```

**Worked example — "Caught: Folgers" (★ recommended channel DEBUT)** — big, US-iconic, emotionally
charged, *under*-covered as shrinkflation, and the strongest story. (Cadbury is the strongest
*newsjack*, not the strongest debut — open with coffee, save Cadbury for its next news spike.)
```
COLD-OPEN: "Caught: Folgers."
HOOK/SNAP: "They shrank your coffee and blamed record prices. Coffee's since crashed almost 40% —
            and your can never came back."
LOCK-IN:   "If you've caught yourself rationing scoops to stretch the can to payday — and felt a
            little pathetic about it — that's not you being cheap. That's them."
PROOF:     "Folgers' big can went 51oz to 43.5 — 14.7% less. And here's coffee's real price:
            record high early 2025, 19-month low now." [ShrinkOverlay folgers + SourceFrame on a REAL chart]
TRICK:     "Price-per-pot quietly jumped while the shelf price barely moved. Economists call it
            'rockets and feathers' — prices rocket up on bad news, feather down on good. Coffee
            feathered down. Your can didn't move at all." [day-job signature]
PAYOFF:    "The costs left. The shrink stayed. You got a permanent raise — for them."
CTA:       "Follow — I catch the next one. Check your coffee at fullcarts.org. ☕"
```
*Coffee price verified Jun 2026: ~$4.40/lb peak (early 2025) → ~$2.70/lb (~−39%). Always read the
exact figures off your own real chart screenshot (`coffee-chart.json` → SourceFrame). Never an AI chart.*

**Worked example — "Caught: Gatorade"**
```
COLD-OPEN: "Caught: Gatorade."
HOOK/SNAP: "Same bottle shape, same price as a couple years ago — but there's a full glass of
            Gatorade missing."
LOCK-IN:   "If you've grabbed one after a workout, told yourself you were just thirstier than
            usual, then wondered if it shrank — you're not imagining it."
PROOF:     "32oz down to 28 — 12.5%, documented. The small bottles got it worse: 20oz to 16.9."
            [ShrinkOverlay gatorade]
TRICK:     "Same silhouette, less liquid — your eye says 'same bottle,' the label says otherwise."
PAYOFF:    "You didn't get thirstier. The bottle got smaller — old price, every single time."
CTA:       "Follow — I catch the next one. Search Gatorade at fullcarts.org."
```

**Flagship pilot episodes (already in the data):**
- **Caught: Cadbury** — Freddo 122→99g (−18.9%); Cadbury is also our #1 news brand (convergence).
- **Caught: Folgers** — the coffee "rockets & feathers": 51→43.5oz, prices later crashed ~40%, the can never came back. *(Confirm the coffee % off a real chart — `SourceFrame` over a real ICE/FRED screenshot, never an AI chart.)*
- **Caught: Gatorade** — 32→28oz (−12.5%); the small bottles got it worse.

**Bingeability mechanics to layer in:**
- End-screen tease: "Tomorrow — Caught: [next brand], and it's worse." (forces the next view)
- Pin a playlist / "Caught" highlight so a new viewer can binge the backlog.
- Consistent thumbnail/cold-open framing so the backlog reads as one body of work.

---

## WEEKLY REPEATABLE FORMATS (the locked slot templates)

These are the **video formats** behind the weekly schedule (`posting-schedule.md`). The beats are
**fixed**; only the `[bracketed variables]` change week to week — that's what keeps prep light and
the series recognizable. "Caught:" (above) is the Wed hero. The four below fill the other slots.

### ⚡ "Caught Slipping" — Mon, 30s reveal
> Quick dopamine reveal · 25–35s · one take, one overlay. Every DB entry is a candidate → infinite supply.
```
BAIT  (0–4s):   hold product, casual — "This is [Product]. Looks totally normal, right?"
LEAN  (4–10s):  "Except [N] years ago it was [before]. Now it's [after]."
SNAP  (10–22s): drop −[X]% overlay + per-oz price — "Same price. More money for less."
TAG   (22–30s): "It's in the database. Free. Link in bio."
```

### 🔄 "Rotating Peg Short" — Thu, 7–15s + poll  (*Inflation Receipt* on print weeks)
> **Thursday rotates a different peg every week** (`content-angles.md` §5) so the slot never fatigues —
> one week a parent-company convergence, the next a CEO-quote, then record-profits, skimpflation,
> tariffs, etc. Pick the freshest/highest-convergence peg that week and cut it to 7–15s. **A weekly CPI
> receipt gets old fast** (the headline is only "breaking" on print day), so **reserve the *Inflation
> Receipt* format below for the actual CPI print week** — or for a deliberate "this is in the news right
> now" episode. The pegs are simply more interesting than a monthly index, so they carry the other weeks.

#### The *Inflation Receipt* (CPI-print-week variant)
> The signature "official inflation vs. the hidden cut" beat · 7–15s. **Run it the week the BLS CPI
> print lands** (freshest newsjack punch). One print is a *basket* of category indexes; if you want a
> second CPI-flavored week, pick a different food-at-home category. Pulls the same category data as
> **Carousel Series #3 ("Official Inflation vs. Reality")** — one query, two formats.
```
HEADLINE (0–4s):  "CPI says [category] is up [X]% this year."
COUNTER  (4–12s): "Here's what they don't count: [Product] lost [Y]% of its size. Same shelf price."
POLL     (sticker): "Did your [category] shrink too? 👆 yes / 👇 no."
```
**CPI category rotation (for whichever weeks you choose to run an Inflation Receipt — CPI food-at-home has 6 groups):**

| Thu | Angle | Pairing |
|---|---|---|
| **Wk 1** (release week) | **the headline** | topline "food is up [X]% overall" — freshest newsjack punch |
| **Wk 2** | **cereals & bakery** | official +[X]% **+** the hidden shrink on top |
| **Wk 3** | **dairy & related** | official +[X]% **+** the box that also got smaller |
| **Wk 4** | **meats/eggs** *or* **nonalcoholic beverages** | official +[X]% **+** the FullCarts receipt |

> *Honesty note:* the **newsjack punch is strongest Wk 1** (headline is fresh); later-week category
> receipts are evergreen but carry less "breaking" energy — **which is exactly why the Thursday slot
> now rotates pegs instead of running CPI every week.** Run the Inflation Receipt on the print week (and
> optionally one follow-up category week), and let the peg library fill the rest. Re-pull fresh numbers
> when the next print lands. Remaining groups (fruits & veg, "other food at home") are spares for a
> second CPI week or to swap by season.

### 🚨 "Breaking Shrink" — Fri (reactive ONLY — a trigger, not a calendar slot)
> Rides a live news moment to prove the database is *ahead* of the headlines · 15–40s. If nothing
> breaks, Friday rests (no forced post).
```
TRIGGER (0–5s):  "This just hit the news —" (name the event/brand)
RECEIPT (5–20s): "so I pulled our data." — what the DB already had on file
TAKE    (20–40s): the opinion + "we documented this [N] months before it made headlines."
```

### 👨 "Why I Built This" — Sun, 1-min vlog (the persona — trust, NOT data)
> The tired-dad credibility engine · 45–75s · talk-to-camera, minimal graphics. **Topic backlog of 52
> in `vlog-ideas.md`** (one year of Sundays). Format is locked even though each topic is unique:
```
HUMAN MOMENT (0–15s): an opinion / confession / slice-of-life — NO stat
MISSION      (15–45s): connect it to why this matters to a tired dad sick of getting ripped off
SOFT CTA     (45–60s): "that's why it's free." → fullcarts.org
```

---

## FUTURE SERIES (backlog — spin these up once "Caught:" is established)

Run these as recurring sub-threads or standalone series later. All infinite from the database.

### "How They Hid It" (educational sub-thread — start this one alongside Caught)
One **technique** per episode — teaches viewers to spot shrinkflation everywhere, which is pure
authority + very bingeable (a taxonomy people want to complete). Technique buckets:
- **Same box, less inside** (slack-fill / air)
- **Fewer per pack** (21 → 18 count)
- **Thinner / lighter** (sheets, bars)
- **Recipe skimflation** (cheaper ingredients, same size — ties to `skimpflation_events`)
- **The unit-price dodge** (price/oz quietly up while shelf price flat)

### "Shrinkflation Report Card" (shareable ratings series)
Grade a brand or product **A–F**. Rating archetype = highly shareable ("what grade did YOUR brand
get?"). Backed by the `brand_index` leaderboard. Rubric: magnitude × frequency × repeat-offender ×
whether they raised price too.

### "Same Price, Less Stuff" (simplest core reveal)
The before/after reveal as a named, no-frills series. Lowest concept, easiest to sustain — a good
fallback/filler that still stays on-brand. Least differentiated, so secondary to the above.

---

## One-off nuggets (not series, but high-impact standalone posts)
- **"Only 23 of 2,200+ ever came back."** Restorations are ~1% (23 / 2,228). Don't build a series on
  it — but it's a killer standalone stat about how permanent shrinkflation is.

---

## How series ties into the rest of the system
- **Hooks:** every episode hook uses **The Snap** (`hooks.md`).
- **Overlays:** `ShrinkOverlay` / `StatCard` / `RundownChip` / `SourceFrame` from the `video/` toolkit.
- **Gates:** the three gates still apply to every episode (rules / claims / evidence).
- **Operator:** the `fullcarts-content` skill assigns each weekly pick to a series and keeps the
  cold-open + structure consistent.
