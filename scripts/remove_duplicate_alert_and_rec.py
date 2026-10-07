import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    # Delete ALT-UP-1012
    a1012 = db.alerts.find_one({"alert_id": "ALT-UP-1012"})
    if a1012:
        db.alerts.delete_many({"alert_id": "ALT-UP-1012"})
        print("Deleted duplicate alert 'ALT-UP-1012' from db.alerts.")
    else:
        print("Alert 'ALT-UP-1012' not found (already deleted).")

    # Delete REC-UP-112
    r112 = db.recommendations.find_one({"rec_id": "REC-UP-112"})
    if r112:
        db.recommendations.delete_many({"rec_id": "REC-UP-112"})
        print("Deleted duplicate recommendation 'REC-UP-112' from db.recommendations.")
    else:
        print("Recommendation 'REC-UP-112' not found (already deleted).")

    remaining_alerts = len(fetch_records(db.alerts))
    remaining_recs = len(fetch_records(db.recommendations))

    print(f"\nSummary after duplicate removal:")
    print(f"  Total remaining alerts in Atlas: {remaining_alerts}")
    print(f"  Total remaining recommendations in Atlas: {remaining_recs}")

if __name__ == "__main__":
    main()
