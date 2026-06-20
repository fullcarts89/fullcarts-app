# Computer-Use: finishing the GUI-only steps in CapCut

The file-writer (`vfx/capcut`) assembles everything expressible as **data** — clips,
tracks, layering, and (soon) transitions/text/keyframes. A few CapCut features can
**only** be done through the app's UI — **Remove Background**, particle/sticker
effects, some masks. The computer-use runner performs those by driving CapCut's
on-screen controls on your Mac.

> It runs on **your Mac** (that's where CapCut is) using **your** `ANTHROPIC_API_KEY`,
> so you control the spend. It is **token-heavy** (a screenshot per step): budget
> roughly **$0.50–$2+ per video**. It never runs without the key set.

## One-time setup (macOS)

1. **Install the input driver:**
   ```bash
   brew install cliclick
   ```
2. **Grant permissions** — System Settings → Privacy & Security:
   - **Screen Recording** → enable for your Terminal (so it can screenshot CapCut)
   - **Accessibility** → enable for your Terminal (so it can move the mouse / type)
3. **Set your API key** in the shell you launch from:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   ```
   (Use a **fresh** key — never one pasted into a chat.)

## Usage

```bash
# 1) Build the project (file-writer) and open it in CapCut.
python -m vfx build package_morph_transition --asset current_pack=... --out ~/Movies/...

# 2) Preview exactly what computer-use will do — FREE, no clicks, no API:
python -m vfx finish package_morph_transition --dry-run

# 3) With the project OPEN and visible in CapCut, run it for real:
python -m vfx finish package_morph_transition          # prompts before EACH action
python -m vfx finish package_morph_transition --yes     # auto-confirm (hands-off)
```

## Safety rails

- **Per-action confirm** by default — you approve each click/keystroke (`--yes` to skip).
- **Step budget** (`--max-steps`, default 60) so a confused run can't loop forever.
- **Kill switch** — Ctrl-C, or answer `q` at a prompt, stops immediately. Slamming the
  mouse into a screen corner also lets you grab back control.
- **Dry-run** prints the task and exits without touching the API or the mouse.

## Reliability notes

UI automation is inherently brittle: a CapCut update or a different screen
resolution can move buttons. The manuals name the **exact** CapCut feature labels
(e.g. `Remove Background → Auto Removal`) so the model finds controls by reading
the screen rather than by fixed coordinates — but expect to babysit the first few
runs and re-run a step if it misfires. The file-writer path (no UI) is always the
reliable backbone; computer-use is the last-mile for the genuine GUI effects.
```
