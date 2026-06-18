# Viral VFX CapCut Agent (`vfx`)

Turns a step-by-step VFX manual + your footage into an **openable CapCut project**
plus a short finish-by-hand checklist. The brain (recommend / footage-QA / compile
/ draft-assembly) runs locally; the CapCut project is written directly to disk.

## One-time setup (macOS)

```bash
# 1. System tools
brew install ffmpeg poppler           # ffmpeg = footage probing/QA; poppler = PDF manuals

# 2. Get the code (in your fullcarts-app clone)
cd ~/path/to/fullcarts-app
git fetch origin claude/exciting-knuth-j4q5t6
git checkout claude/exciting-knuth-j4q5t6

# 3. Python env + install (creates the `vfx` command)
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 4. Confirm
vfx --help
```

After this, `vfx` works **from any directory** (as long as the `.venv` is active —
run `source ~/path/to/fullcarts-app/.venv/bin/activate` in a new terminal, or add an
alias; see "Launching for future videos" below).

## Everyday commands

```bash
# What can I make with the gear I have?
vfx recommend --equipment tripod,lighting,phone

# What do I film + what will I finish by hand, for one effect?
vfx plan clone_effect_talking_head

# Add a new manual you authored to the library (see docs/MANUAL_SCHEMA.md)
vfx ingest-manual ~/path/to/my_effect.yaml

# Build a CapCut project from a manual + your clips (the main one):
vfx build --manual ~/manuals/clone_effect_talking_head.yaml \
  --asset pointing_clip=~/Movies/clip1.mp4 \
  --asset stepin_clip=~/Movies/clip2.mp4 \
  --out ~/Movies/CapCut/User\ Data/Projects/com.lveditor.draft/
# Then: quit + reopen CapCut, open the new project, finish the FINISH_BY_HAND.md steps.
```

`build` also accepts a slug from the library instead of `--manual`:
`vfx build clone_effect_talking_head --asset ... --out ...`

## Launching for future videos

Add this alias to `~/.zshrc` so you never think about the venv again:

```bash
echo 'alias vfx="~/path/to/fullcarts-app/.venv/bin/vfx"' >> ~/.zshrc
source ~/.zshrc
```

Now just open Terminal and run `vfx ...` whenever you want to make a video.

## AI / conversational features (optional)

`recommend`, `plan`, `ingest-manual`, and `build` need **no API key** — they're
deterministic and free. Only the AI features need one:
- `enrich` (one-time LLM normalization of the bundled dataset)
- Script Studio / computer-use (future)

Set a key when you use those: `export ANTHROPIC_API_KEY=sk-ant-...`
(get one at https://console.anthropic.com/settings/keys).

## Notes
- CapCut draft format is version-specific (built against v8.6.0). If a future
  CapCut update makes a generated project fail to open, re-capture a golden sample
  (see `vfx/capcut/FORMAT_NOTES.md`) and the writer's skeleton can be refreshed.
- Run the tests anytime: `python -m pytest tests/vfx/ -v`
