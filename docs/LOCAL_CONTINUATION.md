# Continuing on your Mac — no more terminal back-and-forth

We hit the wall that defines this whole project: **I run in the cloud, CapCut runs
on your Mac.** Every change had to be hand-carried across with terminal commands.
This doc sets up the bridge so that stops.

There are two ways to continue. **Option 1 is the real fix.**

---

## Option 1 (recommended): run Claude Code on your Mac

Right now you're talking to me through the cloud. If you instead run **Claude Code
on your own Mac**, then *I* am running on your machine — I can write CapCut
projects straight into your drafts folder, see the files, and rebuild on your
feedback **with no zip, no download, and no terminal steps from you.** The cloud↔Mac
gap that caused all the friction simply disappears.

- **Get it:** Claude Code is available as a **Mac desktop app** and a VS Code
  extension — https://claude.com/claude-code
- **Open this project** in it: `~/Documents/fullcarts-app`
- Then we continue exactly where we left off, except now when you say *"make the
  morph warpier"* I change it and it lands in your CapCut directly. You give
  feedback; I do the work; you watch it in CapCut.

This is the closest thing to the original vision (you provide film + feedback, the
tool does the rest).

---

## Option 2 (no Claude on your Mac): double-click launchers

If you'd rather not run Claude locally, I've built two **double-click** apps so you
never type a terminal command. After this, the loop is: *you tell me a change → I
push it → you double-click one icon → it appears in CapCut.*

**One-time setup:**
1. In Finder, open `~/Documents/fullcarts-app/scripts/`.
2. Double-click **`setup_local.command`**. (If macOS blocks it: right-click →
   Open → Open.) It fetches the draft engine and installs the bits. A `vfx_assets`
   folder opens.

**Each video:**
1. Put your two clips in `~/Documents/fullcarts-app/vfx_assets/`, named exactly
   **`current.mov`** (the current/smaller pack) and **`old.mov`** (the older/bigger
   pack or a photo).
2. Double-click **`make_morph.command`**. It pulls my latest changes, builds the
   project, and drops it into your CapCut drafts.
3. **Quit CapCut (Cmd+Q) and reopen it.** Open the **PACKAGE_MORPH** project.

**To change the look without me:** create a text file
`vfx_assets/settings.txt` with lines like:
```
TRANSITION=Stretch
YEAR=2024
NAME=KRAFT_MORPH
```
Transitions to try: `Dissolve`, `Mix`, `Stretch`, `Pull_in`, `Glitch`, `Inhale`.
Then double-click `make_morph.command` again.

---

## What I do vs. what stays manual (the honest boundary)

| Automated (the tool / me) | Still needs a human |
|---|---|
| Import clips, lay tracks, transition, scale "grow" keyframes, Typewriter year text | **Filming** the clips (you) |
| Generate the openable CapCut project from your assets | **Remove Background** — it's an in-app AI step CapCut runs; no file can produce it. Do it on the end-card clip by hand, or strip the background outside CapCut and drop in the cut-out. |
| Change transition / timing / text / add effects (I edit the generator) | Watching the result in CapCut and telling me what to fix (you're the eyes — I can't see your screen) |

---

## Where we are (so the next session can pick up fast)

- **Proven:** the file-based generator works — a library-generated morph draft
  (clip A → transition → clip B + scale grow + Typewriter year) **opens in your
  updated CapCut** with media linked. This is the reliable path; computer-use
  (clicking CapCut's GUI) was abandoned as too brittle.
- **Engine:** `pyJianYingDraft` (from the CapCutAPI repo), fetched into `vendor/`
  by `setup_local.command` (not committed; MIT per its `pyproject`, no LICENSE
  file — fine for personal use).
- **Generator:** `scripts/build_morph.py` (`--current --old --transition --year
  --name`). Launchers: `scripts/setup_local.command`, `scripts/make_morph.command`.
- **Open items:** dial in the exact "morph" transition (the real *Tawel Flip*
  isn't in the engine's catalog — closest are Dissolve / Stretch; or we source its
  resource ID); add the glitch + data-reveal text + Remove-BG end card to match the
  full "Grocery Store Time Machine" script; anchor the on-screen numbers to the
  documented Kraft Mac & Cheese 225 g → 200 g shrink.
- **Other tracks still in the repo:** the QA gate, recommender, the `vfx` CLI, the
  FullCarts content pipeline. Unchanged.
