#!/usr/bin/env python3
"""Generate a CapCut "package morph" draft directly into the CapCut drafts folder.

This is the local generator: it builds the morph project (clip A -> transition ->
clip B with a scale "grow" + a Typewriter year label) from two clips, writing a
complete, openable CapCut draft. No cloud round-trip, no zip — it lands straight
in your CapCut Projects.

It uses the open-source pyJianYingDraft engine (from the CapCutAPI repo). Run
``scripts/setup_local.command`` once to fetch that engine; this script locates it
automatically.

Usage:
    python3 scripts/build_morph.py \
        --current /path/current.mov --old /path/old.mov \
        --name KRAFT_MORPH --transition Dissolve --year 2022

Then quit + reopen CapCut; the project appears in your drafts.
"""
import argparse
import json
import os
import shutil
import sys
from pathlib import Path

# --- locate the pyJianYingDraft engine (from a local CapCutAPI clone) ----------
_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "vendor" / "CapCutAPI",
    Path.home() / "fullcarts-vfx" / "CapCutAPI",
    Path(os.environ.get("CAPCUTAPI_DIR", "")) if os.environ.get("CAPCUTAPI_DIR") else None,
]


def _find_engine():
    for c in _CANDIDATES:
        if c and (c / "pyJianYingDraft").is_dir():
            return c
    raise SystemExit(
        "Could not find the CapCutAPI engine. Run scripts/setup_local.command first "
        "(it clones it into vendor/CapCutAPI).")


def _default_capcut_drafts() -> Path:
    return (Path.home() / "Movies" / "CapCut" / "User Data" / "Projects"
            / "com.lveditor.draft")


def main():
    ap = argparse.ArgumentParser(description="Build a CapCut package-morph draft.")
    ap.add_argument("--current", required=True, help="current/smaller clip (clip A)")
    ap.add_argument("--old", required=True, help="older/bigger clip or photo (clip B)")
    ap.add_argument("--name", default="PACKAGE_MORPH", help="project name in CapCut")
    ap.add_argument("--transition", default="Dissolve",
                    help="transition between clips (e.g. Dissolve, Mix, Stretch, Pull_in, Glitch)")
    ap.add_argument("--year", default="2022", help="text label that types on at the morph")
    ap.add_argument("--clip-seconds", type=float, default=2.0, help="length of each clip")
    ap.add_argument("--grow", type=float, default=1.30,
                    help="clip B start scale (settles to 1.0) — the 'grow'")
    ap.add_argument("--out", default=None,
                    help="output folder (default: your CapCut drafts folder)")
    args = ap.parse_args()

    engine = _find_engine()
    sys.path.insert(0, str(engine))
    import pyJianYingDraft as draft
    from pyJianYingDraft import CapCut_Transition_type, CapCut_Text_intro, trange
    from pyJianYingDraft.keyframe import Keyframe_property

    try:
        transition = CapCut_Transition_type[args.transition]
    except KeyError:
        names = [m.name for m in CapCut_Transition_type]
        raise SystemExit(f"Unknown transition {args.transition!r}. Options include: "
                         + ", ".join(sorted(names)[:40]) + " …")

    cur = Path(args.current).expanduser().resolve()
    old = Path(args.old).expanduser().resolve()
    for p in (cur, old):
        if not p.is_file():
            raise SystemExit(f"asset not found: {p}")

    out_root = Path(args.out).expanduser() if args.out else _default_capcut_drafts()
    out = out_root / args.name
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(engine / "template", out)

    secs = args.clip_seconds
    s = draft.Script_file(1080, 1920)
    s.add_track(draft.Track_type.video, "main")
    s.add_track(draft.Track_type.text, "labels")
    matA = draft.Video_material("video", path=str(cur), width=1080, height=1920, duration=secs + 2)
    matB = draft.Video_material("video", path=str(old), width=1080, height=1920, duration=secs + 2)
    segA = draft.Video_segment(matA, trange("0s", f"{secs}s"), source_timerange=trange("0s", f"{secs}s"))
    segB = draft.Video_segment(matB, trange(f"{secs}s", f"{secs}s"), source_timerange=trange("0s", f"{secs}s"))
    segA.add_transition(transition, duration="0.6s")           # on clip A -> bridges A->B
    segB.add_keyframe(Keyframe_property.uniform_scale, "0s", args.grow)
    segB.add_keyframe(Keyframe_property.uniform_scale, "0.5s", 1.0)
    s.add_segment(segA, "main")
    s.add_segment(segB, "main")
    txt = draft.Text_segment(args.year, trange(f"{secs}s", "1.5s"))
    txt.add_animation(CapCut_Text_intro.Typewriter)
    s.add_segment(txt, "labels")

    # bundle media inside the project and point the draft at it (no relink)
    media = out / "media"
    media.mkdir(exist_ok=True)
    shutil.copy(cur, media / cur.name)
    shutil.copy(old, media / old.name)

    di = out / "draft_info.json"
    s.dump(str(di))
    data = di.read_text()
    data = data.replace(str(cur.parent), str(media)).replace(str(old.parent), str(media))
    di.write_text(data)

    mp = out / "draft_meta_info.json"
    meta = json.loads(mp.read_text())
    meta["draft_name"] = args.name
    mp.write_text(json.dumps(meta))

    json.loads(di.read_text())  # validate
    print(f"✅ Built '{args.name}' -> {out}")
    print("   Quit CapCut (Cmd+Q) and reopen — it appears in your Projects.")


if __name__ == "__main__":
    main()
