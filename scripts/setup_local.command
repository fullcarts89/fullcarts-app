#!/bin/bash
# One-time setup for the local VFX morph generator. Double-click this once.
set -e
cd "$(dirname "$0")/.."
echo "== One-time setup for the morph generator =="
echo
echo "[1/2] Fetching the draft engine..."
mkdir -p vendor
if [ ! -d vendor/CapCutAPI/pyJianYingDraft ]; then
  git clone --depth 1 https://github.com/ashreo/CapCutAPI vendor/CapCutAPI
else
  echo "    already present."
fi
echo "[2/2] Installing Python bits..."
if [ ! -d .venv ]; then python3 -m venv .venv; fi
./.venv/bin/pip install --quiet --upgrade pip
./.venv/bin/pip install --quiet imageio pillow pyyaml
echo
echo "== Done. Put two clips named current.mov and old.mov in the vfx_assets folder,"
echo "   then double-click make_morph.command. =="
mkdir -p vfx_assets
open vfx_assets 2>/dev/null || true
echo
read -p "Press Return to close."
