import os
import io
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks, Response, Body
from fastapi.responses import FileResponse, StreamingResponse
import pandas as pd
import numpy as np

from app.db import get_db, fetch_records
from app.core.security import require_admin, get_current_user
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.pipeline import run_ml_pipeline

router = APIRouter(prefix="/datasets", tags=["Dataset Management"])

TEMP_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "uploads")
os.makedirs(TEMP_DIR, exist_ok=True)
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "sample_data")

REQUIRED_COLUMNS = {
    "energy": ["building_id", "timestamp", "value"],
    "water": ["building_id", "timestamp", "value"],
    "traffic": ["building_id", "timestamp", "value"],
    "occupancy": ["building_id", "timestamp", "occupancy_count", "capacity"],
    "parking": ["timestamp", "total_slots", "occupied_slots"],
    "buildings": ["building_id", "name", "category", "capacity", "floors", "area_sqft", "lat", "lng"]
}

def validate_dataframe(df: pd.DataFrame, dataset_type: str, valid_buildings: set):
    req_cols = REQUIRED_COLUMNS.get(dataset_type, [])
    missing_cols = [col for col in req_cols if col not in df.columns]
    
    col_report = {col: "present" if col in df.columns else "missing" for col in req_cols}
    row_errors = []
    warnings = []

    if missing_cols:
        return {
            "valid": False,
            "missing_columns": missing_cols,
            "detected_columns": list(df.columns),
            "column_report": col_report,
            "row_errors": [f"Missing required column(s) for '{dataset_type}': {', '.join(missing_cols)}. Detected columns: {', '.join(list(df.columns))}."],
            "warnings": warnings,
            "total_rows": len(df)
        }

    for idx, row in df.iterrows():
        r_num = idx + 1
        if "building_id" in row and valid_buildings:
            bid = str(row["building_id"])
            if bid not in valid_buildings:
                warnings.append(f"Row {r_num}: Building ID '{bid}' is not registered in buildings list.")
        
        if "timestamp" in row:
            try:
                pd.to_datetime(row["timestamp"])
            except Exception:
                row_errors.append(f"Row {r_num}: Invalid timestamp format '{row['timestamp']}'.")

        if "value" in row and pd.notnull(row["value"]):
            try:
                val = float(row["value"])
                if val < 0:
                    row_errors.append(f"Row {r_num}: Metric value ({val}) not allowed to be negative.")
            except ValueError:
                row_errors.append(f"Row {r_num}: Metric value '{row['value']}' is non-numeric.")

    is_valid = len(row_errors) == 0

    return {
        "valid": is_valid,
        "missing_columns": [],
        "detected_columns": list(df.columns),
        "column_report": col_report,
        "row_errors": row_errors[:20],
        "warnings": warnings[:20],
        "total_rows": len(df)
    }

