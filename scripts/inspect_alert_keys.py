import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    alerts = fetch_records(db.alerts, query={"source": "uploaded"})
    print(f"Total uploaded alerts: {len(alerts)}")
    keys = []
    for a in alerts:
        k = (a['building_id'], a['metric'], a['timestamp'])
        keys.append(k)
        print(f"  {a['alert_id']} | {a['building_id']} | {a['metric']} | {a['timestamp']} | val={a['value']}")

    print(f"Unique keys count: {len(set(keys))}")

if __name__ == "__main__":
    main()
