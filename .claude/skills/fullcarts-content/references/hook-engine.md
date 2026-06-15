# The Hook Engine

A **deterministic template bank** that turns one brief row into a ranked set of gate-passing hook
candidates. It does not replace [`hooks.md`](hooks.md) — that file is the *law* (The Snap, the
Emotional Lock-In, clarity-before-contrast, the kill-list). This file is the *applied layer*: it
takes proven, field-tested viral **frames** and **binds their blanks to real database fields** so a
candidate event comes out the other side as a FullCarts hook, never a context-free tease.

**Where it runs:** Step 3 of the operator loop (`references/operator-loop.md`). For each brief pick,
run the engine → get ~10 candidates → keep the 2–3 that survive the hook checklist → pick one as the
spoken hook, bank the rest as caption hooks / A-B test variants for Agent Opus.

---

## 1. Why these frames, and the one rule that governs all of them

The 10 frames below are the proven "always-works" hook skeletons every short-form operator uses.
They are *generic on purpose* — which means **half of them are the exact anti-pattern `hooks.md`
forbids** until you fill the blank. `NOBODY TALKS ABOUT THIS` and `THIS WILL CHANGE HOW YOU SEE ___`
are vague open loops with nothing in the blank. The engine's entire value is the binding step.

> **The binding rule (non-negotiable):** every blank must be filled with a **concrete token from the
> brief row** — a named product, a number, a year, a parent company — *before* the frame is spoken.
> A frame that still reads as a context-free tease after binding is **killed**, not shipped. The
> filled hook must pass the `hooks.md` 2-question test (context clear? + curiosity induced?) and the
> 7-point checklist. The frame is the delivery; **the Snap is still the engine underneath.**

---

## 2. Slot variables (the tokens the engine binds)

Every token maps to a column the brief SQL already pulls (`operator-loop.md` Step 2) or to a peg/feel
chosen during the brief. **Only `{pct}`, `{size_*}`, `{unit}`, `{brand}`, `{product}`, `{year}` are
pre-cleared as approved-claims** (they trace to the DB). Every peg-derived token (`{parent}`,
`{commodity}`, `{profit}`, `{quote}`) is an **external fact** — trace it to a real source and show it
via `SourceFrame`; never assert from memory (see `content-angles.md` §5 gate).

| Token | Source | Example |
|---|---|---|
| `{brand}` | `published_changes.brand` | Cadbury |
| `{product}` | `published_changes.product_name` | Dairy Milk |
| `{pct}` | `round((1-(size_after/size_before))*100,1)` | 20% |
| `{size_before}` `{size_after}` `{unit}` | DB | 200 → 160 g |
| `{year}` | `observed_date` (the "same price as ___" anchor) | 2022 |
| `{category}` | `product_entities.category` | chocolate |
| `{parent}` | `corporate_tree` view (Peg C) | Mondelez |
| `{peg}` | chosen from `content-angles.md` §5 (A–J) | commodity / record-profits / calendar |
| `{feeling}` | chosen from `content-angles.md` §4 / `hooks.md` lock-in bank | "you're not bad with money" |

---

## 3. The frame bank — each proven frame, FullCarts-bound

For every frame: the **bound template** (clarity-first, you/your), the **Snap mapping** (which beat
each part plays), the **bucket** it serves, and the **kill caveat** (what makes this frame fail).

