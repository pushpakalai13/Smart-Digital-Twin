import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records, get_db_status

def main():
    db = get_db()
    print("DB status:", get_db_status())
    
    active_source_setting = db.settings.find_one({"key": "data_source"})
    print("Active data_source setting:", active_source_setting)

    for coll_name in ["energy_data", "water_data", "occupancy_data", "alerts"]:
        coll = getattr(db, coll_name)
        total_count = coll.count_documents({})
        uploaded_count = coll.count_documents({"source": "uploaded"})
        simulated_count = coll.count_documents({"source": "simulated"})
        print(f"Collection {coll_name}: total={total_count}, uploaded={uploaded_count}, simulated={simulated_count}")
        latest_uploaded = fetch_records(coll, query={"source": "uploaded"}, sort_key="timestamp" if coll_name != "alerts" else "created_at", reverse=True, limit=1)
        if latest_uploaded:
            print(f"  Latest uploaded in {coll_name}: {latest_uploaded[0]}")
        else:
            print(f"  No uploaded records in {coll_name}")

if __name__ == "__main__":
    main()
