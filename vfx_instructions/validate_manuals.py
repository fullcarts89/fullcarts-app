#!/usr/bin/env python3
"""Validate VFX manuals against the controlled vocabularies in manual_builder.py.

    python validate_manuals.py            # validate all manuals/*.json
    python validate_manuals.py <file ...> # validate specific files

Exits non-zero if any ERROR is found (drafts are allowed to be incomplete and
only emit WARNINGs). Run before committing new/edited manuals.
"""
import json, os, sys
import manual_builder as mb

REQUIRED = ["id", "technique_primitive", "title", "difficulty", "inputs", "edit_steps"]
DIFFICULTIES = {"beginner", "intermediate", "advanced", "foundation"}


def validate(path):
    errs, warns = [], []
    try:
        m = json.load(open(path))
    except Exception as e:
        return ["cannot parse JSON: %s" % e], []
    draft = bool(m.get("draft"))
    mtype = m.get("manual_type", "effect")
    if mtype not in mb.MANUAL_TYPES:
        errs.append("manual_type '%s' not in %s" % (mtype, sorted(mb.MANUAL_TYPES)))

    # reference / deep_dive / stub entries are not full recipes — only need id + title
    if mtype != "effect":
        for k in ("id", "title"):
            if not m.get(k):
                errs.append("missing/empty: %s" % k)
        if m.get("technique_primitive") and m["technique_primitive"] not in mb.TECHNIQUE_PRIMITIVES:
            errs.append("technique_primitive '%s' not in vocab" % m["technique_primitive"])
        if os.path.basename(path) != m.get("id", "") + ".json":
            warns.append("filename does not match id '%s'" % m.get("id"))
        return errs, warns

    for k in REQUIRED:
        if k not in m or m[k] in (None, "", [], {}):
            (warns if (draft and k in ("inputs", "edit_steps")) else errs).append("missing/empty: %s" % k)

    tp = m.get("technique_primitive")
    if tp and tp not in mb.TECHNIQUE_PRIMITIVES:
        errs.append("technique_primitive '%s' not in vocab" % tp)
    if m.get("difficulty") and m["difficulty"] not in DIFFICULTIES:
        errs.append("difficulty '%s' not in %s" % (m["difficulty"], sorted(DIFFICULTIES)))

    if os.path.basename(path) != m.get("id", "") + ".json":
        warns.append("filename does not match id '%s'" % m.get("id"))

    for i, s in enumerate(m.get("edit_steps", []) or []):
        loc = "edit_steps[%d]" % i
        if s.get("action") not in mb.ACTIONS:
            errs.append("%s: action '%s' not in vocab" % (loc, s.get("action")))
        if s.get("channel") not in mb.CHANNELS:
            errs.append("%s: channel '%s' not in vocab" % (loc, s.get("channel")))

    for i, inp in enumerate(m.get("inputs", []) or []):
        if not inp.get("name") or not inp.get("what_to_film"):
            errs.append("inputs[%d]: needs name + what_to_film" % i)

    if m.get("is_ai_generated") and not m.get("ai_generation"):
        warns.append("is_ai_generated but no ai_generation block")
    for i, a in enumerate(m.get("ai_generation", []) or []):
        if a.get("channel") not in mb.CHANNELS:
            warns.append("ai_generation[%d]: channel '%s' not in vocab" % (i, a.get("channel")))

    return errs, warns


def main():
    files = sys.argv[1:] or sorted(
        os.path.join(mb.MANUALS_DIR, f) for f in os.listdir(mb.MANUALS_DIR)
        if f.endswith(".json") and f != "index.json")
    total_err = 0
    for p in files:
        errs, warns = validate(p)
        total_err += len(errs)
        name = os.path.basename(p)
        if not errs and not warns:
            print("  ok    %s" % name)
        else:
            for e in errs:  print("  ERROR %s: %s" % (name, e))
            for w in warns: print("  warn  %s: %s" % (name, w))
    print("\n%d file(s), %d error(s)" % (len(files), total_err))
    sys.exit(1 if total_err else 0)


if __name__ == "__main__":
    main()
