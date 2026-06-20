#!/bin/bash
set -e
cd "$(dirname "$0")/.."
echo "== Installing Viral VFX tool =="
if command -v brew >/dev/null 2>&1; then brew install ffmpeg poppler || true; else
  echo "(!) Homebrew not found — install ffmpeg + poppler manually if QA/PDF features are needed."; fi
python3 -m venv .venv
./.venv/bin/pip install --upgrade pip
./.venv/bin/pip install -e .
echo "== Done. Close this window, then double-click launch_vfx.command =="