@router.post("/upload")
def upload_dataset(
    file: UploadFile = File(...),
    dataset_type: str = Form(...),
    current_user: dict = Depends(require_admin)
):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    if dataset_type not in REQUIRED_COLUMNS:
        raise HTTPException(status_code=400, detail=f"Unsupported dataset type '{dataset_type}'")

    file_bytes = file.file.read()
    if len(file_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum limit of 50 MB.")

    file_ext = os.path.splitext(file.filename)[1].lower()
    try:
        if file_ext in [".csv", ".txt"]:
            df = pd.read_csv(io.BytesIO(file_bytes))
        elif file_ext in [".xlsx", ".xls"]:
            df = pd.read_excel(io.BytesIO(file_bytes))
        else:
            raise HTTPException(status_code=400, detail="Only CSV and XLSX files are supported.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse file content: {e}")

    dataset_id = f"DS-{uuid.uuid4().hex[:8].upper()}"
    temp_filepath = os.path.join(TEMP_DIR, f"{dataset_id}{file_ext}")
    with open(temp_filepath, "wb") as f:
        f.write(file_bytes)

    buildings_docs = fetch_records(db.buildings)
    valid_bids = set([b["building_id"] for b in buildings_docs if "building_id" in b])

    val_result = validate_dataframe(df, dataset_type, valid_bids)
    preview_rows = df.head(20).fillna("").to_dict(orient="records")

    doc = {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "dataset_type": dataset_type,
        "row_count": len(df),
        "status": "pending_import" if val_result["valid"] else "validation_failed",
        "validation_report": val_result,
        "source": "uploaded",
        "file_path": temp_filepath,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": current_user["email"]
    }
    db.datasets.insert_one(doc)

    return {
        "dataset_id": dataset_id,
        "filename": file.filename,
        "dataset_type": dataset_type,
        "row_count": len(df),
        "validation": val_result,
        "preview": preview_rows
    }

@router.get("")
def list_datasets(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    datasets = list(db.datasets.find())
    for d in datasets:
        d["_id"] = str(d["_id"])
    return datasets

@router.get("/{dataset_id}")
def get_dataset_detail(dataset_id: str, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    ds = db.datasets.find_one({"dataset_id": dataset_id})
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")

    ds["_id"] = str(ds["_id"])
    return ds

@router.post("/{dataset_id}/import")
def import_dataset(
    dataset_id: str,
    payload: Optional[Dict[str, Any]] = Body(None),
    current_user: dict = Depends(require_admin)
):
    column_mapping = payload.get("column_mapping") if payload else None
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    ds = db.datasets.find_one({"dataset_id": dataset_id})
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")

    file_path = ds.get("file_path")
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail="Upload file lost or expired.")

    file_ext = os.path.splitext(file_path)[1].lower()
    df = pd.read_csv(file_path) if file_ext in [".csv", ".txt"] else pd.read_excel(file_path)

    if column_mapping:
        df = df.rename(columns=column_mapping)

    dataset_type = ds["dataset_type"]
    records = df.to_dict(orient="records")

    for r in records:
        r["source"] = "uploaded"
        r["dataset_id"] = dataset_id
        if "unit" not in r:
            if dataset_type == "energy": r["unit"] = "kWh"
            elif dataset_type == "water": r["unit"] = "L"
            elif dataset_type == "traffic": r["unit"] = "vehicles"

    coll_map = {
        "energy": db.energy_data,
        "water": db.water_data,
        "traffic": db.traffic_data,
        "occupancy": db.occupancy_data,
        "parking": db.parking_data,
        "buildings": db.buildings
    }
    coll = coll_map.get(dataset_type)
    if coll is None:
        raise HTTPException(status_code=400, detail="Invalid dataset collection map")

    inserted = 0
    if dataset_type == "buildings":
        for r in records:
            bid = r.get("building_id")
            if bid:
                db.buildings.delete_many({"building_id": bid})
                db.buildings.insert_one(r)
                inserted += 1
            else:
                db.buildings.insert_one(r)
                inserted += 1
    else:
        chunk_size = 5000
        for i in range(0, len(records), chunk_size):
            chunk = records[i:i + chunk_size]
            coll.insert_many(chunk)
            inserted += len(chunk)

    try:
        db.datasets.update_one(
            {"dataset_id": dataset_id},
            {"$set": {"status": "imported", "imported_rows": inserted, "imported_at": datetime.now(timezone.utc).isoformat()}}
        )
    except Exception as update_err:
        print(f"Mongita update notice: {update_err}. Performing direct document replace.")
        ds["status"] = "imported"
        ds["imported_rows"] = inserted
        ds["imported_at"] = datetime.now(timezone.utc).isoformat()
        db.datasets.delete_many({"dataset_id": dataset_id})
        db.datasets.insert_one(ds)

    db.settings.delete_many({"key": "data_source"})
    db.settings.insert_one({
        "key": "data_source",
        "value": "uploaded",
        "updated_at": datetime.now(timezone.utc).isoformat()
    })

    try:
        run_ml_pipeline(source="uploaded")
    except Exception as e:
        print(f"ML retraining warning after dataset import: {e}")

    return {
        "dataset_id": dataset_id,
        "status": "imported",
        "rows_imported": inserted,
        "message": f"Successfully imported {inserted} records into Atlas collection '{dataset_type}'."
    }

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: str, current_user: dict = Depends(require_admin)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    ds = db.datasets.find_one({"dataset_id": dataset_id})
    if not ds:
        raise HTTPException(status_code=404, detail=f"Dataset '{dataset_id}' not found")

    dataset_type = ds.get("dataset_type")
    coll_map = {
        "energy": db.energy_data,
        "water": db.water_data,
        "traffic": db.traffic_data,
        "occupancy": db.occupancy_data,
        "parking": db.parking_data,
        "buildings": db.buildings
    }
    coll = coll_map.get(dataset_type)
    deleted_rows = 0
    if coll is not None:
        res = coll.delete_many({"dataset_id": dataset_id})
        deleted_rows = res.deleted_count

    db.datasets.delete_one({"dataset_id": dataset_id})

    file_path = ds.get("file_path")
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass

    return {
        "dataset_id": dataset_id,
        "status": "deleted",
        "rows_deleted": deleted_rows,
        "message": f"Dataset '{dataset_id}' and all imported rows deleted from Atlas."
    }

@router.get("/template/{dataset_type}")
def get_dataset_template(dataset_type: str):
    if dataset_type not in REQUIRED_COLUMNS:
        raise HTTPException(status_code=400, detail="Invalid dataset type")

    sample_file = os.path.join(SAMPLE_DIR, f"{dataset_type}_sample.csv")
    if os.path.exists(sample_file):
        return FileResponse(sample_file, media_type="text/csv", filename=f"{dataset_type}_template.csv")

    cols = REQUIRED_COLUMNS[dataset_type]
    csv_content = ",".join(cols) + "\n"
    return StreamingResponse(
        io.StringIO(csv_content),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={dataset_type}_template.csv"}
    )
