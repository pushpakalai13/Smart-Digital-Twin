#!/usr/bin/env bash

echo "=========================================================================="
echo "       Starting AI Digital Twin for Smart Campus (Backend & Frontend)     "
echo "=========================================================================="

if [ -d "venv" ]; then
    source venv/bin/activate
fi

trap 'kill 0' EXIT

echo "[START] Starting FastAPI Backend..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend &

echo "[START] Starting React Frontend..."
(cd frontend && npm run dev) &

wait
