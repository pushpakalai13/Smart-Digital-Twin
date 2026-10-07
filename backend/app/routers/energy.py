from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta, timezone
from app.db import get_db, fetch_records
from app.core.security import get_current_user

router = APIRouter(prefix="/energy", tags=["Energy"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
if not os.path.exists(MODEL_DIR):
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")

def get_active_source(db):
    setting = db.settings.find_one({"key": "data_source"})
    return setting.get("value", "simulated") if setting else "simulated"

@router.get("")
def get_energy_data(
    building_id: Optional[str] = None,
    limit: int = Query(168, ge=1, le=2000),
    source: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = source or get_active_source(db)
    query = {}
    if building_id:
        query["building_id"] = building_id
    if active_src:
        query["source"] = active_src

    records = fetch_records(db.energy_data, query=query, sort_key="timestamp", reverse=True, limit=limit)
    if not records and building_id:
        records = fetch_records(db.energy_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=limit)
    return records[::-1]

@router.get("/predict/{building_id}")
def predict_energy_load(building_id: str, hours: int = 24, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = get_active_source(db)
    records = fetch_records(db.energy_data, query={"building_id": building_id, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
    if not records:
        records = fetch_records(db.energy_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=1)

    last_val = records[0]["value"] if records else 150.0

    b_codes = {"B001": 0, "B002": 1, "B003": 2, "B004": 3, "B005": 4, "B006": 5, "B007": 6, "B008": 7, "B009": 8, "B010": 9}
    b_code = b_codes.get(building_id, 0)

    model_path = os.path.join(MODEL_DIR, "energy_forecaster.joblib")
    model = None
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
        except Exception:
            pass

    predictions = []
    now = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    curr_val = last_val

    for i in range(1, hours + 1):
        future_dt = now + timedelta(hours=i)
        hr = future_dt.hour
        dow = future_dt.weekday()
        mo = future_dt.month
        is_wknd = 1 if dow >= 5 else 0

        if model is not None:
            X_input = pd.DataFrame([{
                "hour": hr,
                "dayofweek": dow,
                "month": mo,
                "is_weekend": is_wknd,
                "b_code": b_code,
                "lag_1": curr_val
            }])
            pred_val = float(model.predict(X_input)[0])
        else:
            pattern_mult = 1.6 if 8 <= hr <= 18 and not is_wknd else 0.7
            pred_val = (last_val * 0.4) + (100.0 * pattern_mult * 0.6)

        pred_val = max(10.0, round(pred_val, 2))
        curr_val = pred_val

        predictions.append({
            "timestamp": future_dt.isoformat(),
            "predicted_kwh": pred_val,
            "unit": "kWh"
        })

    return {
        "building_id": building_id,
        "hours_ahead": hours,
        "predictions": predictions
    }

@router.get("/{building_id}")
def get_building_energy(building_id: str, limit: int = 168, source: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = source or get_active_source(db)
    records = fetch_records(db.energy_data, query={"building_id": building_id, "source": active_src}, sort_key="timestamp", reverse=True, limit=limit)
    if not records:
        records = fetch_records(db.energy_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=limit)
    return records[::-1]
