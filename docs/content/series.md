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
