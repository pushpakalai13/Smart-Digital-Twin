import sys
import os
import urllib.request
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db
from app.core.security import create_access_token

def main():
    db = get_db()
    user = db.users.find_one({})
    if user:
        email = user["email"]
        role = user.get("role", "admin")
        name = user.get("name", "Admin User")
    else:
        email = "admin@smartcampus.edu"
        role = "admin"
        name = "System Admin"

    token = create_access_token({"sub": email, "role": role, "name": name})

    url = "http://127.0.0.1:8000/api/digital-twin"
    headers = {"Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode('utf-8')
            data = json.loads(res_body)
            print(f"Active Data Source: {data.get('source')}")
            print(f"Total Buildings returned: {len(data.get('buildings', []))}\n")
            
            buildings = data.get('buildings', [])
            target_ids = ["B001", "B003", "B005"]
            
            for b in buildings:
                if b.get("building_id") in target_ids:
                    print("=" * 60)
                    print(f"BUILDING: {b.get('name')} (ID: {b.get('building_id')})")
                    print(f"  Category: {b.get('category')}")
                    print(f"  Coordinates: Lat {b.get('lat')}, Lng {b.get('lng')}")
                    print(f"  Nested Coordinates Obj: {b.get('coordinates')}")
                    print(f"  Live Sensor Telemetry:")
                    print(f"    - Energy Load:    {b.get('metrics', {}).get('energy_kwh')} kWh")
                    print(f"    - Water Flow:     {b.get('metrics', {}).get('water_litres')} L")
                    print(f"    - Occupancy Rate: {b.get('metrics', {}).get('occupancy_rate')}% ({b.get('metrics', {}).get('occupancy_count')} / {b.get('capacity')} people)")
                    print(f"  Status Color: {b.get('status').upper()}")
                    print(f"  Status Trigger Reasons: {b.get('status_reasons')}")
                    print(f"  Active Anomaly Alerts Count: {b.get('active_alerts_count')}")

    except Exception as err:
        print(f"Request error: {err}")

if __name__ == "__main__":
    main()
