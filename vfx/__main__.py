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
    args = ap.parse_args()

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
