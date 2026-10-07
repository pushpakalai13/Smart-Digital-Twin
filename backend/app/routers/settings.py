from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from app.db import get_db
from app.models.schemas import DataSourceSetting
from app.core.security import get_current_user, require_admin

router = APIRouter(prefix="/settings", tags=["System Settings"])

@router.get("/data-source")
def get_data_source_setting(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    setting = db.settings.find_one({"key": "data_source"})
    val = setting.get("value", "simulated") if setting else "simulated"
    return {"source": val}

@router.put("/data-source")
def update_data_source_setting(
    req: DataSourceSetting,
    current_user: dict = Depends(require_admin)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    if req.source not in ["simulated", "uploaded"]:
        raise HTTPException(status_code=400, detail="Source must be 'simulated' or 'uploaded'")

    db.settings.delete_many({"key": "data_source"})
    db.settings.insert_one({
        "key": "data_source",
        "value": req.source,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "updated_by": current_user["email"]
    })
    return {"source": req.source, "message": f"Global data source updated to '{req.source}'"}
