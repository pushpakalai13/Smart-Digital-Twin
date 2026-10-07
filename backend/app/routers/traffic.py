from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta, timezone
from app.db import get_db, fetch_records
from app.core.security import get_current_user

router = APIRouter(tags=["Traffic & Parking"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
if not os.path.exists(MODEL_DIR):
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")

def get_active_source(db):
    setting = db.settings.find_one({"key": "data_source"})
    return setting.get("value", "simulated") if setting else "simulated"

@router.get("/traffic")
def get_traffic_data(
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

    records = fetch_records(db.traffic_data, query=query, sort_key="timestamp", reverse=True, limit=limit)
    if not records and building_id:
        records = fetch_records(db.traffic_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=limit)
    return records[::-1]

@router.get("/traffic/{building_id}")
def get_building_traffic(
    building_id: str,
    limit: int = 168,
    source: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = source or get_active_source(db)
    records = fetch_records(db.traffic_data, query={"building_id": building_id, "source": active_src}, sort_key="timestamp", reverse=True, limit=limit)
    if not records:
        records = fetch_records(db.traffic_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=limit)
    return records[::-1]

@router.get("/traffic/predict/{building_id}")
@router.get("/traffic/predict")
@router.get("/predict/traffic")
def predict_traffic_flow(
    building_id: Optional[str] = None,
    hours: int = 24,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    target_bid = building_id or "B001"
    active_src = get_active_source(db)
    records = fetch_records(db.traffic_data, query={"building_id": target_bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
    if not records:
        records = fetch_records(db.traffic_data, query={"building_id": target_bid}, sort_key="timestamp", reverse=True, limit=1)

    last_val = records[0]["value"] if records else 85.0

    b_codes = {"B001": 0, "B002": 1, "B003": 2, "B004": 3, "B005": 4, "B006": 5, "B007": 6, "B008": 7, "B009": 8, "B010": 9}
    b_code = b_codes.get(target_bid, 0)

    model_path = os.path.join(MODEL_DIR, "traffic_forecaster.joblib")
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
            if is_wknd:
                val = 20 if 10 <= hr <= 18 else 5
            else:
                val = 140 if 8 <= hr <= 10 or 17 <= hr <= 19 else (45 if 10 < hr < 17 else 10)
            pred_val = (curr_val * 0.3) + (val * 0.7)

        pred_val = max(5.0, round(pred_val, 1))
        curr_val = pred_val

        predictions.append({
            "timestamp": future_dt.isoformat(),
            "predicted_vehicles": pred_val,
            "predicted_vehicle_count": pred_val,
            "congestion_level": "high" if pred_val > 100 else ("medium" if pred_val > 40 else "low"),
            "unit": "vehicles/hr"
        })

    return {
        "building_id": target_bid,
        "hours_ahead": hours,
        "predictions": predictions
    }

@router.get("/parking")
def get_parking_status(limit: int = 48, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = get_active_source(db)
    records = fetch_records(db.parking_data, query={"source": active_src}, sort_key="timestamp", reverse=True, limit=limit)
    if not records:
        records = fetch_records(db.parking_data, sort_key="timestamp", reverse=True, limit=limit)
    return records[::-1]
