from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import os
import joblib
import pandas as pd
from datetime import datetime, timedelta, timezone
from app.db import get_db, fetch_records
from app.core.security import get_current_user

router = APIRouter(tags=["Facilities & Occupancy"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "ml", "models")
if not os.path.exists(MODEL_DIR):
    MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "ml", "models")

def get_active_source(db):
    setting = db.settings.find_one({"key": "data_source"})
    return setting.get("value", "simulated") if setting else "simulated"

@router.get("/facilities")
def get_facilities(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = get_active_source(db)
    facilities = fetch_records(db.facilities, sort_key="facility_id", reverse=False)

    for f in facilities:
        bid = f.get("building_id", "B001")
        latest_occ = fetch_records(db.occupancy_data, query={"building_id": bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
        if not latest_occ:
            latest_occ = fetch_records(db.occupancy_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=1)

        occ_rec = latest_occ[0] if latest_occ else None
        cap = f.get("capacity", 100) or 100
        count = occ_rec["occupancy_count"] if (occ_rec and "occupancy_count" in occ_rec) else (int(occ_rec.get("value", 0)) if occ_rec else 25)

        if occ_rec and "occupancy_rate" in occ_rec:
            rate = round(occ_rec["occupancy_rate"] * 100, 1)
        else:
            rate = round((count / cap) * 100, 1)

        if rate >= 90.0:
            status = "critical"
            rec_action = "High capacity alert - consider overflow scheduling or restricting further entries immediately."
        elif rate >= 75.0:
            status = "warning"
            rec_action = "Approaching capacity - consider overflow scheduling or staggering space bookings."
        else:
            status = "normal"
            rec_action = None

        f["current_occupancy_count"] = count
        f["current_occupancy_rate"] = rate
        f["status"] = status
        f["recommended_action"] = rec_action

    return facilities

FACILITY_BUILDING_MAP = {
    "F001": "B001",
    "F002": "B004",
    "F003": "B010",
    "F004": "B008",
    "F005": "B009"
}

@router.get("/occupancy")
def get_campus_occupancy(
    building_id: Optional[str] = None,
    facility_id: Optional[str] = None,
    limit: int = 72,
    source: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = source or get_active_source(db)
    query = {"source": active_src} if active_src else {}

    target_bid = building_id or FACILITY_BUILDING_MAP.get(facility_id) or facility_id
    if target_bid:
        query["building_id"] = target_bid

    records = fetch_records(db.occupancy_data, query=query, sort_key="timestamp", reverse=True, limit=limit)
    if not records and target_bid:
        records = fetch_records(db.occupancy_data, query={"building_id": target_bid}, sort_key="timestamp", reverse=True, limit=limit)

    result = records[::-1]
    for r in result:
        r["value"] = r.get("occupancy_count") if "occupancy_count" in r else r.get("value", 0)

    return result

@router.get("/occupancy/predict/{identifier}")
def predict_occupancy_load(identifier: str, hours: int = 24, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    target_bid = FACILITY_BUILDING_MAP.get(identifier, identifier)
    active_src = get_active_source(db)
    records = fetch_records(db.occupancy_data, query={"building_id": target_bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
    if not records:
        records = fetch_records(db.occupancy_data, query={"building_id": target_bid}, sort_key="timestamp", reverse=True, limit=1)

    last_val = records[0]["occupancy_count"] if (records and "occupancy_count" in records[0]) else (records[0]["value"] if records else 30.0)

    b_codes = {"B001": 0, "B002": 1, "B003": 2, "B004": 3, "B005": 4, "B006": 5, "B007": 6, "B008": 7, "B009": 8, "B010": 9}
    b_code = b_codes.get(target_bid, 0)

    model_path = os.path.join(MODEL_DIR, "occupancy_forecaster.joblib")
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
            pattern_mult = 1.7 if 9 <= hr <= 17 and not is_wknd else 0.3
            pred_val = (last_val * 0.3) + (50.0 * pattern_mult * 0.7)

        pred_val = max(0.0, round(pred_val, 1))
        curr_val = pred_val

        predictions.append({
            "timestamp": future_dt.isoformat(),
            "predicted_occupancy": pred_val,
            "unit": "people"
        })

    return {
        "building_id": target_bid,
        "facility_id": identifier,
        "hours_ahead": hours,
        "predictions": predictions
    }
