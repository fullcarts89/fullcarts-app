# Viral VFX — Instruction Dataset

Machine-readable recreation instructions for ~30 phone VFX effects (filming + CapCut
editing). Designed as inputs to a VFX automation tool. **Local reads only — no network,
no API, no LLM cost.**

## Files
| File | What |
|---|---|
| `effects.json` | Full dataset: `{ meta..., effects: [...] }`. Primary source of truth. |
| `effects.jsonl` | Same data, one effect per line (stream-friendly). |
| `vfx.sqlite` | `effects` + `lessons` tables. List/dict fields are JSON-encoded strings. |
| `assets/<slug>/…` | Images: official breakdown infographics, demo stills, demo frames. Referenced by **relative path** from records. |
| `vfx_loader.py` | Zero-dependency helper (`VFXData`). |
| `schema.json` | Field-by-field schema. |

## Quick start
```python
from vfx_loader import VFXData
d = VFXData()
eff = d.get("make_an_object_appear")
for s in eff["filming_steps"]: print("FILM:", s)
for s in eff["editing_steps"]: print("EDIT:", s)
for img in eff["breakdown_images"]: print(d.asset_path(img))
```
SQL:
```python
import sqlite3, json
con = sqlite3.connect("vfx.sqlite")
steps = json.loads(con.execute(
  "SELECT editing_steps FROM effects WHERE slug=?", ("ball_transition",)).fetchone()[0])
```

## Effect record (key fields)
- `slug`, `effect`, `difficulty` (`Foundation|Beginner|Intermediate`)
- `gear` — required equipment (string; null for full-tutorial effects)
- `filming_steps` / `editing_steps` — ordered `list[str]` (CapCut). **Narration-derived**;
  for the authoritative raw source use `lessons[].transcript`.
- `breakdown_images` — relative paths to official numbered visual guides (when available)
- `demo_still`, `demo_frames` — result preview images
- `tags` — derived technique tags: `mask, overlay, keyframes, clean_plate, blend_mode,
  green_screen, cutout, locked_off, feather, speed_ramp, transition, split_clip`
- `is_full_tutorial` — `true` = steps from the real lesson videos; `false` = newer effect
  that ships only a demo, so steps are the standard technique (see `technique_note`)
- `lessons[]` — per-lesson `transcript`, `transcript_source` (`wistia|whisper`), `role`
  (`demo|filming|editing|guide|reference`), `duration_sec`, `source_url`, `wistia_id`,
  `image_files`, `image_source_urls` (durable CDN urls)

## Notes
- `meta.schema_version` + `meta.generated` are stamped at the top of `effects.json`.
- Personal-study use of member content; keep private.
