#!/bin/bash
# Build the morph video into CapCut. Double-click this whenever you want a fresh build.
set -e
cd "$(dirname "$0")/.."
echo "== Building your morph =="
echo "[1/3] Getting the latest version..."
git pull --quiet --no-rebase 2>/dev/null || echo "    (offline or no updates — using local version)"
ASSETS="$PWD/vfx_assets"
CUR="$ASSETS/current.mov"; OLD="$ASSETS/old.mov"
if [ ! -f "$CUR" ] || [ ! -f "$OLD" ]; then
  echo
  echo "!! Put your two clips in this folder, named exactly current.mov and old.mov:"
  echo "   $ASSETS"
  mkdir -p "$ASSETS"; open "$ASSETS" 2>/dev/null || true
  read -p "Press Return to close."; exit 1
fi
echo "[2/3] Generating the CapCut project..."
# settings.txt (optional) can hold: TRANSITION=Dissolve / YEAR=2022 / NAME=PACKAGE_MORPH
TRANSITION=Dissolve; YEAR=2022; NAME=PACKAGE_MORPH
[ -f vfx_assets/settings.txt ] && source vfx_assets/settings.txt
CAPCUTAPI_DIR="$PWD/vendor/CapCutAPI" ./.venv/bin/python scripts/build_morph.py \
  --current "$CUR" --old "$OLD" --name "$NAME" --transition "$TRANSITION" --year "$YEAR"
echo "[3/3] Done."
echo
echo "== Quit CapCut (Cmd+Q) and reopen it. Open the '$NAME' project. =="
read -p "Press Return to close."
