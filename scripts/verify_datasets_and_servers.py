import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db
from app.core.security import create_access_token

def main():
    token = create_access_token({"sub": "admin@smartcampus.edu", "role": "admin", "name": "System Admin"})
    headers = {"Authorization": f"Bearer {token}"}

    url = "http://127.0.0.1:8000/api/datasets"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            datasets = json.loads(resp.read().decode('utf-8'))
            print(f"Total Datasets in Atlas/DB: {len(datasets)}\n")
            print(f"{'Dataset ID':<15} {'Filename':<30} {'Type':<12} {'Status':<15} {'Rows':<10}")
            print("-" * 85)
            for d in datasets:
                ds_id = d.get("dataset_id", "")
                fname = d.get("filename", "")
                dtype = d.get("dataset_type", "")
                status = d.get("status", "")
                rows = d.get("imported_rows", d.get("row_count", 0))
                print(f"{ds_id:<15} {fname:<30} {dtype:<12} {status:<15} {rows:<10}")

    except Exception as e:
        print(f"Error checking datasets endpoint: {e}")

if __name__ == "__main__":
    main()
