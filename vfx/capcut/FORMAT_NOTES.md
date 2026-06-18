# CapCut Desktop draft format — reverse-engineering notes

Reverse-engineered from a golden sample created in **CapCut Desktop v8.6.0 (macOS)**
— a 2-clip project with one clip on an overlay track. The sample skeleton is
bundled at `vfx/capcut/templates/draft_skeleton/`.

> ⚠️ Undocumented, version-specific format. Pin the CapCut version; re-capture a
> golden sample if CapCut changes the schema. The writer uses **clone-and-rewrite**
> (copy the skeleton, overwrite the meaningful fields) so the hundreds of default
> fields CapCut expects survive untouched.

## Folder layout (project = a folder named like `0617 (2)`)
```
<project>/
  draft_info.json            # THE timeline (canvas, materials, tracks, segments)
  draft_meta_info.json       # project id/name/paths/duration + media manifest
  draft_virtual_store.json, key_value.json, draft_settings,
  draft_agency_config.json, draft_biz_config.json, timeline_layout.json
  Timelines/
    project.json
    <UUID>/draft_info.json   # a copy of the root draft_info.json
    <UUID>/draft.extra, attachment/patch/{patch,mini_draft}.json
```
The root `draft_info.json` and `Timelines/<UUID>/draft_info.json` carry the **same**
timeline content — write both.

## Units & canvas
- **Time is in microseconds (µs).** e.g. `11866666` = 11.866666 s; fps `30.0`.
- `canvas_config`: `{ratio, width, height, background}` — sample is `1080×1920` portrait.

## materials (parallel arrays, one entry per clip)
- `materials.videos[]`: `{id(UUID), type:"video", path(ABSOLUTE), material_name, width, height, duration(µs), ...}`
- Each clip also needs **one entry in each** of these helper arrays, referenced by the
  segment's `extra_material_refs` (6 ids per segment):
  `speeds`, `placeholder_infos`, `canvases`, `sound_channel_mappings`,
  `material_colors`, `vocal_separations`.

## tracks & segments  (layering = separate tracks)
- `tracks[]`: each `{id(UUID), type:"video", attribute:0, segments:[...]}`.
  **One segment per track here** — the overlay is a *second track*, not a second
  segment. Track order in the array = stacking order (lower track index = below).
- `segment` (key fields; the rest are defaults to clone verbatim):
  - `id` (UUID), `material_id` → `videos[].id`
  - `target_timerange` `{start, duration}` — position on the **timeline** (µs)
  - `source_timerange` `{start, duration}` — in/out within the **source** media (µs)
  - `extra_material_refs` — the 6 helper-material ids for this clip
  - `render_index` — increments per stacked layer (0, 1, ...)
  - `clip` — transform `{scale, rotation, transform, flip, alpha}` (defaults = identity)
  - `speed` 1.0, `volume` 1.0, `visible` true

## draft_meta_info.json
- `draft_id` (UUID), `draft_name`, `draft_fold_path` (absolute project folder),
  `draft_root_path` (parent), `tm_draft_create`/`tm_draft_modified` (µs epoch),
  `tm_duration` (µs), and `draft_materials` (a manifest of the media: `file_Path`,
  `duration`, `extra_info`=filename, ...). Must be consistent with `draft_info.json`.

## Writer strategy (clone-and-rewrite)
1. Copy `draft_skeleton/` → new project folder.
2. Build `draft_info.json`: clone a template segment + the 7 materials (video + 6
   helpers) per clip, assign fresh UUIDs, set paths/dims/durations/timeranges,
   assemble one track per layer with incrementing `render_index`. Write to root **and**
   `Timelines/<UUID>/draft_info.json`.
3. Patch `draft_meta_info.json`: new `draft_id`, `draft_name`, `*_path`s,
   `tm_*` timestamps, `tm_duration`, `draft_materials` manifest.
4. **Validation in CI is structural only** (no CapCut here): valid JSON, N videos,
   M tracks, correct timeranges, unique ids, refs resolve. The real "does CapCut
   open it" test runs on the user's Mac.
