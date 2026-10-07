import urllib.request
import urllib.parse
import json

# 1. Login to get admin token
login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({
    "email": "admin@smartcampus.edu",
    "password": "ALxM21AllspN"
}).encode('utf-8')

req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req) as response:
        res_text = response.read().decode('utf-8')
        print(f"Login Status: {response.status}")
        token = json.loads(res_text).get("access_token")
        print(f"Token: {token[:20]}...")
except Exception as e:
    print(f"Login Error: {e}")
    exit(1)

# 2. Test uploading using multipart form data manually constructed
upload_url = "http://127.0.0.1:8000/api/datasets/upload"
csv_path = r"C:\Users\pushpakalai\.gemini\antigravity\scratch\smart_campus_digital_twin\sample_data\real\energy_real_dataset.csv"

with open(csv_path, "rb") as f:
    file_bytes = f.read()

boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"

# Construct valid multipart body
body_parts = []
# Field: dataset_type
body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"dataset_type\"\r\n\r\nenergy\r\n".encode('utf-8'))
# Field: file
body_parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"energy_real_dataset.csv\"\r\nContent-Type: text/csv\r\n\r\n".encode('utf-8') + file_bytes + b"\r\n")
body_parts.append(f"--{boundary}--\r\n".encode('utf-8'))

full_body = b"".join(body_parts)

print("\n--- TEST A: Correct Content-Type WITH boundary string ---")
headers_correct = {
    "Authorization": f"Bearer {token}",
    "Content-Type": f"multipart/form-data; boundary={boundary}"
}
req_a = urllib.request.Request(upload_url, data=full_body, headers=headers_correct, method="POST")
try:
    with urllib.request.urlopen(req_a) as resp:
        print(f"[Test A] HTTP {resp.status}")
        print(f"Response JSON: {resp.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    print(f"[Test A] HTTP {e.code}: {e.read().decode('utf-8')}")

print("\n--- TEST B: Plain 'Content-Type: multipart/form-data' WITHOUT boundary string (What Axios sends when manually specified) ---")
headers_bad = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "multipart/form-data"
}
req_b = urllib.request.Request(upload_url, data=full_body, headers=headers_bad, method="POST")
try:
    with urllib.request.urlopen(req_b) as resp:
        print(f"[Test B] HTTP {resp.status}")
        print(f"Response JSON: {resp.read().decode('utf-8')[:300]}")
except urllib.error.HTTPError as e:
    print(f"[Test B] HTTP {e.code}: {e.read().decode('utf-8')}")
