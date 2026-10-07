import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    print("--- DB ALERTS INSPECTION ---")
    all_alerts = fetch_records(db.alerts)
    print(f"Total alerts: {len(all_alerts)}")
    sources = {}
    timestamps = []
    for a in all_alerts:
        src = a.get("source", "<NO_SOURCE>")
        sources[src] = sources.get(src, 0) + 1
        if "created_at" in a:
            timestamps.append(a["created_at"])
        elif "timestamp" in a:
            timestamps.append(a["timestamp"])

    print(f"Alert counts by source: {sources}")
    if timestamps:
        print(f"Alert timestamp range: min={min(timestamps)}, max={max(timestamps)}")

    print("\n--- DB ANOMALIES INSPECTION ---")
    anomalies = fetch_records(db.anomalies)
    print(f"Total anomalies: {len(anomalies)}")
    anom_sources = {}
    anom_ts = []
    for an in anomalies:
        src = an.get("source", "<NO_SOURCE>")
        anom_sources[src] = anom_sources.get(src, 0) + 1
        if "timestamp" in an:
            anom_ts.append(an["timestamp"])
    print(f"Anomaly counts by source: {anom_sources}")
    if anom_ts:
        print(f"Anomaly timestamp range: min={min(anom_ts)}, max={max(anom_ts)}")

    print("\n--- DB RECOMMENDATIONS INSPECTION ---")
    recs = fetch_records(db.recommendations)
    print(f"Total recommendations: {len(recs)}")
    rec_sources = {}
    for r in recs:
        src = r.get("source", "<NO_SOURCE>")
        rec_sources[src] = rec_sources.get(src, 0) + 1
    print(f"Recommendation counts by source: {rec_sources}")

if __name__ == "__main__":
    main()
