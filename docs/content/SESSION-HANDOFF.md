# Session Handoff — FullCarts Content System (continue here)

**Branch with ALL work:** `claude/peaceful-euler-xwh8mf` (committed + pushed).
**Read this first in a new thread**, then the linked docs. Goal: continue producing face-forward,
data-driven shrinkflation videos with the Remotion pipeline we built.

---

## What exists (all on the branch)

### Strategy + rules (docs/)
- `docs/plans/2026-06-10-face-forward-content-strategy.md` — master strategy (face-forward, "Caught:" series, TikTok-led, content mix, schedule).
- `docs/content/posting-schedule.md` — **the standing weekly operating plan** + the carousel/story template system (1 film day + auto-generated DB carousels + light daily posting; weekly table; effort tiers; phased ramp; "slice-and-dice" variant menu; swipe-through principle; images/logos approach).
- `docs/content/content-rules.md` — the 5 non-negotiables + three-bucket evidence policy.
- `docs/content/approved-claims.md` — verified claims registry (DB-checked; say "2,200+" not "3,000+").
- `docs/content/content-angles.md` — pillars, contrarian takes, the **Emotional Lock-In** bank.
- `docs/content/series.md` — the **"Caught:"** series + the **locked weekly slot formats** (*Caught Slipping* Mon / *Inflation Receipt* Thu / *Breaking Shrink* Fri / *Why I Built This* Sun) + future threads (How They Hid It / Report Card / Same Price Less Stuff).
- `docs/content/vlog-ideas.md` — **52-topic backlog** for the Sunday "Why I Built This" vlog (one year, checkable).
- `docs/content/production-playbook.md` — the stack + **the proven SRT-synced loop** (see below).
- `docs/content/visual-identity.md` — fonts/color/captions + the **animation library** + safe zones + "cut away often" principle.
- `docs/content/profile-copy.md` — per-platform bios + pinned posts.
- `docs/content/first-batch.md` — 5 ready-to-film scripts.
- `.claude/skills/fullcarts-content/` — the operator skill (brief → script → gates → render).

### Video toolkit (`video/` — Remotion, `@fullcarts/video`)
Branded compositions (in `video/src/compositions/`):
- `FinalVideo` — the assembler: ingests film + a timeline JSON → composited MP4. Supports **captions, overlays, cutaways, SFX, a camera track (zoom/punch-in/pattern-interrupt/fake-angle rehook)**.
- `CaughtTitle`, `ShrinkOverlay`, `StatCard`, `RundownChip`, `SourceFrame` — overlays.
- `BeforeAfter` — clean before/after card (cropped cans + size + price-per-oz).
- `ShrinkReveal` — "watch it shrink" animation (real product scales down + ghost outline + ticking number).
- `KineticQuote` — full-screen kinetic typography for punch lines.
- `HookText` — **text in the negative space over the talking head** (above the head / under the chin).
- `Carousel` (4:5, 1080×1350) — **data carousel, zero filming**: cover → ranked product slides (before/after bars, −X%, optional product image + brand logo) → CTA with the persona line. One slide per frame (render stills `0..N+1`). Default: "5 Stealth Shrinks." Driven by live DB queries.
- `TierList` (4:5) — **swipe-reveal carousel**: cover → tiers bottom-up D…S (one per swipe, progress dots) → **full list as the payoff last slide**. Brand pills with logo/monogram icons. See `posting-schedule.md` for the variant menu (worst-this-month, by-category, vs-CPI, US-only, …).
- `Thumbnail`, `SafeZonePreview` (dev), `BeforeAfter`.
- Fonts are **embedded as base64** (`src/lib/fontsCss.ts`) so renders work offline. Safe zones in `src/lib/safezone.ts`.

---

## The proven production loop (USE THIS)
1. **Film** to camera, vertical 9:16, ~60s, **no product needed** (proof = the before/after image).
2. **Caption in your app** (CapCut/Captions) → **export the `.srt`** (this is the sync key).
3. **Send to the agent as FILES:** the film, the `.srt`, and the evidence images **ZIPPED**
   (⚠️ pasted/attached *images do NOT reach the agent* — only real files like `.mov`/`.zip`/`.srt` do. **Zip the images.**)
4. **Agent builds it:** clean before/after card, real chart behind the citation, **every overlay/cutaway/hook synced to the SRT word timings**, your face the anchor (~35–65%), graphics in the negative space (not all full-screen cutaways = avoids the PowerPoint feel). Output: finished MP4, **no captions**.
5. **You** add captions in your app (from the same SRT) → post.

