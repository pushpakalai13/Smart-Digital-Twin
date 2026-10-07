from fastapi import APIRouter, Depends, HTTPException
from app.db import get_db, fetch_records
from app.core.security import get_current_user

router = APIRouter(prefix="/buildings", tags=["Buildings"])

@router.get("")
def get_buildings(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")
    buildings = fetch_records(db.buildings, sort_key="building_id", reverse=False)
    return buildings

@router.get("/{building_id}")
def get_building_detail(building_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    building = db.buildings.find_one({"building_id": building_id}, {"_id": 0})
    if not building:
        raise HTTPException(status_code=404, detail=f"Building '{building_id}' not found")

    recent_energy = fetch_records(db.energy_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=48)
    recent_water = fetch_records(db.water_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=48)
    recent_occupancy = fetch_records(db.occupancy_data, query={"building_id": building_id}, sort_key="timestamp", reverse=True, limit=48)
    building_alerts = fetch_records(db.alerts, query={"building_id": building_id}, sort_key="created_at", reverse=True)

    return {
        "building": building,
        "energy_history": recent_energy[::-1],
        "water_history": recent_water[::-1],
        "occupancy_history": recent_occupancy[::-1],
        "alerts": building_alerts
    }
