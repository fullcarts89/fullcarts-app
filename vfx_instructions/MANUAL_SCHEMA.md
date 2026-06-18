# VFX Manual Schema

A **manual** is the machine-executable recreation recipe the VFX tool consumes. One
file per effect lives in `manuals/<id>.json`; `manuals/index.json` is the catalog the
recommender queries. Manuals are parsed with **zero AI inference** — every field is
either a literal value or drawn from a controlled vocabulary below.

This complements the raw evidence records in `external_sources.json` (narration,
frames, source metadata). A manual is the *authored* recipe distilled from a record.

## File layout

```
manuals/
  index.json              # catalog: one row per manual (id, technique_primitive, gear, ...)
  <id>.json               # the manual itself
```

## Top-level fields

| field | type | notes |
|---|---|---|
| `id` | str | matches the filename (`<id>.json`) and the source record slug |
| `schema_version` | int | currently `1` |
| `technique_primitive` | enum | controlled vocab (see below) |
| `title` | str | human title |
| `difficulty` | enum | `beginner` \| `intermediate` \| `advanced` |
| `aspect_ratio` | str | e.g. `9:16` |
| `gear_required` | [str] | e.g. `tripod`, `lighting`, `camera_operator` |
| `props_required` | [str] | physical props |
| `result_description` | str | what the finished effect looks like |
| `source` / `source_url` | str | attribution |
| `is_ai_generated` | bool | true if it needs a generative tool |
| `tool` | str | `CapCut`, `Higgsfield (AI)`, … |
| `inputs` | [Input] | ordered clips/photos to capture (below) |
| `edit_steps` | [Step] | ordered edit operations (below) |
| `ai_generation` | [AIStep] | present only for AI effects (below) |
| `result` | obj | `{description, success_criteria:[str]}` |
| `narration_transcript` | str | prose backup (not executed) |
| `frames` | obj | `{demo:[path], editing:[path]}` reference stills |
| `draft` / `needs_authoring` | bool | present on auto-emitted drafts only |

## `inputs[]`

```json
{
  "name": "pointing_clip",
  "what_to_film": "Sit, point to where the clone will be, then step out.",
  "capture_requirements": {"locked_off": true, "green_screen": false},
  "acceptance_checks": ["camera_locked_off", "min_duration"],
  "variance_tolerance": {"camera_shift_px": 8, "min_seconds": 2}
}
```

## `edit_steps[]`

```json
{"action": "remove_background", "target": "top clip",
 "capcut_feature": "Remove Background → Auto Removal",
 "params": {"mode": "auto"}, "channel": "ui"}
```

Every step is tagged with a **channel** so the tool knows how deterministic it is:

- `structural` — auto-assemblable (import / overlay / duplicate / layer order)
- `ui` — a named CapCut control the tool drives (Mask, Remove Background, Opacity…)
- `taste` — subjective, no fixed value (timing nudges, color choices)
- `ai_gen` — produced by an external generative tool

`params` hold exact values when known. Numeric params are read from the source video
where the creator shows them on screen (e.g. `phone_hologram` opacity `50`, read off
the on-screen "50%"). Where no value is shown, the step stays `ui`/`taste` with a note
rather than a guessed number.

## `ai_generation[]` (AI effects)

For effects that need a generative model, steps map to an MCP tool. Higgsfield is wired
to its MCP server; the exact prompt is authored at runtime (creators gate their prompts).

```json
{"provider": "higgsfield", "mcp_server": "66e733f1-...", "operation": "image_to_video",
 "tool": "generate_video", "inputs": ["selfie_photo"], "motion": "Aerial Pullback",
 "prompt_strategy": "author at runtime", "settings": {}, "channel": "ai_gen"}
```

## Controlled vocabularies

The single source of truth is `manual_builder.py`:

- `TECHNIQUE_PRIMITIVES` — `overlay_bg_removal_clone`, `chroma_key`, `text_reveal`,
  `keyframe_motion`, `clean_plate_mask_reveal`, `match_cut`, `other`
- `ACTIONS` — `import`, `overlay`, `position`, `duplicate`, `remove_background`,
  `chroma_key`, `mask`, `keyframe`, `text`, `transform`, `filter`, `split`, `speed`,
  `reverse`, `trim`, `opacity`, `audio`, `ai_generate`
- `CHANNELS` — `structural`, `ui`, `taste`, `ai_gen`

## Tooling

```bash
python validate_manuals.py            # validate all manuals against the vocabs
python -c "from vfx_loader import Manuals; m=Manuals(); print(m.recipe('phone_hologram'))"
```

New videos ingested via `ingest_video.py` automatically get a **draft** manual
(`draft: true`, `needs_authoring: true`) and `index.json` is rebuilt — so every future
idea lands in this format, ready for a human/Claude authoring pass.
