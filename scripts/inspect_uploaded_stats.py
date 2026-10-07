import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    for coll_name, val_key in [("energy_data", "value"), ("water_data", "value"), ("occupancy_data", "occupancy_count")]:
        coll = getattr(db, coll_name)
        docs = fetch_records(coll, query={"source": "uploaded"})
        if docs:
            vals = [d.get(val_key, 0) for d in docs if val_key in d]
            print(f"{coll_name} (uploaded): count={len(vals)}, min={min(vals)}, max={max(vals)}, avg={sum(vals)/len(vals):.2f}")
        else:
            print(f"{coll_name} (uploaded): none")

if __name__ == "__main__":
    main()