| # | Proven frame | FullCarts-bound template | Snap mapping | Bucket | Kill caveat |
|---|---|---|---|---|---|
| 1 | **IF YOU ARE ___ LISTEN CAREFULLY** | "If you buy `{product}`, check the package — you're paying `{year}` prices for `{pct}` less." | Context = "you buy it"; Lean = "same as always"; Snap = "`{pct}` is gone" | educational | "if you are…" with a vague audience ("a human", "alive") = killed. Bind to a **real buyer segment** tied to the product. |
| 2 | **IF I HAD TO START OVER** | "If I rebuilt my grocery list from scratch today, `{brand}` `{product}` is the first thing I'd drop — here's the receipt." | Context = "rebuild the list"; Lean = "keep the staples"; Snap = "drop this one, `{pct}` gone" | personal | Personal-bucket only (face required). Must end on a **DB receipt**, or it's a generic guru take. |
| 3 | **THIS IS THE REAL REASON YOU'RE STILL ___** | "The real reason your `{category}` budget keeps creeping isn't inflation — it's `{brand}` taking `{pct}` and keeping the price." | Context = "budget creeps"; Lean = "blame inflation"; Snap = "no — it's the `{pct}` cut" | educational | The blank must be a **real felt state** (over budget, broke at checkout). "still poor" = lazy; bind to the rip-off painpoint. |
| 4 | **AVOID THIS MISTAKE WHEN ___** | "Avoid this mistake next time you buy `{product}`: comparing price, not price-per-`{unit}` — that's how `{brand}` hid a `{pct}` cut." | Context = "you shop for it"; Lean = "compare the sticker"; Snap = "the unit price moved, you didn't see it" | educational | The "mistake" must be a **real shopper behavior**, and the fix must be the thing our data exposes. |
| 5 | **HERE'S THE TRUTH ABOUT ___** | "Here's the truth about `{brand}` `{product}`: same price as `{year}`, `{pct}` less in the pack." | Context = "you know this product"; Lean = "price is the truth"; Snap = "the truth is the `{pct}`" | reveal | "the truth about [vague]" = killed. The truth must be a **specific number**, stated in the hook. |
| 6 | **THIS IS WHY YOU'RE STILL ___** | "This is why your cart costs more even when you buy less: `{brand}` shrank `{product}` `{pct}` and held the price." | Context = "cart costs more"; Lean = "you're buying more"; Snap = "no — you're getting `{pct}` less" | educational | Same blank-rule as #3 — bind to a felt money state, not an abstraction. |
| 7 | **MOST PEOPLE DON'T REALIZE** | "Most people don't weigh their groceries — so most people never caught `{brand}` pulling `{pct}` out of `{product}`." | Context = "nobody weighs food"; Lean = "why would you"; Snap = "that's the cover for the `{pct}` cut" | educational | "most people don't realize [obvious thing]" = killed. The unrealized thing must be the **hidden mechanism**, not the headline. |
| 8 | **I LEARNED THIS TOO LATE** | "I caught `{brand}` `{product}` at `{pct}` smaller too late — I'd already bought it for `{year}`-money for months. You don't have to." | Context = "I bought it for years"; Lean = "normal staple"; Snap = "it was `{pct}` smaller the whole time" | personal | Personal-bucket only. The "too late" must be **our own logged miss**, then flip to "you/your" (don't strand it in "I"). |
| 9 | **THIS WILL CHANGE HOW YOU SEE ___** | "This will change how you see your `{category}` shelf: `{parent}` owns half of it and shrank `{product}` `{pct}` — you weren't even choosing." | Context = "you pick a brand"; Lean = "you have options"; Snap = "one parent shrank the aisle" | educational | Pairs with **Peg C (`corporate_tree`)**. Without the parent-company token it collapses to a vague tease — killed. |
| 10 | **NOBODY TALKS ABOUT THIS** | "Nobody talks about the second grocery price hike: `{brand}` left the price on `{product}` alone and took `{pct}` out of the box." | Context = "prices went up"; Lean = "that's the whole story"; Snap = "there's a second hike — the `{pct}`" | reveal | The single highest-risk frame. **Only ships with a number in the first sentence.** "nobody talks about this" alone is the textbook kill. |

---

## 4. Selection matrix — which frames fit which event

Don't run all 10 blind. The event's *signature* and its *peg* pre-select the strong frames.

| Event signature (from brief row) | Lead frames | Why |
|---|---|---|
| High `{pct}` (≥18%), image-backed, recent | 5, 10, 1 | the number carries the hook; reveal frames hit hardest |
| Peg C — parent owns the category (`corporate_tree`) | 9, 7 | the "illusion of choice" payoff needs the parent token |
| Peg A/B — commodity fell / record profit | 3, 6, 10 | "real reason / second hike" reframes the macro excuse |
| Peg F — seasonal/calendar | 1, 5 | concrete buyer segment + plain truth, lowest gate risk |
| Peg H — restoration ("almost never comes back") | 8, 2 | the "too late / start over" regret frames carry the accountability kicker |
| Personal slot (face, narrative meta) | 2, 8 | the only two frames that license first-person — flip to you/your by the end |
| Quiet week / evergreen reveal | 5, 4 | plain-truth + practical-fix frames never miss |

---

## 5. The generation procedure (run per brief pick)

```
1. PULL the brief row → fill the slot tokens (§2). Confirm {pct}/{size_*}/{year} trace to the DB.
2. PEG it → which of content-angles §5 A–J does this event hit? (≥2 = higher rank.) Bind {parent}/
   {commodity}/{profit}/{quote} only if a real source exists; else those frames are unavailable.
3. PICK the lead frames from the §4 matrix (signature × peg). Usually 3–4 frames, not 10.
4. BIND each chosen frame's blanks with the tokens — no blank left generic.
5. SNAP-CHECK each: does it carry context → lean → snap? If it's a flat stat, rewrite to the reversal.
6. GATE each against the hooks.md 7-point checklist. KILL any that stay vague after binding (§3 caveat).
7. RANK survivors: (a) clarity in ≤8 words, (b) contrast size, (c) peg count. Top one = spoken hook.
8. BANK the rest → caption hooks + Agent Opus A/B hook-test variants (faceless B-side, AI-labeled).
```

The output of the engine is **not one hook** — it's a spoken hook + a small bank of tested variants,
so the same event can run a hook A/B test across platforms without re-ideating.

---

## 6. Worked example — one event → the full frame bank

Event (canonical, already approved in `hooks.md`): **Cadbury Dairy Milk**, ~**20%** smaller, same
price as **~2022**, category **chocolate**, parent **Mondelez** (Peg C available), feeling = *"you're
not imagining it."* Tokens: `{brand}`=Cadbury `{product}`=Dairy Milk `{pct}`=20% `{year}`=2022
`{category}`=chocolate `{parent}`=Mondelez.

Matrix says: high-pct + Peg C → lead with **5, 10, 9**, then 1/7.

| # | Frame | Bound hook (spoken-ready) | Verdict |
|---|---|---|---|
| 5 | HERE'S THE TRUTH | "Here's the truth about Cadbury Dairy Milk — same price as 2022, a fifth of the bar is gone." | ✅ lead |
| 10 | NOBODY TALKS ABOUT | "Nobody talks about the second price hike: Cadbury left the price alone and took 20% out of the bar." | ✅ strong |
| 9 | CHANGE HOW YOU SEE | "This'll change how you see the chocolate aisle — Mondelez owns half of it and quietly shrank Dairy Milk 20%." | ✅ Peg C |
| 1 | IF YOU ARE… LISTEN | "If you buy Dairy Milk, check the bar — you're paying 2022 prices for 20% less chocolate." | ✅ |
| 7 | MOST PEOPLE DON'T | "Most people never weigh a chocolate bar — which is how Cadbury pulled 20% out of Dairy Milk unnoticed." | ✅ |
| 3 | REAL REASON YOU'RE STILL | "The real reason your chocolate costs more for less isn't cocoa — it's Cadbury keeping the price and cutting 20%." | ✅ (needs Peg A source for "isn't cocoa") |
| 8 | LEARNED TOO LATE | "I caught Dairy Milk 20% smaller too late — paid 2022-money for it for months. You don't have to." | ✅ personal-bucket |
| 2 | IF I HAD TO START OVER | "If I rebuilt my grocery list today, Dairy Milk's the first cut — 20% gone, same price. Here's the receipt." | ✅ personal-bucket |
| 6 | WHY YOU'RE STILL | "This is why your cart costs more for less — Cadbury shrank Dairy Milk 20% and held the price." | ⚠ near-dup of #3, bank as variant |
| 4 | AVOID THIS MISTAKE | "Avoid this mistake buying chocolate: comparing price, not price-per-gram — that's how Cadbury hid a 20% cut." | ✅ |

Spoken pick: **#5** (clarity in 8 words, the number is the snap). Banked variants: #10, #9, #1 for
captions + the Agent Opus hook A/B test. #6 dropped as a duplicate of #3.

---

## 7. Integration points

- **`hooks.md`** stays canonical theory. This file is referenced from there as the applied frame bank.
- **`operator-loop.md` Step 3** calls the engine per pick; the §5 procedure is the sub-routine.
- **`gates.md`** is unchanged — the engine *feeds* the gates; the `interesting` gate still has final say.
- **Agent Opus B-side** consumes the banked variants as the hook-A/B test set (AI-labeled, faceless).
