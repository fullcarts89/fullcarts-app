---
name: hyperframes
description: >
  Entry point for creating, previewing, editing, animating, or rendering videos
  with HyperFrames (HTML/CSS/GSAP → deterministic MP4) in this repo. Use whenever
  the task is to make / edit / animate / render a video, motion graphic, explainer,
  title card, overlay, captioned clip, product promo, or HyperFrames HTML
  composition — the same way `remotion` is used for Remotion work. The HyperFrames
  project lives in `videos/`. This skill orients you and hands off to the full
  HyperFrames workflow skills installed under `videos/.agents/skills/`.
metadata:
  tags: hyperframes, video, animation, motion-graphics, render, gsap, mp4
---

## When to use

Use this skill for **any** video work in this repo built with HyperFrames —
creating, previewing, editing, animating, or rendering a video, motion graphic,
explainer, overlay, or HTML composition. It's the HyperFrames counterpart to the
`remotion` skill.

(For the FullCarts weekly social batch loop specifically, `fullcarts-content` is
still the active operator — it owns the brief/script/gates and calls into video
tooling. This skill is the general-purpose "I'm editing a video" router.)

## The project lives in `videos/`

All HyperFrames work happens in `videos/`:

- `videos/index.html` — main composition (root timeline)
- `videos/compositions/` — sub-compositions (`data-composition-src`)
- `videos/vendor/` — locally vendored libs (see "Environment gotcha" below)
- `videos/renders/` — rendered MP4 output
- `videos/meta.json` — project metadata

## Read the HyperFrames skills FIRST

The full, authoritative HyperFrames knowledge is installed under
`videos/.agents/skills/`. **Always read the relevant one before writing or
modifying a composition** — they encode framework rules (timeline registration on
`window.__timelines`, `data-*` timing/track semantics, `class="clip"` visibility)
that generic web/CSS knowledge will get wrong.

Start at `videos/.agents/skills/hyperframes/SKILL.md` — it routes "make me a
video" intent to the right workflow. Key skills:

- `hyperframes/` — **entry router. Read first.**
- `hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`,
  `hyperframes-cli`, `hyperframes-media`, `hyperframes-registry` — domain knowledge.
- Workflows: `product-launch-video`, `faceless-explainer`, `website-to-video`,
  `pr-to-video`, `embedded-captions`, `graphic-overlays`, `motion-graphics`,
  `general-video`, `remotion-to-hyperframes`.

`videos/CLAUDE.md` also documents the project's key rules and commands.

## Commands (run from `videos/`)

```bash
cd videos
npm run dev      # preview server with live reload — LONG-RUNNING, start with run_in_background: true
npm run check    # lint + validate (headless Chrome) + inspect — always run after edits
npm run render   # render to MP4 (writes to videos/renders/)
npm run publish  # publish + shareable link
npx hyperframes docs <topic>   # offline reference: data-attributes, gsap, compositions, rendering, examples, troubleshooting
```

> `npm run dev` blocks until stopped — always launch it with `run_in_background: true`,
> never as a foreground command.

Always run `npm run check` and fix all errors before considering a composition done.

## Environment gotcha — vendor CDN libs locally

This repo runs in remote Claude Code containers whose network proxy does TLS
interception. The system trusts the proxy CA, but the headless Chromium that
HyperFrames downloads does **not** — so any `<script src="https://cdn...">` in a
composition fails at validate/render time with `ERR_CERT_AUTHORITY_INVALID`
("gsap is not defined").

**Fix:** vendor the library into `videos/vendor/` and reference it with a relative
path. GSAP is already vendored (`videos/vendor/gsap.min.js`, referenced from
`index.html`). For any new CDN dependency, do the same:

```bash
cd videos
curl -sS https://cdn.jsdelivr.net/npm/<pkg>/dist/<file>.js -o vendor/<file>.js
# then in the HTML: <script src="vendor/<file>.js"></script>
```

Prerequisites (Node 22+, ffmpeg) are guaranteed by the SessionStart hook in
`.claude/hooks/session-start.sh`.
