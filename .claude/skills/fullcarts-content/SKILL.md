---
name: fullcarts-content
description: "Use when producing FullCarts social content — the face-forward, data-driven shrinkflation videos for TikTok/Reels/Shorts/X. Trigger phrases: 'make this week's content', 'weekly content batch', 'content brief', 'what should I film', 'shrinkflation video', 'shrinkflation script', 'fullcarts post', 'new reveal', 'rundown video', 'newsjack the CPI print', 'render the overlay', 'production packet'. This skill is the ACTIVE OPERATOR for the weekly batch loop: it pulls a data-backed brief from the FullCarts database, drafts scripts to the house template, enforces the content rules + approved-claims + evidence gates, renders the Remotion overlays, generates Higgsfield b-roll, and hands over a film-ready packet. For generic social strategy see social; for video tooling see video; for Remotion specifics see remotion."
metadata:
  version: 1.0.0
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
- `docs/content/first-batch.md` — the repeatable script template + 5 worked examples
- `docs/content/series.md` — the bingeability engine: the "Caught:" series + future-series backlog
- `docs/content/content-angles.md` — what & how to talk: pillars, contrarian takes, the Emotional Lock-In bank
- `references/hooks.md` — the Hook System (The Snap 3-beat + Emotional Lock-In + the 4-mistake fixes)
- `docs/content/profile-copy.md` — bios + pinned posts

## The automation boundary (what you do vs. what the human does)

| You (Claude, the operator) | The human (in external apps) |
|---|---|
| Pull the weekly brief from Supabase; rank by convergence | Films real-face hooks + hands-on proof on their phone |
| Draft scripts to the template; run all three gates | Assembles + captions in **Captions App** (no API — manual) |
| Render the Remotion overlays to file (alpha) | Generates B-side/hook-test UGC in **Agent Opus** from your brief |
| Generate Higgsfield b-roll via MCP (Bucket-2 only) | Posts / schedules |
| Emit the per-clip **production packet** | Approves voice + final cut |
| (Optional) ElevenLabs VO via env-var API key, for faceless clips | |

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
2. **Brief.** Rank candidates by convergence (FullCarts signal × external news/macro/calendar). Pick 3–5, and **assign each to a series** — default the primary **"Caught:"** series (keep the fixed `Caught: [Brand]` cold-open), or a future thread per `series.md`.
3. **Script.** Draft each to the house template (cold-open → hook → **lock-in** → proof → trick → payoff → CTA). Pick an **angle + a contrarian take + a feeling** from `content-angles.md`, write the hook as **The Snap** and add the **Emotional Lock-In** beat ([references/hooks.md](references/hooks.md)); per-platform captions + hashtags. Never a vague open loop.
4. **Gate.** Run all three gates on every script. A script that fails any gate does not proceed.
5. **Assets.** Render the matching Remotion overlay(s); generate Bucket-2 Higgsfield b-roll if needed; note the real screenshots the human must grab.
6. **Packet.** Emit a per-clip production packet (shot list, on-screen text + timing, overlay files, captions, hashtags, post time, and an Agent-Opus brief for any B-side clip).
7. **Hand off + iterate.** The human films, assembles in Captions, posts. You stop at the packet. **Every ~10 posts, review by _follows-driven_ (not views)** — find the outlier, extract why it won (hook? series? brand?), and bias the next batch toward it.

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
