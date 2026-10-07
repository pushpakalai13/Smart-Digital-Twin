import urllib.request
import json
import os

login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

base_dir = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real"

test_cases = [
    ("energy", "energy_real_dataset.csv"),
    ("water", "water_real_dataset.csv"),
    ("traffic", "traffic_real_dataset.csv"),
    ("occupancy", "occupancy_real_dataset.csv"),
    ("parking", "parking_real_dataset.csv"),
    ("buildings", "buildings_real_dataset.csv")
]

print("=== TEST 1: Appending 'dataset_type' BEFORE 'file' in Multipart Form Body ===")
for dtype, fname in test_cases:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, "rb") as f:
        file_bytes = f.read()

    boundary = f"----BoundaryDtypeBefore{dtype}"
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\n{dtype}\r\n".encode('utf-8'),
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
        f"--{boundary}--\r\n".encode('utf-8')
    ])

    upload_url = "http://127.0.0.1:8000/api/datasets/upload"
    req_upload = urllib.request.Request(upload_url, data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    try:
        with urllib.request.urlopen(req_upload) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            v = res_data.get("validation", {})
            print(f"[{dtype.upper()}] HTTP {resp.status} | Dataset ID: {res_data.get('dataset_id')} | Valid: {v.get('valid')} | Rows: {v.get('total_rows')} | Errors: {len(v.get('row_errors', []))}")
    except urllib.error.HTTPError as e:
        print(f"[{dtype.upper()}] HTTP {e.code}: {e.read().decode('utf-8')}")

print("\n=== TEST 2: Appending 'file' BEFORE 'dataset_type' in Multipart Form Body ===")
for dtype, fname in test_cases:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, "rb") as f:
        file_bytes = f.read()

    boundary = f"----BoundaryFileBefore{dtype}"
    body = b"".join([
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"{fname}\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\n{dtype}\r\n".encode('utf-8'),
        f"--{boundary}--\r\n".encode('utf-8')
    ])

    upload_url = "http://127.0.0.1:8000/api/datasets/upload"
    req_upload = urllib.request.Request(upload_url, data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
    try:
        with urllib.request.urlopen(req_upload) as resp:
            res_data = json.loads(resp.read().decode('utf-8'))
            v = res_data.get("validation", {})
            print(f"[{dtype.upper()}] HTTP {resp.status} | Dataset ID: {res_data.get('dataset_id')} | Valid: {v.get('valid')} | Rows: {v.get('total_rows')} | Errors: {len(v.get('row_errors', []))}")
    except urllib.error.HTTPError as e:
        print(f"[{dtype.upper()}] HTTP {e.code}: {e.read().decode('utf-8')}")
