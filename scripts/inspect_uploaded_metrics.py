import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    buildings = fetch_records(db.buildings, sort_key="building_id")
    print("Metrics per building from uploaded dataset:")
    print("-" * 60)
    for b in buildings:
        bid = b["building_id"]
        latest_e = fetch_records(db.energy_data, query={"building_id": bid, "source": "uploaded"}, sort_key="timestamp", reverse=True, limit=1)
        latest_w = fetch_records(db.water_data, query={"building_id": bid, "source": "uploaded"}, sort_key="timestamp", reverse=True, limit=1)
        latest_o = fetch_records(db.occupancy_data, query={"building_id": bid, "source": "uploaded"}, sort_key="timestamp", reverse=True, limit=1)
        
        e_val = latest_e[0]["value"] if latest_e else None
        w_val = latest_w[0]["value"] if latest_w else None
        o_count = latest_o[0]["occupancy_count"] if latest_o else None
        o_cap = b.get("capacity", 500)
        o_rate = round((o_count / o_cap) * 100, 1) if o_count is not None and o_cap else None
        
        print(f"Building: {bid} ({b['name']})")
        print(f"  Latest Energy (kWh): {e_val}")
        print(f"  Latest Water (L):    {w_val}")
        print(f"  Latest Occupancy:   {o_count}/{o_cap} ({o_rate}%)")

if __name__ == "__main__":
    main()
