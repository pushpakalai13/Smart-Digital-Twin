import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import get_db, fetch_records

db = get_db()
if db is not None:
    res = db.datasets.delete_many({"status": {"$in": ["pending_import", "validation_failed"]}})
    print(f"Deleted {res.deleted_count} pending/failed dataset history records from database.")
    
    remaining = fetch_records(db.datasets)
    print("Remaining datasets in database:")
    for d in remaining:
        print(f" - ID: {d.get('dataset_id')} | File: {d.get('filename')} | Type: {d.get('dataset_type')} | Status: {d.get('status')}")