---

## Folgers piece — current state (the work-in-progress)
- **Script + SRT:** the "Caught: Folgers" script (in `series.md` / `folgers-package.md`); the user's
  real SRT was used to sync the latest cut.
- **Timeline:** `video/src/props/folgers-final.json` = the **v4 "hooks-over-you" cut**: opening zoom,
  pattern-interrupt punch (~0:17), fake angle-change push-in (~0:38), text above-head + under-chin
  while the face stays on screen, with full-screen only for the 3 evidence beats (ShrinkReveal,
  BeforeAfter, chart). `FolgersCut` composition in `Root.tsx` loads it.
- **Real data baked in:** Folgers 51oz→43.5oz (−14.7%); per-oz $0.22 → 59.5¢; coffee chart ~420→~251 (−40% from peak, ICE/tradingeconomics, Jun 2026).

### ⚠️ Assets are NOT in git (they're the user's uploads, gitignored)
`video/public/film/`, `video/public/cutaways/` are gitignored. In a **new thread/session the sandbox
is fresh**, so re-provide:
- the **film** → attach the `.mov` (saves to disk), place at `video/public/film/folgers.mov`
- the **before/after listings + coffee chart** → **as a `.zip`**, unzip into `video/public/cutaways/`
  (then rebuild the before/after card: `npx remotion still BeforeAfter public/cutaways/folgers-before-after.png --frame=0`)
- the **`.srt`** → attach (saves to disk) for re-syncing.

---

## How to render / preview
```bash
cd video && pnpm install          # or npm install
# render the Folgers cut (sandbox needs --browser-executable; a normal machine doesn't):
npx remotion render FinalVideo out/folgers.mp4 --codec=h264 --props=src/props/folgers-final.json
# live Studio (run on YOUR machine to scrub/edit; the sandbox's localhost isn't reachable):
npx remotion studio
```
- In the sandbox, Chrome is at `/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell` → pass `--browser-executable=<that>`.
- Full render ≈ 6–8 min; preview single frames with `npx remotion still FinalVideo out/x.png --frame=N --props=...`.

---

## Open items / next steps (where we stopped)
1. **Review the v5 cut** (`FolgersCutV5`, `src/props/folgers-final-v5.json`) — same as v4 but the
   climax hooks are replaced with the new motion graphics: `PriceJump` (37.7–41.8, per-oz 22¢→59.5¢,
   above-head), `RocketsFeathers` (42.4–47.4, above-head), and a full-frame `OutroCard` close
   (53.0–end). Needs the film + cutaway assets dropped back in to render (see asset section above).
2. ~~Build more motion graphics~~ **DONE (2026-06-11):** `RocketsFeathers`, `PriceJump`, `FewerCups`,
   `OutroCard` — all registered in Root, wired into `FinalVideo` as cue types `rockets` / `pricejump` /
   `fewercups` / `outro`, schema-defaulted AND destructure-defaulted (cues can pass sparse props).
   `FewerCups` is NOT in the v5 timeline: cups-per-can isn't in the approved-claims registry — read the
   real number off a can label before using it (the default shows the verified −7.5 oz fact instead).
3. **Density balance:** v5 keeps the face on screen for both climax graphics (negative-space panels,
   `zone: "above"`). Keep iterating; `FewerCups`/`PriceJump`/`RocketsFeathers` all take `zone: "above" | "chin"`.
4. **Studio access:** on the user's local machine `cd video && npx remotion studio` just works now.
5. Then: repeat the loop for the next episode (Gatorade is scripted in `series.md`).

## Gotchas learned (don't relearn these)
- **Zip images to send them** (pasted images aren't saved to disk in this env).
- **SRT = sync.** Without word timings, overlay timing is blind-guessing and feels like a slideshow.
- **Fonts** are embedded (no fetch) so long multi-tab renders don't hang. ⚠️ The original
  `fontsCss.ts` had EMPTY font-family names (`font-family:;`) — every render before 2026-06-11 fell
  back to a serif. Fixed by `video/scripts/gen-fonts.mjs` (regenerates the file; rerun if fonts change).
  **Re-render anything kept from before the fix.**
- **Accuracy:** "2,200+" events, not "3,000+". Per-oz comparison spans years (one listing is archived) — frame the **51→43.5oz cut** as the hard fact, the chart as the rockets-and-feathers backdrop.
- **Evidence policy:** real before/after image + real chart screenshot only; never an AI chart/packaging.
