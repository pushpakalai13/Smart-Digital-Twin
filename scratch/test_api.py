import urllib.request
import json

base_url = "http://127.0.0.1:8000/api"

# 1. Login
req = urllib.request.Request(f"{base_url}/auth/login", data=json.dumps({"email": "admin@smartcampus.edu", "password": "ALxM21AllspN"}).encode("utf-8"), headers={"Content-Type": "application/json"})
res = urllib.request.urlopen(req)
token = json.loads(res.read().decode("utf-8"))["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Test GET /api/energy/B001
req1 = urllib.request.Request(f"{base_url}/energy/B001", headers=headers)
try:
    res1 = urllib.request.urlopen(req1)
    data1 = json.loads(res1.read().decode("utf-8"))
    print(f"GET /api/energy/B001 -> Count: {len(data1)}")
    if data1:
        print("Sample B001 record:", data1[0])
except Exception as e:
    print("GET /api/energy/B001 error:", e)

# 3. Test GET /api/energy/predict/B001
req2 = urllib.request.Request(f"{base_url}/energy/predict/B001", headers=headers)
try:
    res2 = urllib.request.urlopen(req2)
    data2 = json.loads(res2.read().decode("utf-8"))
    print("GET /api/energy/predict/B001 -> Response:", data2)
except Exception as e:
    print("GET /api/energy/predict/B001 error:", e)
