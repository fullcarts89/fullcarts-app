import argparse
from pathlib import Path
from vfx.db import RecipeStore
from vfx.ingest.vfxdata import ingest_all

DEFAULT_DB = Path.home() / ".vfx" / "vfx.db"


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
    args = ap.parse_args()

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
