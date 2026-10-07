#!/usr/bin/env bash
set -e

echo "=========================================================================="
echo "         AI Digital Twin for Smart Campus - Setup Script (POSIX)          "
echo "=========================================================================="

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3.10+ is required but not installed."
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "[ERROR] Node 18+ is required but not installed."
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "[SETUP] Creating Python Virtual Environment (venv)..."
    python3 -m venv venv
fi

source venv/bin/activate
echo "[SETUP] Installing Python requirements..."
pip install --upgrade pip
pip install -r backend/requirements.txt

echo "[SETUP] Installing frontend dependencies..."
(cd frontend && npm install)

if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
fi

if [ ! -f "frontend/.env" ]; then
    echo "VITE_API_URL=http://localhost:8000/api" > frontend/.env
fi

echo "[SETUP] Validating MongoDB Atlas..."
python3 scripts/test_atlas.py || echo "[NOTICE] Atlas ping unverified. You may set USE_EMBEDDED_DB=true in backend/.env for offline mode."

echo "[SETUP] Seeding database and training ML models..."
python3 database/seed_data.py
python3 ml/pipeline.py

echo "=========================================================================="
echo "          SETUP COMPLETED SUCCESSFULLY! Ready to Start!                   "
echo "=========================================================================="
echo "Run 'scripts/start.sh' to launch application servers."
