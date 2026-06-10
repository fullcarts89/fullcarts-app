# FullCarts Production Playbook — Stack + Repeatable Workflow

**Date:** June 10, 2026
**Parent strategy:** `docs/plans/2026-06-10-face-forward-content-strategy.md`
**Goal:** Produce 3–5 face-forward, rules-compliant clips/week in **4–6 hrs**, from one batch film day, without burning out. This is the operational layer — the "how," step by step.

You have no content-creation experience, so this is written as a literal procedure. Follow the loop; the quality is engineered into the steps.

---

## The core principle: separate the moat from the labor

Two layers, two very different treatments:

- **The moat (do once, reuse forever):** your face, your real product footage, your data visualizations, your FullCarts screen-records. These are what nobody can copy. Build a reusable kit so each one costs minutes, not hours.
- **The labor (automate ruthlessly):** captioning, silence-trimming, b-roll cutaways, scheduling, scripting first drafts. Hand all of it to AI tools.

The whole stack below is just this principle applied tool by tool.

---

## Recommended stack (mapped to the tools you already have)

| Stage | Tool | Role | Notes |
|---|---|---|---|
| **Ideation** | **Claude / Agent Opus** | Run the brief generator; rank ideas; pull data from the FullCarts DB (Supabase) | Ideation only — never writes the finished post. The convergence detector + 5-rule scorer. |
| **Scripting** | **Claude / Agent Opus** | Draft the full hybrid script (hook→proof→context→payoff→CTA), captions, hashtags per platform | You edit to your voice. Claude proposes; you approve. |
| **Filming** | **Your phone** | Film the hook (face) + hands-on real product + real scale reading | The Bucket-1 real-evidence layer. Authentic > polished. |
| **Data viz** | **Remotion** (+ Agent Opus to generate the React) | On-brand data overlays: the −12.5%, "32oz → 28oz," the FullCarts step-chart, lower-thirds | The moat, custom and reusable. Build a template once; feed it data forever. |
| **Atmosphere b-roll** | **Higgsfield** | Bucket-2 connective shots ONLY — abstract intros, mood, metaphor | NEVER fake packaging/charts (Bucket 3). Toggle the AI label. Use `virality_predictor` to gut-check a cut. |
| **Assembly + captions** | **Captions App** | Rough cut, burn-in captions, silence removal, eye-contact, layer sound FX/music, batch edit | The finishing line. Where most of the labor disappears. |
| **AI voice** | **ElevenLabs** | Voiceover for *faceless evergreen / pure-data* clips only | Keep your REAL voice on authority + personal pieces. AI voice is for the SEO/data B-side. |
| **Scheduling** | Buffer (free) or native schedulers | Queue TikTok/Reels/Shorts; post X reactively | X newsjacking is posted live, not scheduled. |

**Subscription verdict:** this covers everything — no need to add Placid/JSON2Video from the old plan (those rendered fake stat-cards, which is exactly the Bucket-3 failure mode). If you want one *optional* add, **Opus Clip or Submagic** (~$9–23/mo) is the best "long explainer → many shorts" slicer and has punchy auto-captions; you can defer it until you're filming longer-form. **Teleprompter app** (free) is worth it day one — it kills retakes on the hook.

---

## The reusable asset kit (build this ONCE, week 0)

Spend one 60–90 min session before your first batch making "real" the fast path:

1. **Screen-record FullCarts pages** — the homepage counter, a `/brands/[name]` timeline, a `/products/[id]` step-chart, the running shrink total. Clean 1080×1920 captures you'll reuse across dozens of videos.
2. **Screenshot the real source charts** — FRED CPI, BLS shrinkflation series, ICE coffee. Grab fresh on data-drop days.
3. **Shoot a product b-roll bank** — boxes/cans/bags on a clean surface, a kitchen scale, your hands picking items up. 10–15 clips covers months.
4. **Build the Remotion template** (Agent Opus does the React) — one component that takes `{brand, oldSize, newSize, pctChange, unit, sourceUrl}` and renders the branded overlay (number, before→after bar, FullCarts watermark, source citation). This is the single highest-leverage build; after it, every data overlay is a one-line prop change.
5. **Set the look** — pull the FullCarts design system (dark graphite + Space Grotesk + JetBrains Mono + alert red, per `FULLCARTS_DESIGN_EXPORT.md`) into the Remotion template and your caption style so every clip is unmistakably yours.

