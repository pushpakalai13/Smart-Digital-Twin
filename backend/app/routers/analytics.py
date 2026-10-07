from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.db import get_db, fetch_records
from app.core.security import get_current_user

router = APIRouter(tags=["Analytics, Anomalies & Recommendations"])

@router.get("/predictions")
def get_predictions(
    prediction_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    query = {}
    if prediction_type:
        query["prediction_type"] = prediction_type

    records = fetch_records(db.predictions, query=query, sort_key="created_at", reverse=True, limit=limit)
    return records

@router.get("/anomalies")
def get_anomalies(
    building_id: Optional[str] = None,
    metric: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    query = {}
    if building_id:
        query["building_id"] = building_id
    if metric:
        query["metric"] = metric

    records = fetch_records(db.anomalies, query=query, sort_key="timestamp", reverse=True, limit=limit)
    return records

@router.get("/recommendations")
def get_recommendations(
    building_id: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    query = {}
    if building_id:
        query["building_id"] = building_id
    if category:
        query["category"] = category

    recs = fetch_records(db.recommendations, query=query, sort_key="created_at", reverse=True)
    return recs

@router.get("/analytics")
def get_cross_resource_analytics(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    buildings = fetch_records(db.buildings, sort_key="building_id", reverse=False)
    comparison = []

    for b in buildings:
        bid = b["building_id"]
        latest_e = fetch_records(db.energy_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=24)
        latest_w = fetch_records(db.water_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=24)
        
        sum_e = sum([item.get("value", 0) for item in latest_e])
        sum_w = sum([item.get("value", 0) for item in latest_w])

        comparison.append({
            "building_id": bid,
            "building_name": b["name"],
            "category": b["category"],
            "area_sqft": b["area_sqft"],
            "energy_kwh_24h": round(sum_e, 1),
            "water_litres_24h": round(sum_w, 1),
            "energy_intensity": round(sum_e / max(1, b["area_sqft"] / 1000.0), 2),
            "water_intensity": round(sum_w / max(1, b["capacity"]), 2)
        })

    rankings = sorted(comparison, key=lambda x: x["energy_kwh_24h"], reverse=True)

    return {
        "building_rankings": rankings,
        "resource_totals": {
            "total_energy_kwh_24h": round(sum([c["energy_kwh_24h"] for c in comparison]), 1),
            "total_water_litres_24h": round(sum([c["water_litres_24h"] for c in comparison]), 1)
        }
    }
