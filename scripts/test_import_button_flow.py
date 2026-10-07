import urllib.request
import json

login_url = "http://127.0.0.1:8000/api/auth/login"
login_data = json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode('utf-8')
req = urllib.request.Request(login_url, data=login_data, headers={"Content-Type": "application/json"})
with urllib.request.urlopen(req) as resp:
    token = json.loads(resp.read().decode('utf-8'))["access_token"]

ds_id = "DS-F6957B13"
import_url = f"http://127.0.0.1:8000/api/datasets/{ds_id}/import"
req_import = urllib.request.Request(import_url, data=json.dumps({}).encode('utf-8'), headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"}, method="POST")

try:
    with urllib.request.urlopen(req_import) as resp:
        res_import = json.loads(resp.read().decode('utf-8'))
        print(f"[IMPORT SUCCESS] {res_import}")
except urllib.error.HTTPError as e:
    print(f"[IMPORT ERROR] HTTP {e.code}: {e.read().decode('utf-8')}")

# Check ML status
ml_url = "http://127.0.0.1:8000/api/ml/status"
req_ml = urllib.request.Request(ml_url, headers={"Authorization": f"Bearer {token}"})
with urllib.request.urlopen(req_ml) as resp:
    ml_res = json.loads(resp.read().decode('utf-8'))
    water_model = ml_res.get("models", {}).get("water", {})
    print(f"[ML STATUS] Water Model Metrics: {water_model}")
