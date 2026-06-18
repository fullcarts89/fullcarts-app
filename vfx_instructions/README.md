# Viral VFX — Instruction Dataset

Machine-readable recreation instructions for the full Viral VFX Vault catalog
(filming + CapCut editing). Built as inputs to a VFX video automation tool.
**Local reads only — no network, no API, no LLM cost.**

## Counts
**44 records** = **34 distinct VFX effects** + **7 foundation/training modules**
(CapCut crash course ×4, Getting Started, Keyframes, Working with Audio)
+ **4 long-form deep-dive lessons** (`deepdive_*`, incl. an 80-min keyframes demo).

The 34 effects break down as 26 standalone effects + 8 that the vault bundled inside
two BONUS modules (now split into individual records: Stomp Effect, Appear (Bonus),
Clothing Appear, Jump Cuts, Animating Text, Mirror/Flashlight Costume Change,
Costume Fly-in).

## Files
| File | What |
|---|---|
| `effects.json` | Full dataset: `{ meta..., effects: [...] }`. Source of truth. |
| `effects.jsonl` | One effect per line (stream-friendly). |
| `vfx.sqlite` | `effects` + `lessons` tables. List/dict fields are JSON-encoded strings. |
| `assets/<slug>/…` | Breakdown infographics, demo stills, demo frames. Referenced by relative path. |
| `vfx_loader.py` | Zero-dependency helper (`VFXData`). |
| `schema.json` | Field-by-field schema. |

## Quick start
```python
from vfx_loader import VFXData
d = VFXData()
eff = d.get("jump_cuts")
for s in eff["filming_steps"]: print("FILM:", s)
for s in eff["editing_steps"]: print("EDIT:", s)
for img in eff["breakdown_images"]: print(d.asset_path(img))   # official visual steps
d.filter(kind="effect")       # 34 effects only (excludes foundations? no—excludes deep dives)
d.filter(kind="deep_dive")    # the 4 long-form lessons
```

## Effect record (key fields)
- `slug`, `effect`, `difficulty` (`Foundation|Beginner|Intermediate`)
- `gear` — equipment (string; often null)
- `filming_steps` / `editing_steps` — ordered `list[str]`. **Narration-derived**; the
  authoritative raw source is `lessons[].transcript`.
- `breakdown_images` — relative paths to the official **tall annotated step-sheet
  infographics**. These exist for only **5 core effects** (Object Appear, 1st Cloning,
  Liquid from an Object, Ball Transition, Magic Pole Transition); the vault never made
  them for the rest. Decorative 16:9 title cards were stripped — this field is empty
  unless a genuine visual guide exists.
- `demo_still`, `demo_frames` — result preview images
- `tags` — `mask, overlay, keyframes, clean_plate, blend_mode, green_screen, cutout,
  feather, speed_ramp, transition, split_clip`
- `is_full_tutorial` — `false` = newer effect with only a demo (steps are standard
  technique in `technique_note`)
- `slug.startswith("deepdive_")` marks the 4 long-form reference lessons
- `lessons[]` — per-lesson `transcript`, `transcript_source` (`wistia|whisper`), `role`
  (`demo|filming|editing|guide|reference|deep_dive`), `duration_sec`, `source_url`, `wistia_id`

Personal-study use of member content; keep private.

## External sources (`external_sources.json`)

Public short-form videos (Instagram / YouTube / TikTok) ingested into the **same
schema** via `ingest_video.py`. `VFXData()` merges them automatically (each carries a
`source` + `source_url` + `source_creator`). Extra fields: `editing_screenshots`
(frames from the editing portion).

```bash
# Ingest one or many videos (appends/updates external_sources.json + assets/<slug>/)
python ingest_video.py "https://www.instagram.com/reel/XXXX/" "https://youtube.com/shorts/YYYY"
python ingest_video.py "<url>" --slug clone_effect --difficulty Beginner
INGEST_INSECURE=1 python ingest_video.py "<url>"   # behind a TLS-intercepting proxy
```
Requires `yt-dlp`, `ffmpeg`/`ffprobe`, and `faster-whisper` (transcription; skipped with
`--no-transcribe`). Re-running a URL updates that record in place.
