import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return
    buildings = fetch_records(db.buildings, sort_key="building_id")
    print(f"Total buildings: {len(buildings)}\n")
    for b in buildings:
        print(f"ID: {b.get('building_id')}")
        print(f"Name: {b.get('name')}")
        print(f"Category: {b.get('category')}")
        print(f"Latitude: {b.get('latitude')}")
        print(f"Longitude: {b.get('longitude')}")
        print(f"Coordinates: {b.get('coordinates')}")
        print(f"Location: {b.get('location')}")
        print("-" * 40)

if __name__ == "__main__":
    main()
