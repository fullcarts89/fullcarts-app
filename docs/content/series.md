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
- ~~**Caught: Gatorade** — 32→28oz (−12.5%); the small bottles got it worse.~~ **❌ DO NOT USE / DO NOT RECOMMEND.** Founder's standing call: Gatorade shrinkflation is overdone across the genre — it does nothing for reach. Removed from the queue. Don't resurface it in briefs, batches, or the operator's convergence picks. (See `content-rules.md` → "Do-not-use brands.")

**Bingeability mechanics to layer in:**
- End-screen tease: "Tomorrow — Caught: [next brand], and it's worse." (forces the next view)
- Pin a playlist / "Caught" highlight so a new viewer can binge the backlog.
- Consistent thumbnail/cold-open framing so the backlog reads as one body of work.

---

## WEEKLY REPEATABLE FORMATS (the locked slot templates)

These are the **video formats** behind the weekly schedule (`posting-schedule.md`). The beats are
**fixed**; only the `[bracketed variables]` change week to week — that's what keeps prep light and
the series recognizable. "Caught:" (above) is the Wed hero. The four below fill the other slots.

> **Two rules across ALL series:** (1) the **Convergence Peg Library** (`content-angles.md` §5) is the
> idea engine for every slot — any peg, any length; (2) **every video carries a POV/"so-what" beat**
> (`content-angles.md` §6) — factual on the data, opinionated on the behavior. In *Caught:* that's the
> payoff/kicker; in *Shrink Check* the closing line; in *The Take* it's the whole point.

### ⚡ "Shrink Check" — Mon, short single-product spotlight (≤25s, **rotates 4 treatments**)
> The fast counterpart to the Wed hero: **always one product, always short, but a different *treatment*
> each week** so it never reads as a mini-*Caught:*. Where Wednesday tells the full story (brand on
> trial + macro peg + the trick), Monday does one quick *job* — play, teach, or gut-punch. Rotate the
> four below; every DB entry is fuel, so supply is infinite. *(Name is a placeholder — rename freely.)*

**1) Guess the Cut** — the game (curiosity gap drives comments/duets)
```
BEFORE (0–5s):  hold product — "This was [before size]. Guess how much they cut it."
GUESS  (5–10s): "Comment your guess. I lowballed it."
REVEAL (10–20s): drop −[X]% overlay — "[after size]. Same price." → "Did you get it?"
```
**2) Do the Math** — the skill (the channel's useful-tool identity) · ★ **family-of-4 annual angle**
> Don't just show one cut — **show the yearly damage.** Take a commonly-bought staple (or a basket of
> them) that shrank, and compute what a **family of four overpays per year** because the box got smaller
> at the same price. Concrete, shareable, rage-inducing in the best way.
```
SETUP  (0–6s):  "Your [product] shrank [X]%. Doesn't sound like much — watch this."
MATH   (6–18s): per-unit price × a family-of-4's real annual usage → "$[N] a year, gone, on ONE item."
STACK  (18–25s): "Now multiply that across your whole cart." → CTA
```
> ⚠️ **Gate:** the math must be **defensible arithmetic** — real shelf prices, a stated, reasonable
> family-of-4 consumption assumption shown on screen, and per-unit (not vibes). Cite the size cut to the
> DB; show the price source. If an assumption is rough, say so. Never inflate the annual number.

**3) Then vs Now** — the nostalgia gut-punch (feeling-first, trending-audio friendly)
```
NOW   (0–6s):  "This is [product] today."
THEN  (6–15s): "This is what it used to be." → before/after overlay + −[X]%  — let it land, minimal words
```
**4) Same Price, Less Stuff** — the pure stat-drop (fastest, snackable)
```
SNAP (0–12s): product → "[before] → [after], −[X]%, same price." → "It's in the database. Free."
```

### 🎙️ "The Take" — Thu, ~30–45s (the opinion/commentary slot — the moat)
> **Information is cheap; the take is the moat** (`content-angles.md` §6). A **peg** (`content-angles.md`
> §5) is the springboard, but this piece is your *perspective* — the rant, the prediction, the call —
> not just the receipt. It runs a touch longer than the other shorts because **opinion needs room to
> breathe.** The data still anchors it (always show the receipt), but the *job* is your read on what it
> means. *(Pegs fuel every slot now, in any length — this is just the slot where opinion leads.)*
```
HOOK   (0–5s):   the take, stated flat — "The 'New Look!' sticker is the biggest tell in the store."
RECEIPT(5–18s):  the data that earns the take — a real DB entry / source screenshot (anchor it)
TAKE   (18–38s): your perspective — why it matters, who they're betting on, what you'd do
CTA    (38–45s): "Agree? 👇 Follow for the take they won't give you. fullcarts.org"
```
**Rotates through opinion-first angles** (§6): the **Take/rant** · **Predictions** ("who shrinks next, and
why") · **The Defense / The Call** ("this one's actually fine" / "this is the worst kind") · the **§2
contrarian comebacks** (esp. visible-vs-hidden). On a **CPI print week**, the macro read becomes the
take ("groceries 'only' rose X% — here's what that number hides," over a real FRED screenshot).
> ⚠️ **Guardrail (§6):** factual on the numbers, opinionated on the *behavior* — corporate tactics +
> consumer advocacy ("it's not you"). **Never** partisan politics or monetary-policy lectures.

### 🧾 "Receipt of the Week" — Fri, 15–30s (with an evidence-tag review as the built-in fallback)
> The reliable replacement for the old reactive-only *Breaking Shrink* slot. **Lead with the freshest
> noteworthy entry added to the DB that week** — "here's the one that just landed." If the week's new
> shrinks are unremarkable, **fall back to an evidence-tag review** (so Friday always has fuel and never
> rests). Recency-driven, visually proof-rich (tagged claims are image-backed and admin-reviewed), and
> independent of outside news.
```
RECEIPT (0–6s):  "This week's receipt:" — the freshest/most notable new entry → before/after + −[X]%
WHY     (6–18s): one line on what makes it notable (magnitude, brand, or the trick) + the source
CTA     (18–28s): "New receipts every week. Search it free at fullcarts.org."
```
**Fallback — Evidence-Tag Review** (run when no single shrink is noteworthy enough): pull the freshest
claims under **one rotating tag** and rundown them (`RundownChip` ×N) with the real tagged photos. The
tags (live counts; re-pull each batch): **So Smol** (218, extreme cuts) · **Spot the Difference** (150,
before/after) · **Slack Fill** (185, air) · **Skimpflation** (128, recipe) · **Paper Thin** (49) ·
**Stretchflation** (11, price up same size). Source: `claims.evidence_tags`, `status='evidence'` only.
```
THEME  (0–5s):  "This week in [So Smol / Slack Fill / …]:" — name the tag + what it means
RUNDOWN (5–22s): 3–4 fresh tagged finds, photo + −[X]% each
CTA    (22–28s): "Caught one in the wild? Tag me. fullcarts.org"
```
> **Genuine breaking news still wins:** if a real story hits a brand we cover, it can **preempt any
> day's slot** with the "we documented this [N] months before the headline" receipt — it's now a
> floating wildcard, not a scheduled slot that sits empty.

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
- **Music:** the operator also assigns a **music lane** per slot/series from `music-beds.md` (royalty-free
  bed for the cross-posted master; trending sound is a native per-platform discovery add-on only).
