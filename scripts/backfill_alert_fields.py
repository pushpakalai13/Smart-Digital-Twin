import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    alerts = fetch_records(db.alerts)
    updated_count = 0
    for a in alerts:
        aid = a.get("alert_id")
        if not aid:
            continue
        metric_val = a.get("metric") or a.get("type") or "general"
        desc_val = a.get("description") or a.get("message") or "System anomaly detected."
        
        db.alerts.update_one(
            {"alert_id": aid},
            {"$set": {
                "metric": metric_val,
                "type": metric_val,
                "description": desc_val,
                "message": desc_val
            }}
        )
        updated_count += 1

    print(f"Successfully backfilled {updated_count} alert records in db.alerts.")

if __name__ == "__main__":
    main()
