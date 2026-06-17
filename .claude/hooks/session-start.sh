#!/bin/bash
set -euo pipefail

# Only run in Claude Code on the web (remote) containers, which start fresh
# each session and don't persist apt-installed system packages.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Idempotent: skip the install if ffmpeg is already on PATH.
if command -v ffmpeg >/dev/null 2>&1; then
  exit 0
fi

# Non-interactive apt install of ffmpeg.
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -qq
sudo apt-get install -y ffmpeg
