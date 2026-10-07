import urllib.request
import json
import os

login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

base_dir = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real"

test_files = [
    ("traffic", "traffic_real_dataset.csv"),
    ("occupancy", "occupancy_real_dataset.csv"),
    ("parking", "parking_real_dataset.csv"),
    ("buildings", "buildings_real_dataset.csv")
]

for dtype, fname in test_files:
    fpath = os.path.join(base_dir, fname)
    with open(fpath, "rb") as f:
        file_bytes = f.read()

    boundary = f"----BoundaryFix{dtype}"
    # Form field 'dataset_type' FIRST, 'file' SECOND
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
            ds_id = res_data["dataset_id"]
            v = res_data.get("validation", {})
            print(f"[{dtype.upper()} UPLOAD SUCCESS] Dataset ID: {ds_id} | Valid: {v.get('valid')} | Rows: {v.get('total_rows')} | Errors: {len(v.get('row_errors', []))}")
            
            # Immediately import
            import_url = f"http://127.0.0.1:8000/api/datasets/{ds_id}/import"
            req_import = urllib.request.Request(import_url, data=json.dumps({}).encode('utf-8'), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req_import) as imp_resp:
                imp_res = json.loads(imp_resp.read().decode('utf-8'))
                print(f"  -> [IMPORT SUCCESS] {imp_res.get('message')}")
    except urllib.error.HTTPError as e:
        print(f"[{dtype.upper()} ERROR] HTTP {e.code}: {e.read().decode('utf-8')}")
