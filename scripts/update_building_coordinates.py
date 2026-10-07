import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

NEW_COORDINATES = {
    "B001": {"lat": 12.9728, "lng": 77.5935, "name": "Academic Block A"},
    "B002": {"lat": 12.9728, "lng": 77.5945, "name": "Academic Block B"},
    "B003": {"lat": 12.9722, "lng": 77.5940, "name": "Central Library"},
    "B004": {"lat": 12.9720, "lng": 77.5932, "name": "Admin Complex"},
    "B005": {"lat": 12.9712, "lng": 77.5945, "name": "Student Hostel North"},
    "B006": {"lat": 12.9706, "lng": 77.5945, "name": "Student Hostel South"},
    "B007": {"lat": 12.9714, "lng": 77.5936, "name": "Campus Canteen & Food Court"},
    "B008": {"lat": 12.9718, "lng": 77.5954, "name": "Indoor Sports Complex"},
    "B009": {"lat": 12.9735, "lng": 77.5942, "name": "Advanced Research Labs"},
    "B010": {"lat": 12.9735, "lng": 77.5950, "name": "Technology Innovation Hub"}
}

def update_campus_coordinates():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    print("Updating building coordinates in MongoDB...")
    for bid, coords in NEW_COORDINATES.items():
        doc = db.buildings.find_one({"building_id": bid})
        if doc:
            db.buildings.update_one(
                {"building_id": bid},
                {"$set": {
                    "lat": coords["lat"],
                    "lng": coords["lng"],
                    "coordinates": {"lat": coords["lat"], "lng": coords["lng"]}
                }}
            )
            print(f"Updated {bid} ({coords['name']}): lat={coords['lat']}, lng={coords['lng']}")
        else:
            print(f"Warning: Building {bid} not found in DB")

if __name__ == "__main__":
    update_campus_coordinates()
