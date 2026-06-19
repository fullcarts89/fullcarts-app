import argparse
from pathlib import Path
from vfx.db import RecipeStore
from vfx.ingest.vfxdata import ingest_all

DEFAULT_DB = Path.home() / ".vfx" / "vfx.db"
# Committed, enriched store (34 recipes) used as the default for end-user commands.
# Package-relative so it resolves no matter the caller's working directory.
ENRICHED_DB = str(Path(__file__).resolve().parent / "data" / "recipes.db")


def main():
    ap = argparse.ArgumentParser(prog="vfx")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ing = sub.add_parser("ingest-dataset")
    ing.add_argument("--db", default=str(DEFAULT_DB))
    ls = sub.add_parser("list")
    ls.add_argument("--db", default=str(DEFAULT_DB))
    en = sub.add_parser("enrich")
    en.add_argument("--db", default=str(DEFAULT_DB))
    en.add_argument("--with-vision", action="store_true")
    en.add_argument("--limit", type=int, default=None)
    rc = sub.add_parser("recommend")
    rc.add_argument("--equipment", default="")
    rc.add_argument("-k", type=int, default=3)
    rc.add_argument("--db", default=ENRICHED_DB)
    pl = sub.add_parser("plan")
    pl.add_argument("slug")
    pl.add_argument("--db", default=ENRICHED_DB)
    im = sub.add_parser("ingest-manual")
    im.add_argument("file")
    im.add_argument("--db", default=str(DEFAULT_DB))
    bd = sub.add_parser("build")
    bd.add_argument("slug", nargs="?")
    bd.add_argument("--manual", default=None, help="build straight from a manual file")
    bd.add_argument("--asset", action="append", default=[], metavar="NAME=PATH")
    bd.add_argument("--out", default=".")
    bd.add_argument("--name", default=None)
    bd.add_argument("--db", default=ENRICHED_DB)
    fin = sub.add_parser(
        "finish", help="drive CapCut's GUI-only steps via computer-use (macOS)")
    fin.add_argument("slug", nargs="?")
    fin.add_argument("--manual", default=None)
    fin.add_argument("--db", default=ENRICHED_DB)
    fin.add_argument("--max-steps", type=int, default=60)
    fin.add_argument("--yes", action="store_true",
                     help="auto-confirm each action (default: prompt before each)")
    fin.add_argument("--dry-run", action="store_true",
                     help="print the GUI task and exit (no API, no clicks)")
    args = ap.parse_args()

    if args.cmd == "ingest-manual":
        from vfx.ingest.manual_schema import load_manual
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        recipe = load_manual(args.file)
        RecipeStore(args.db).put(recipe)
        print(f"ingested: {recipe.slug} ({recipe.technique_primitive})")
        return

    if args.cmd == "build":
        from vfx.ingest.manual_schema import load_manual
        from vfx.capcut.compile import compile_timeline
        from vfx.capcut.draft import write_project
        if args.manual:
            recipe = load_manual(args.manual)
        elif args.slug:
            recipe = RecipeStore(args.db).get(args.slug)
            if recipe is None:
                raise SystemExit(f"no recipe: {args.slug}")
        else:
            raise SystemExit("provide a slug (with --db) or --manual FILE")
        assets = {}
        for pair in args.asset:
            if "=" not in pair:
                raise SystemExit(f"bad --asset (need NAME=PATH): {pair}")
            name, path = pair.split("=", 1)
            assets[name] = path
        res = compile_timeline(recipe, assets)
        name = args.name or recipe.slug
        dest = write_project(res.timeline, args.out, name)
        checklist = dest / "FINISH_BY_HAND.md"
        lines = [f"# Finish by hand - {recipe.title}", ""]
        lines += [f"- {n}" for n in res.manual_notes] or ["- (nothing - fully assembled)"]
        checklist.write_text("\n".join(lines), encoding="utf-8")
        print(f"project:   {dest}")
        print(f"checklist: {checklist}  ({len(res.manual_notes)} manual step(s))")
        return

    if args.cmd == "finish":
        from vfx.computer_use import build_task, gui_steps, reference_blocks
        if args.manual:
            from vfx.ingest.manual_schema import load_manual
            recipe = load_manual(args.manual)
        elif args.slug:
            recipe = RecipeStore(args.db).get(args.slug)
            if recipe is None:
                raise SystemExit(f"no recipe: {args.slug}")
        else:
            raise SystemExit("provide a slug (with --db) or --manual FILE")
        steps = gui_steps(recipe)
        task = build_task(recipe)
        refs = reference_blocks(recipe)
        if not steps:
            print("No GUI-only steps for this recipe — the file-writer covers it.")
            return
        print(f"GUI-only steps computer-use will perform ({len(steps)}):")
        for i, s in enumerate(steps, 1):
            print(f"  {i}. {s}")
        print(f"reference screenshots attached: {len(refs)}")
        for cap, path in refs:
            print(f"  - {cap} -> {path}")
        if args.dry_run:
            print("\n[dry-run] not launching. Open the built project in CapCut, then "
                  "re-run without --dry-run.")
            return
        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set — refusing to run (would spend money).")
        from vfx.computer_use import MacExecutor, run_task
        print("\n⚠️  Make sure the built project is OPEN in CapCut and visible.")
        print("    Computer-use will control your mouse/keyboard. Move mouse to a "
              "corner or press Ctrl-C to stop.\n")
        executor = MacExecutor()

        def _confirm(action) -> bool:
            if args.yes:
                return True
            ans = input(f"  perform [{action.kind} {action.x or ''},{action.y or ''} "
                        f"{action.text or ''}]? [y/N/q] ").strip().lower()
            if ans == "q":
                raise SystemExit("stopped by user")
            return ans == "y"

        res = run_task(task, executor, max_steps=args.max_steps,
                       confirm=_confirm, on_event=lambda m: print("   ", m),
                       reference_images=refs)
        print(f"\n{'✅ completed' if res.completed else '⛔ stopped'} after {res.steps} step(s).")
        return

    if args.cmd == "recommend":
        from vfx.recommender import top_recipes, feasibility_score
        from vfx.intake import Capabilities
        caps = Capabilities(equipment=[e for e in args.equipment.split(",") if e])
        store = RecipeStore(args.db)
        for r in top_recipes(store.all(), caps, k=args.k):
            print(f"{feasibility_score(r, caps):.2f}  {r.slug}  ({r.technique_primitive})")
        return

    if args.cmd == "plan":
        from vfx.capcut.checklist import build_filming_plan, build_checklist
        r = RecipeStore(args.db).get(args.slug)
        if r is None:
            raise SystemExit(f"no recipe: {args.slug}")
        print(build_filming_plan(r))
        print()
        print(build_checklist(r))
        return

    if args.cmd == "enrich":
        import os
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit(
                "ANTHROPIC_API_KEY is not set - refusing to run (would spend money).")
        from vfx.llm import LLM
        from vfx.ingest.enrich_llm import enrich_all
        from vfx_instructions.vfx_loader import VFXData
        Path(args.db).parent.mkdir(parents=True, exist_ok=True)
        d = VFXData()
        records = list(d)[: args.limit] if args.limit else list(d)
        store = RecipeStore(args.db)
        n = enrich_all(records, LLM(), store, with_vision=args.with_vision,
                       asset_resolver=d.asset_path)
        print(f"enriched {n} recipes -> {args.db}")
        return

    Path(args.db).parent.mkdir(parents=True, exist_ok=True)
    store = RecipeStore(args.db)
    if args.cmd == "ingest-dataset":
        n = ingest_all(store)
        print(f"ingested {n} recipes -> {args.db}")
    elif args.cmd == "list":
        for r in store.all():
            print(f"{r.slug:32} {r.technique_primitive:24} {r.difficulty:14} {r.gear}")


if __name__ == "__main__":
    main()
