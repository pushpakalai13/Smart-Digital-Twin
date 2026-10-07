import urllib.request
import json

login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

upload_url = "http://127.0.0.1:8000/api/datasets/upload"
csv_path = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real\water_real_dataset.csv"
with open(csv_path, "rb") as f:
    file_bytes = f.read()

boundary = "----WebKitFormBoundaryWaterTest"

# Test 1: Upload with dataset_type="water"
body_1 = b"".join([
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\nwater\r\n".encode('utf-8'),
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"water_real_dataset.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
    f"--{boundary}--\r\n".encode('utf-8')
])

req_1 = urllib.request.Request(upload_url, data=body_1, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
try:
    with urllib.request.urlopen(req_1) as resp:
        print("[Test 1: dataset_type=water] Status:", resp.status)
        print("Response:", resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"[Test 1] HTTP {e.code}:", e.read().decode('utf-8'))

# Test 2: Upload without dataset_type parameter (to see if FastAPI returns 'field required')
body_2 = b"".join([
    f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"water_real_dataset.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n",
    f"--{boundary}--\r\n".encode('utf-8')
])

req_2 = urllib.request.Request(upload_url, data=body_2, headers={"Authorization": f"Bearer {token}", "Content-Type": f"multipart/form-data; boundary={boundary}"}, method="POST")
try:
    with urllib.request.urlopen(req_2) as resp:
        print("[Test 2: No dataset_type] Status:", resp.status)
        print("Response:", resp.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"[Test 2] HTTP {e.code}:", e.read().decode('utf-8'))
