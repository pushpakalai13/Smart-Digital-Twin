import urllib.request
import json
import os
import sys

login_url = 'http://127.0.0.1:8080/api/auth/login'
login_data = json.dumps({'email': 'admin@smartcampus.edu', 'password': 'ALxM21AllspN'}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={'Content-Type': 'application/json'})

try:
    with urllib.request.urlopen(req) as resp:
        token = json.loads(resp.read().decode('utf-8'))['access_token']
        print("Successfully logged in as admin.")
except Exception as e:
    print(f"Failed to login: {e}")
    sys.exit(1)

types_files = [
    ('buildings', 'buildings_real_dataset.csv'),
    ('energy', 'energy_real_dataset.csv'),
    ('water', 'water_real_dataset.csv'),
    ('traffic', 'traffic_real_dataset.csv'),
    ('occupancy', 'occupancy_real_dataset.csv'),
    ('parking', 'parking_real_dataset.csv')
]

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data", "real"))

for dtype, fname in types_files:
    fpath = os.path.join(base_dir, fname)
    if not os.path.exists(fpath):
        print(f"[{dtype.upper()}] File missing: {fpath}")
        continue
    
    with open(fpath, 'rb') as f:
        file_bytes = f.read()

    boundary = f"----WebKitFormBoundary{dtype}"
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\n{dtype}\r\n".encode('utf-8'),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
        f"--{boundary}--\r\n".encode('utf-8')
    ])

    upload_url = 'http://127.0.0.1:8080/api/datasets/upload'
    req_upload = urllib.request.Request(upload_url, data=body, headers={'Authorization': f'Bearer {token}', 'Content-Type': f'multipart/form-data; boundary={boundary}'}, method='POST')
    try:
        with urllib.request.urlopen(req_upload) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            ds_id = res_data['dataset_id']
            valid = res_data.get('validation', {}).get('valid')
            print(f"[{dtype.upper()}] Uploaded Dataset ID: {ds_id} | Valid: {valid}")
    except Exception as e:
        print(f"[{dtype.upper()}] Upload Error: {e}")
        continue

    import_url = f"http://127.0.0.1:8080/api/datasets/{ds_id}/import"
    req_import = urllib.request.Request(import_url, data=json.dumps({'column_mapping': {}}).encode('utf-8'), headers={'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req_import) as resp:
            res_import = json.loads(resp.read().decode('utf-8'))
            print(f"[{dtype.upper()}] Import Result: {res_import.get('message', 'Success')}")
    except Exception as e:
        print(f"[{dtype.upper()}] Import Error: {e}")

print("\n--- Running ML Pipeline on Uploaded Real Datasets ---")
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from ml.pipeline import run_ml_pipeline
ml_result = run_ml_pipeline(source="uploaded")
print("ML Pipeline execution completed:", ml_result)