---

## The weekly loop (4–6 hrs)

### ① Saturday — Brief (15–30 min)
- Run the content-brief generator (`pipeline/scripts/generate_content_briefs.py`, via Claude/Agent Opus) → ranked digest of ideas, each with data + why-now + source URLs + a 5-rule score.
- **Pick 3–5.** Favor a mix across the content buckets (≈2 educational, 1 newsjack, 1 reveal/entertainment, rotate in 1 personal).
- For a newsjack, check the BLS/CPI/USDA calendar — if a print lands this week, that's an automatic slot.

### ② Saturday — Scripts + assets (30–45 min)
- Claude/Agent Opus drafts each script in the repeatable template (hook→proof→context→payoff→CTA) with per-platform captions + hashtags. **You edit each to sound like you** — read it out loud; if you wouldn't say it at the store, change it.
- Run each script through the **pre-publish checklist** (`content-rules.md`). 5/5 or it doesn't make the shoot list.
- Agent Opus generates the **Remotion data-viz** for each (feed it the numbers from the brief). Render the overlays now so they're ready for edit.
- Pull the needed real assets from your kit (FullCarts screen-record, source chart). Grab any fresh product on camera you don't have.

### ③ Sunday — Batch film (60–90 min)
- One sitting, good light (window or ring light), phone on a stand, **teleprompter app** running your hooks.
- Film **all 3–5 hooks** back to back (face, to camera), then **all the hands-on-product / scale proof** shots. Batching like-with-like is the time saver.
- Don't aim for perfect — aim for real and energetic. Reshoot only the hook if the first 3 seconds are flat (that's the one beat worth a retake).

### ④ Sunday — Assemble + caption (60–90 min)
- In **Captions App**: drop each clip, auto-caption (burn them in), trim silences, fix eye contact, layer light sound design.
- Drop in the **Remotion overlay** *the moment you say the number* (≈0.2–0.5s before you say the subject — the brain reads visuals slightly ahead of audio). Pin it next to the product.
- Add a **Higgsfield** atmosphere shot only if a clip needs an intro/transition — labeled, Bucket-2 only. Optionally run the cut through Higgsfield `virality_predictor` for a hook gut-check.
- Final pass against the checklist: captions on, 9:16, cut every 2–4s, CTA present, no Bucket-3 AI.

### ⑤ Sunday — Schedule (15–20 min)
- Queue the week: TikTok first (native), cross-post to Reels + Shorts with per-platform caption tweaks. Stagger across Mon/Wed/Thu/Fri.
- Leave the X slots empty on purpose — those are live newsjacks.

### ⑥ Mon–Fri — Engage (15 min/day)
- Reply to every comment in the first hour (first-hour engagement drives ~80% of reach).
- 5–10 quality comments on other creators' / news posts in the niche.
- Fire any reactive X post when a data drop or viral receipt hits — quote it with your chart + a one-line verified take.

---

## Faceless evergreen B-side (optional, for volume)

When you want extra reach without filming, spin a **pure-data, faceless** clip: Remotion data-viz + **ElevenLabs** voiceover (your cloned voice or a brand voice) + Captions. These are great for SEO/evergreen ("Every Cadbury size change since 2019") and don't cost a film day. Keep them clearly the B-side — your face stays the channel's identity. (Still Bucket-1 clean: real screenshots, real numbers.)

---

## Tool-by-tool cheat notes

- **Claude / Agent Opus** — your creative director + data analyst. It reads the DB, ranks ideas, drafts scripts, generates Remotion components, writes platform captions. It stops at *finished post* — you film and approve.
- **Remotion** — programmatic, deterministic, on-brand data viz. One template, infinite data. This is what makes your overlays a moat instead of generic CapCut text. (See the project's `remotion` skill for best practices.)
- **Higgsfield** — atmosphere/metaphor b-roll + `virality_predictor`. Hard rule: never let it render anything a viewer could read as evidence.
- **Captions App** — the assembly + caption + sound finishing line; batch mode for doing the whole week at once.
- **ElevenLabs** — voice for the faceless B-side only; your real voice carries authority/personal pieces.

---

## What "done" looks like each week

5/5 on every clip's checklist, 3–5 clips scheduled across TikTok/Reels/Shorts, X armed for the week's data drop, and you spent **one Saturday planning slot + one Sunday afternoon** — not your whole week. That's the burnout-proof target.
