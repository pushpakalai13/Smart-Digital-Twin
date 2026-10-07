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
    print(f"Total alerts in db.alerts: {len(alerts)}\n")
    for a in alerts[:5]:
        print(f"ID: {a.get('alert_id')}")
        print(f"  metric: {a.get('metric')}")
        print(f"  type: {a.get('type')}")
        print(f"  description: {a.get('description')}")
        print(f"  message: {a.get('message')}")
        print("-" * 50)

if __name__ == "__main__":
    main()
