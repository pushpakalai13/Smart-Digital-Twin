import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    db.alerts.delete_many({"alert_id": "ALT-UP-1012"})
    db.recommendations.delete_many({"rec_id": "REC-UP-112"})

    alerts = fetch_records(db.alerts)
    recs = fetch_records(db.recommendations)

    print(f"Total active alerts remaining: {len(alerts)}")
    print(f"Total recommendations remaining: {len(recs)}")

    # Verify no duplicate timestamps exist for same building and metric
    keys = [(a['building_id'], a['metric'], a['timestamp']) for a in alerts]
    print(f"Unique (building_id, metric, timestamp) keys count: {len(set(keys))}")
    if len(keys) == len(set(keys)):
        print("CONFIRMED: ZERO duplicate alert pairs exist!")

if __name__ == "__main__":
    main()
