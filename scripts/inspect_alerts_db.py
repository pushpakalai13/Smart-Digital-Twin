import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    alerts = fetch_records(db.alerts)
    print(f"Total alerts in db.alerts: {len(alerts)}")
    for a in alerts:
        print(a)
    anomalies = fetch_records(db.anomalies)
    print(f"\nTotal anomalies in db.anomalies: {len(anomalies)}")
    for an in anomalies:
        print(an)

if __name__ == "__main__":
    main()
