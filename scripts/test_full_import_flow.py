import urllib.request
import json

login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

upload_url = "http://127.0.0.1:8000/api/datasets/upload"
csv_path = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real\energy_real_dataset.csv"
with open(csv_path, "rb") as f:
    file_bytes = f.read()

boundary = "----WebKitFormBoundaryTest"
body = b"".join([
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\nenergy\r\n".encode('utf-8'),
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"energy_real_dataset.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
    f"--{boundary}--\r\n".encode('utf-8')
])

req_upload = urllib.request.Request(upload_url, data=body, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
with urllib.request.urlopen(req_upload) as resp:
    res_data = json.loads(resp.read().decode('utf-8'))
    ds_id = res_data["dataset_id"]
    print(f"Uploaded Dataset ID: {ds_id} | Validation Valid: {res_data['validation']['valid']}")

import_url = f"http://127.0.0.1:8000/api/datasets/{ds_id}/import"
req_import = urllib.request.Request(import_url, data=json.dumps({"column_mapping": {}}).encode('utf-8'), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(req_import) as resp:
    res_import = json.loads(resp.read().decode('utf-8'))
    print(f"Import Result: {res_import}")
