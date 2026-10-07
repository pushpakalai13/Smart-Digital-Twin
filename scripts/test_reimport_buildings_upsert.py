import urllib.request
import json
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import get_db, fetch_records

# 1. Login to get token
login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

# 2. Upload buildings_real_dataset.csv
fpath = os.path.join(root_dir, "sample_data", "real", "buildings_real_dataset.csv")
with open(fpath, "rb") as f:
    file_bytes = f.read()

boundary = "----BoundaryBuildingsUpsert"
body = b"".join([
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\nbuildings\r\n".encode('utf-8'),
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"buildings_real_dataset.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
    f"--{boundary}--\r\n".encode('utf-8')
])

upload_url = "http://127.0.0.1:8000/api/datasets/upload"
req_upload = urllib.request.Request(upload_url, data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
with urllib.request.urlopen(req_upload) as resp:
    res_data = json.loads(resp.read().decode('utf-8'))
    ds_id = res_data["dataset_id"]
    print(f"Uploaded Buildings Dataset ID: {ds_id}")

# 3. Import dataset
import_url = f"http://127.0.0.1:8000/api/datasets/{ds_id}/import"
req_import = urllib.request.Request(import_url, data=json.dumps({}).encode('utf-8'), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_import) as resp:
    res_import = json.loads(resp.read().decode('utf-8'))
    print(f"Import Result: {res_import}")

# 4. Check DB for building count
db = get_db()
if db is not None:
    b_docs = fetch_records(db.buildings)
    print(f"\nDB Total Building Documents: {len(b_docs)}")
    b_names = [b.get("name") for b in b_docs]
    print(f"Building Names: {b_names}")
    
    # Check Analytics endpoint response
    analytics_url = "http://127.0.0.1:8000/api/analytics"
    req_an = urllib.request.Request(analytics_url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req_an) as an_resp:
        an_data = json.loads(an_resp.read().decode('utf-8'))
        rankings = an_data.get("building_energy_rankings", [])
        print(f"\nAnalytics Building Energy Intensity Rankings Count: {len(rankings)}")
        for r in rankings:
            print(f" - [{r.get('building_id')}] {r.get('name')} | Intensity: {r.get('energy_intensity_kwh_per_sqft')} kWh/sqft")
