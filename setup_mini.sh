#!/bin/bash
# One-time setup on the Mac mini. Usage: GOOGLE_API_KEY=... ./setup_mini.sh   (key is never written to this folder)
set -e
cd "$(dirname "$0")"
PY=$(command -v python3.12 || command -v python3.11 || command -v python3)
$PY -m venv .venv && .venv/bin/pip install -q -r requirements.txt
.venv/bin/python -c "import fastapi, google.genai; print('deps ok')"
[ -n "$GOOGLE_API_KEY" ] || echo "NOTE: export GOOGLE_API_KEY before running the server (server.py reads it from the environment)."
echo "Run: GOOGLE_API_KEY=... .venv/bin/uvicorn server:app --port 8000   then open http://localhost:8000"
