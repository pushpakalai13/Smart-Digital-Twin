import os
import sys
import shutil
from datetime import datetime, timezone

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import get_db

db = get_db()
if db is not None:
    ds_id = "DS-F6957B13"
    filename = "water_real_dataset.csv"
    src_file = os.path.join(root_dir, "sample_data", "real", filename)
    dest_dir = os.path.join(root_dir, "data", "uploads")
    os.makedirs(dest_dir, exist_ok=True)
    dest_file = os.path.join(dest_dir, f"{ds_id}.csv")
    
    shutil.copyfile(src_file, dest_file)
    
    # Remove existing record if present
    db.datasets.delete_many({"dataset_id": ds_id})
    
    doc = {
        "dataset_id": ds_id,
        "filename": filename,
        "dataset_type": "water",
        "row_count": 250,
        "status": "pending_import",
        "source": "uploaded",
        "file_path": dest_file,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "admin@smartcampus.edu",
        "validation_report": {
            "valid": True,
            "missing_columns": [],
            "detected_columns": ["building_id", "timestamp", "value", "unit"],
            "column_report": {"building_id": "present", "timestamp": "present", "value": "present"},
            "row_errors": [],
            "warnings": [],
            "total_rows": 250
        }
    }
    db.datasets.insert_one(doc)
    print(f"[SUCCESS] Prepared dataset record '{ds_id}' ({filename}) with status 'pending_import' at {dest_file}")
