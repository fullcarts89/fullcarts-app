# Session Handoff — FullCarts Content System (continue here)

**Branch with ALL work:** `claude/peaceful-euler-xwh8mf` (committed + pushed).
**Read this first in a new thread**, then the linked docs. Goal: continue producing face-forward,
data-driven shrinkflation videos with the Remotion pipeline we built.

---

## What exists (all on the branch)

### Strategy + rules (docs/)
- `docs/plans/2026-06-10-face-forward-content-strategy.md` — master strategy (face-forward, "Caught:" series, TikTok-led, content mix, schedule).
- `docs/content/content-rules.md` — the 5 non-negotiables + three-bucket evidence policy.
- `docs/content/approved-claims.md` — verified claims registry (DB-checked; say "2,200+" not "3,000+").
- `docs/content/content-angles.md` — pillars, contrarian takes, the **Emotional Lock-In** bank.
- `docs/content/series.md` — the **"Caught:"** series + future threads (How They Hid It / Report Card / Same Price Less Stuff).
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
1. **Review the v4 hooks-over-you cut** (`FolgersCut`) and tune: hook timing, zoom intensity, any text overlapping the face during the push-in (chin text at ~0:42).
2. **Build more motion graphics** (requested): a real **Rockets & Feathers** animated line (price up fast / down slow, can stays small), a **price-per-pot count-up**, a **"fewer cups"** visual, a branded **outro/CTA card** — to break up the kinetic-text climax (37–52s).
3. **Density balance:** user wants graphics over the face in negative space, fewer full cutaways — keep iterating toward that.
4. **Studio access:** the sandbox can't expose a URL to the user → run Studio **locally** for live editing, or the agent renders previews. (This caused the friction at end of session.)
5. Then: repeat the loop for the next episode (Gatorade is scripted in `series.md`).

## Gotchas learned (don't relearn these)
- **Zip images to send them** (pasted images aren't saved to disk in this env).
- **SRT = sync.** Without word timings, overlay timing is blind-guessing and feels like a slideshow.
- **Fonts** are embedded (no fetch) so long multi-tab renders don't hang.
- **Accuracy:** "2,200+" events, not "3,000+". Per-oz comparison spans years (one listing is archived) — frame the **51→43.5oz cut** as the hard fact, the chart as the rockets-and-feathers backdrop.
- **Evidence policy:** real before/after image + real chart screenshot only; never an AI chart/packaging.
