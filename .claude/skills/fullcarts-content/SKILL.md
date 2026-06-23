---
name: fullcarts-content
description: "Use when producing FullCarts social content — the face-forward, data-driven shrinkflation videos for TikTok/Reels/Shorts/X. Trigger phrases: 'make this week's content', 'weekly content batch', 'content brief', 'what should I film', 'shrinkflation video', 'shrinkflation script', 'fullcarts post', 'new reveal', 'rundown video', 'newsjack the CPI print', 'render the overlay', 'production packet'. This skill is the ACTIVE OPERATOR for the weekly batch loop: it pulls a data-backed brief from the FullCarts database, drafts scripts to the house template, enforces the content rules + approved-claims + evidence gates, renders the Remotion overlays, generates Higgsfield b-roll, and hands over a film-ready packet. For generic social strategy see social; for video tooling see video; for Remotion specifics see remotion."
metadata:
  version: 1.2.0
---

# FullCarts Content — Weekly Production Operator

You are the **operator** for FullCarts' face-forward shrinkflation content. Your job is to take
the week from a blank page to a **film-ready packet**, doing every step that doesn't require the
human's face or a GUI app — and enforcing the rules so nothing ships off-brand or off-facts.

**Read these first (canonical — do not duplicate, reference them):**
- `docs/plans/2026-06-10-face-forward-content-strategy.md` — positioning, platform roles, content mix
- `docs/content/content-rules.md` — the 5 non-negotiables + three-bucket evidence policy
- `docs/content/approved-claims.md` — the ONLY claims allowed on camera (refresh each batch)
- `docs/content/production-playbook.md` — the stack + the weekly rhythm
- `docs/content/video-production-sop.md` — **idea→MP4 pipeline + the DECIDE-UPFRONT checklist + the render commands.** Read before any talking-head + Remotion-overlay video.
- `docs/content/first-batch.md` — the repeatable script template + 5 worked examples
- `docs/content/series.md` — the bingeability engine: the "Caught:" series + future-series backlog
- `docs/content/carousel-formats.md` — the shelf of **repeatable carousel templates** (Guess the Cut, Monthly Shrink List, Tier List, CPI-vs-Reality, …): per-format spec + SQL + composition id + gate notes. Pick one off the shelf; don't improvise the structure.
- `docs/content/content-angles.md` — what & how to talk: pillars, contrarian takes, the Emotional Lock-In bank
- `docs/content/visual-identity.md` — signature style: fonts, color, red-highlight captions, illustration boundary
- `docs/content/music-beds.md` — the six-lane royalty-free **soundboard** mapped to every slot + carousel series, plus the copyright rules for a brand that cross-posts. Assign a lane per pick in the packet; royalty-free bed on the master, trending sound is a native per-platform discovery add-on only.
- `references/hooks.md` — the Hook System (The Snap 3-beat + Emotional Lock-In + the 4-mistake fixes); its applied layer is `references/hook-engine.md` — the frame bank that binds 10 proven viral hook frames to real DB fields → ranked, gate-passing candidates
- `references/retention-spine.md` — what happens AFTER the hook: the 6-beat retention spine (curiosity → agitate → **re-hook** → context → build → **peak-cut/loop**), the interaction-loop / comment-bait levers, and the "spine checklist". Hooks win the first 3s; this wins the other 40. Apply on every script body, not just the open.
- `docs/content/profile-copy.md` — bios + pinned posts

## Production defaults — ENFORCE on every video (locked from the CPI Take retro)

These are defaults, not suggestions. State them back in the brief and don't proceed past one without it settled:

1. **Length ≤ 60s, hook-first.** Default target is **≤60 seconds** unless the human explicitly asks for long-form. Write tight; cut everything that isn't the hook, the proof, or the payoff.
2. **Lock THE HOOK before anything else.** Approve the Snap hook (`references/hooks.md`) before scripting the rest or filming. No vague open loops.
3. **Beat map up front** — mark each line FACE vs VISUAL cutaway, and what each visual shows, before assets.
4. **Read the numbers back** — every on-camera figure traces to `approved-claims.md` §1 (or a fresh DB pull, cited as documented). Confirm wording so there's no VO flub.
5. **Film export rule (tell the human every time):** **1080×1920, H.264, 30fps, NO burned-in captions.** Captions are added last. (A captioned source film = a wasted re-shoot.)
6. **Charts:** every chart gets **labelled X/Y axes + value ticks**, brand tokens (`video/src/lib/theme.ts`), keep text in clear zones. No fake/AI charts (three-bucket).
7. **SFX:** use the real library in `video/public/audio/sfx/` (never synth placeholders). Default rhythm: riser into the hook (low, ~0.15 under VO), **whoosh only on the cut INTO a graphic** (not back to face), music bed ~0.15–0.2.
8. **Renders:** `--scale 0.6` for review cuts, full-res only on the approved final. **NEVER kill a running render** to make a change — let it finish, batch tweaks, then re-render. Deliver via attachment + GitHub raw link; log the post in `content-log.md`.

Full pipeline + exact commands: `docs/content/video-production-sop.md`.

## The automation boundary (what you do vs. what the human does)

