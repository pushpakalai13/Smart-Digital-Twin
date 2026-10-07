import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    for coll_name in ["energy_data", "water_data", "traffic_data", "occupancy_data", "parking_data"]:
        coll = getattr(db, coll_name)
        print(f"==================================================")
        print(f"COLLECTION: {coll_name}")
        total = coll.count_documents({})
        uploaded = fetch_records(coll, query={"source": "uploaded"}, sort_key="timestamp", reverse=False)
        simulated = fetch_records(coll, query={"source": "simulated"}, sort_key="timestamp", reverse=False)
        all_recs = fetch_records(coll, sort_key="timestamp", reverse=False)

        print(f"  Total records: {total}")
        print(f"  Uploaded records count: {len(uploaded)}")
        if uploaded:
            print(f"    Uploaded Min TS: {uploaded[0].get('timestamp')}")
            print(f"    Uploaded Max TS: {uploaded[-1].get('timestamp')}")

        print(f"  Simulated records count: {len(simulated)}")
        if simulated:
            print(f"    Simulated Min TS: {simulated[0].get('timestamp')}")
            print(f"    Simulated Max TS: {simulated[-1].get('timestamp')}")

        if all_recs:
            print(f"  Overall Min TS: {all_recs[0].get('timestamp')}")
            print(f"  Overall Max TS: {all_recs[-1].get('timestamp')}")

if __name__ == "__main__":
    main()
