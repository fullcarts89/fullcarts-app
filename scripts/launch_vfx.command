#!/bin/bash
cd "$(dirname "$0")/.."
PORT=8765
( sleep 2 && open "http://127.0.0.1:$PORT" ) >/dev/null 2>&1 &
echo "== Viral VFX running at http://127.0.0.1:$PORT  (close this window to stop) =="
exec ./.venv/bin/uvicorn vfx.web.app:app --host 127.0.0.1 --port "$PORT"