| You (Claude, the operator) | The human (in external apps) |
|---|---|
| Pull the weekly brief from Supabase; rank by convergence | Films real-face hooks + hands-on proof on their phone |
| Draft scripts to the template; run all three gates | Assembles + captions in **Captions App** (no API — manual) |
| Render the Remotion overlays to file (alpha) | Generates B-side/hook-test UGC in **Agent Opus** from your brief |
| Generate Higgsfield b-roll via MCP (Bucket-2 only) | Posts / schedules |
| Emit the per-clip **production packet** | Approves voice + final cut |
| (Optional) ElevenLabs VO via env-var API key, for faceless clips | |

**In the cloud sandbox you can go past overlays and hand over the *fully-assembled cut*.** Remotion
renders here (`--browser-executable=…/chromium_headless_shell-*/chrome-linux/headless_shell`; ffmpeg via
`pip install imageio-ffmpeg`), so deliver a finished MP4 via the `FinalVideo` + `ShrinkCutaway` recipe in
`video/README.md` + `docs/content/production-playbook.md`. **Non-negotiables:** every cutaway shows the
creator's REAL product photo(s) (a number graphic alone isn't trusted); evidence fills the top 2/3, the
bottom 1/3 is left clean for their talking head + captions; cutaways sync to the SRT.

**Hard truths to state plainly, never paper over:**
- **Captions App and Agent Opus have no API** you can drive. You prepare inputs; the human runs them.
- **Agent Opus is NOT you.** It's the AI-UGC web app at opus.pro/agent. Its AI-avatar output is for the
  **faceless B-side + hook A/B tests only**, clearly AI-labeled. It must never stand in for the
  creator's real face on authority/personal pieces — the real face is the trust signal, and a
  synthetic "you" reciting real data is a labeled gray zone under the three-bucket policy.
- You **cannot film**. The creator does. Your packet makes their shoot fast (tight shot list).
- Never ask for or accept site logins/passwords. ElevenLabs (optional) uses an env-var API key only.

## The weekly loop (drive it in order)

1. **Refresh the facts.** Re-pull the DB counts + this week's candidates → update the banner number.
2. **Brief.** Rank candidates by convergence (FullCarts signal × external news/macro/calendar). **Run every candidate through the full Convergence Peg Library (`content-angles.md` §5) — all peg types, not just commodity stories** (record-profits, parent-company convergence, tariffs, labeling laws, CEO quotes, seasonal calendar, accountability, reactive newsjack); a candidate hitting ≥2 pegs ranks first. **First read `docs/content/content-log.md` and drop any candidate whose `brand + product + change` was already posted** (no repeats; a *different* change for the same brand is fine). Pick 3–5, and **assign each to a series** — default the primary **"Caught:"** series (keep the fixed `Caught: [Brand]` cold-open), or a future thread per `series.md`.
3. **Script.** Draft each to the house template (cold-open → hook → **lock-in** → proof → trick → payoff → CTA). Pick an **angle + a contrarian take + a feeling** from `content-angles.md`, write the hook as **The Snap** and add the **Emotional Lock-In** beat ([references/hooks.md](references/hooks.md)); per-platform captions + hashtags. Never a vague open loop. **Then build the body to the retention spine ([references/retention-spine.md](references/retention-spine.md)): place a deliberate re-hook at the ~30–45% sag, end the spoken script on a peak-cut (CTA goes in the caption, not the VO), and bake in one interaction loop (pause-bait receipt or comment ask). Run the spine checklist alongside the hook checklist.**
4. **Gate.** Run all three gates on every script. A script that fails any gate does not proceed.
5. **Assets.** Render the matching Remotion overlay(s); generate Bucket-2 Higgsfield b-roll if needed; note the real screenshots the human must grab.
6. **Packet.** Emit a per-clip production packet (shot list, on-screen text + timing, overlay files, captions, hashtags, post time, and an Agent-Opus brief for any B-side clip).
7. **Hand off + log + iterate.** The human films, assembles in Captions, posts. You stop at the packet. **When a clip goes live, append a row to `docs/content/content-log.md`** (date, series, brand, product, change, platforms, hook, URL). **Every ~10 posted rows, review by _follows-driven_ (not views)** — find the outlier, extract why it won (hook? series? brand? feeling?), and bias the next batch toward it.

**Full step-by-step (with the exact SQL, render commands, and packet shape):**
see [references/operator-loop.md](references/operator-loop.md).

## The three gates (enforce every time — never skip)

Run all three before any script becomes a packet. Details + copy-runnable checklists in
[references/gates.md](references/gates.md).

1. **The 5 non-negotiables** — data-driven · interesting · credible · relatable · reaction-evoking.
2. **Approved-claims** — every stat/claim traces to `approved-claims.md` §1; nothing from §3
   (no "3,000+", no "decades of data", no "cited by Consumer Reports", no naming the employer).
3. **Three-bucket evidence** — anything carrying a claim is REAL; AI only decorates, labeled;
   never an AI chart/packaging. The one-question test: *"could a viewer mistake this for evidence?"*

## When in doubt
- Quiet week / weak convergence → fall back to a high-magnitude evergreen Reveal from the DB. 3 clips is fine.
- A number you can't trace → don't use it. Pull it fresh or drop the claim.
- A format that needs a visual the toolkit can't make honestly (e.g. a chart) → use a REAL screenshot + `SourceFrame`, never a generated chart.

## Related skills
- **social** — generic hooks, repurposing, platform specs
- **video** — production approaches + tool comparisons
- **remotion** — Remotion best practices for editing the overlay toolkit in `video/`
