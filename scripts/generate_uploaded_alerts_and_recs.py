import sys
import os
from datetime import datetime, timezone
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return

    b_map = {b["building_id"]: b.get("name", b["building_id"]) for b in fetch_records(db.buildings)}

    # Remove existing uploaded alerts & recommendations to regenerate cleanly
    db.alerts.delete_many({"source": "uploaded"})
    db.recommendations.delete_many({"source": "uploaded"})

    alerts_to_insert = []
    recs_to_insert = []
    seen_keys = set()  # Deduplication set: (building_id, metric, timestamp)

    # Check energy uploaded data
    e_docs = fetch_records(db.energy_data, query={"source": "uploaded"}, sort_key="timestamp", reverse=True)
    for e in e_docs:
        val = e.get("value", 0)
        bid = e.get("building_id")
        ts = e.get("timestamp")
        bname = b_map.get(bid, bid)
        dedup_key = (bid, "energy", ts)

        if val >= 150.0 and dedup_key not in seen_keys and len([a for a in alerts_to_insert if a["building_id"] == bid and a["metric"] == "energy"]) < 2:
            seen_keys.add(dedup_key)
            alert_id = f"ALT-UP-{len(alerts_to_insert)+1001}"
            alerts_to_insert.append({
                "alert_id": alert_id,
                "building_id": bid,
                "building_name": bname,
                "timestamp": ts,
                "created_at": ts,
                "metric": "energy",
                "value": round(val, 1),
                "expected_value": 70.0,
                "severity": "high" if val >= 250.0 else "medium",
                "description": f"High energy spike of {round(val,1)} kWh detected in {bname}.",
                "status": "active",
                "source": "uploaded"
            })
            recs_to_insert.append({
                "rec_id": f"REC-UP-{len(recs_to_insert)+101}",
                "building_id": bid,
                "building_name": bname,
                "category": "energy",
                "title": f"HVAC Load Shifting for {bname}",
                "description": f"AI model flagged unusual peak load ({round(val,1)} kWh) on {ts[:10]}. Set target temp to 24°C.",
                "impact": "High (Energy Reduction)",
                "status": "pending",
                "source": "uploaded",
                "created_at": ts
            })

    # Check water uploaded data
    w_docs = fetch_records(db.water_data, query={"source": "uploaded"}, sort_key="timestamp", reverse=True)
    for w in w_docs:
        val = w.get("value", 0)
        bid = w.get("building_id")
        ts = w.get("timestamp")
        bname = b_map.get(bid, bid)
        dedup_key = (bid, "water", ts)

        if val >= 250.0 and dedup_key not in seen_keys and len([a for a in alerts_to_insert if a["building_id"] == bid and a["metric"] == "water"]) < 2:
            seen_keys.add(dedup_key)
            alert_id = f"ALT-UP-{len(alerts_to_insert)+1001}"
            alerts_to_insert.append({
                "alert_id": alert_id,
                "building_id": bid,
                "building_name": bname,
                "timestamp": ts,
                "created_at": ts,
                "metric": "water",
                "value": round(val, 1),
                "expected_value": 150.0,
                "severity": "high" if val >= 500.0 else "medium",
                "description": f"Unusual water discharge flow of {round(val,1)} L detected in {bname}.",
                "status": "active",
                "source": "uploaded"
            })
            recs_to_insert.append({
                "rec_id": f"REC-UP-{len(recs_to_insert)+101}",
                "building_id": bid,
                "building_name": bname,
                "category": "water",
                "title": f"Pipe Inspection at {bname}",
                "description": f"Elevated water discharge ({round(val,1)} L) detected on {ts[:10]}. Recommend checking flow valves.",
                "impact": "High (Leak Prevention)",
                "status": "pending",
                "source": "uploaded",
                "created_at": ts
            })

    if alerts_to_insert:
        db.alerts.insert_many(alerts_to_insert)
        print(f"Inserted {len(alerts_to_insert)} deduplicated uploaded active alerts.")

    if recs_to_insert:
        db.recommendations.insert_many(recs_to_insert)
        print(f"Inserted {len(recs_to_insert)} deduplicated uploaded recommendations.")

if __name__ == "__main__":
    main()
