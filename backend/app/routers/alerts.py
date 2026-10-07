from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import datetime, timezone
from app.db import get_db, fetch_records
from app.models.schemas import AlertResolveRequest
from app.core.security import get_current_user

router = APIRouter(prefix="/alerts", tags=["Alerts"])

def get_active_source(db):
    setting = db.settings.find_one({"key": "data_source"})
    return setting.get("value", "simulated") if setting else "simulated"

@router.get("")
def get_alerts(
    status: Optional[str] = None,
    building_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = get_active_source(db)
    query = {"source": active_src} if db.alerts.count_documents({"source": active_src}) > 0 else {}
    if status:
        query["status"] = status
    if building_id:
        query["building_id"] = building_id

    alerts = fetch_records(db.alerts, query=query, sort_key="created_at", reverse=True)
    for a in alerts:
        metric_val = a.get("metric") or a.get("type") or "general"
        desc_val = a.get("description") or a.get("message") or "System anomaly detected."
        a["metric"] = metric_val
        a["type"] = metric_val
        a["description"] = desc_val
        a["message"] = desc_val
    return alerts

@router.put("/{alert_id}/resolve")
def resolve_alert(
    alert_id: str,
    req: AlertResolveRequest,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    alert = db.alerts.find_one({"alert_id": alert_id})
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert '{alert_id}' not found")

    resolved_time = datetime.now(timezone.utc).isoformat()
    db.alerts.update_one(
        {"alert_id": alert_id},
        {"$set": {
            "status": "resolved",
            "resolved_at": resolved_time,
            "resolved_by": current_user["email"],
            "resolution_notes": req.resolution_notes or "Marked resolved by operator"
        }}
    )

    return {
        "alert_id": alert_id,
        "status": "resolved",
        "resolved_at": resolved_time,
        "message": f"Alert '{alert_id}' successfully marked as resolved."
    }
