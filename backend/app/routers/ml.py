import os
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.db import get_db
from app.core.security import require_admin, get_current_user
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.pipeline import run_ml_pipeline

router = APIRouter(prefix="/ml", tags=["Machine Learning Pipeline"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")

_is_training = False

def background_retrain_task(source: str):
    global _is_training
    _is_training = True
    try:
        run_ml_pipeline(source=source)
    finally:
        _is_training = False

@router.post("/retrain")
def trigger_retrain(
    background_tasks: BackgroundTasks,
    source: str = "simulated",
    current_user: dict = Depends(require_admin)
):
    global _is_training
    if _is_training:
        return {"status": "in_progress", "message": "ML training pipeline is already running in background."}

    background_tasks.add_task(background_retrain_task, source)
    return {
        "status": "started",
        "message": f"ML model training pipeline triggered in background for source '{source}'."
    }

@router.get("/status")
def get_ml_status(current_user: dict = Depends(get_current_user)):
    global _is_training

    metrics_data = {}
    if os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r") as f:
                metrics_data = json.load(f)
        except Exception:
            pass

    return {
        "is_training": _is_training,
        "last_trained": metrics_data.get("last_trained", None),
        "active_source": metrics_data.get("source", "simulated"),
        "models": {
            "energy": metrics_data.get("energy"),
            "water": metrics_data.get("water"),
            "traffic": metrics_data.get("traffic")
        }
    }
