import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    # Fetch all alerts
    all_alerts = fetch_records(db.alerts)
    stale_alerts_deleted = 0
    for a in all_alerts:
        src = a.get("source")
        # Any alert that is not explicitly source=="uploaded" or has date in July 2026 is stale
        ts = str(a.get("created_at", a.get("timestamp", "")))
        if src != "uploaded" or "2026-07" in ts:
            aid = a.get("alert_id")
            if aid:
                db.alerts.delete_many({"alert_id": aid})
            stale_alerts_deleted += 1

    # Fetch all recommendations
    all_recs = fetch_records(db.recommendations)
    stale_recs_deleted = 0
    for r in all_recs:
        src = r.get("source")
        ts = str(r.get("created_at", ""))
        if src != "uploaded" or "2026-07" in ts:
            rid = r.get("rec_id")
            if rid:
                db.recommendations.delete_many({"rec_id": rid})
            stale_recs_deleted += 1

    remaining_alerts = len(fetch_records(db.alerts))
    remaining_recs = len(fetch_records(db.recommendations))

    print(f"\n--- CLEANUP COMPLETE ---")
    print(f"  Stale alerts removed: {stale_alerts_deleted}")
    print(f"  Stale recommendations removed: {stale_recs_deleted}")
    print(f"  Current active real alerts remaining: {remaining_alerts}")
    print(f"  Current active real recommendations remaining: {remaining_recs}")

if __name__ == "__main__":
    main()
