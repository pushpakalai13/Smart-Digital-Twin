from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from app.db import get_db, fetch_records
from app.core.security import get_current_user
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from ml.pipeline import compute_campus_efficiency_score

router = APIRouter(tags=["Dashboard & Digital Twin"])

def get_active_source(db):
    setting = db.settings.find_one({"key": "data_source"})
    return setting.get("value", "simulated") if setting else "simulated"

@router.get("/dashboard")
def get_dashboard_summary(source: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = source or get_active_source(db)
    query = {"source": active_src} if active_src else {}

    energy_cursor = fetch_records(db.energy_data, query=query, sort_key="timestamp", reverse=True, limit=240)
    water_cursor = fetch_records(db.water_data, query=query, sort_key="timestamp", reverse=True, limit=240)
    traffic_cursor = fetch_records(db.traffic_data, query=query, sort_key="timestamp", reverse=True, limit=240)
    parking_cursor = fetch_records(db.parking_data, query=query, sort_key="timestamp", reverse=True, limit=24)

    total_energy = sum([e.get("value", 0) for e in energy_cursor[:24]])
    total_water = sum([w.get("value", 0) for w in water_cursor[:24]])
    avg_traffic = sum([t.get("value", 0) for t in traffic_cursor[:24]]) / max(1, len(traffic_cursor[:24]))
    latest_parking = parking_cursor[0] if parking_cursor else {"occupancy_rate": 0.65}

    active_alerts_count = db.alerts.count_documents({"status": "active", "source": active_src})
    if active_alerts_count == 0 and active_src != "uploaded":
        active_alerts_count = db.alerts.count_documents({"status": "active"})

    efficiency_score = compute_campus_efficiency_score(db, source=active_src)

    energy_trend = [round(e.get("value", 0), 1) for e in energy_cursor[:12]][::-1]
    water_trend = [round(w.get("value", 0), 1) for w in water_cursor[:12]][::-1]
    traffic_trend = [int(t.get("value", 0)) for t in traffic_cursor[:12]][::-1]

    recent_alerts = fetch_records(db.alerts, query={"source": active_src}, sort_key="created_at", reverse=True, limit=5)
    if not recent_alerts and active_src != "uploaded":
        recent_alerts = fetch_records(db.alerts, sort_key="created_at", reverse=True, limit=5)

    for a in recent_alerts:
        metric_val = a.get("metric") or a.get("type") or "general"
        desc_val = a.get("description") or a.get("message") or "System anomaly detected."
        a["metric"] = metric_val
        a["type"] = metric_val
        a["description"] = desc_val
        a["message"] = desc_val

    top_recs = fetch_records(db.recommendations, query={"status": "pending", "source": active_src}, sort_key="created_at", reverse=True, limit=3)
    if not top_recs and active_src != "uploaded":
        top_recs = fetch_records(db.recommendations, query={"status": "pending"}, sort_key="created_at", reverse=True, limit=3)

    return {
        "source": active_src,
        "efficiency_score": efficiency_score,
        "kpis": {
            "energy": {"total_kwh_24h": round(total_energy, 1), "trend": energy_trend, "change_pct": -3.2},
            "water": {"total_litres_24h": round(total_water, 1), "trend": water_trend, "change_pct": +1.5},
            "traffic": {"avg_vehicles_per_hr": round(avg_traffic, 1), "trend": traffic_trend, "change_pct": +4.1},
            "parking": {"occupancy_rate": round(latest_parking.get("occupancy_rate", 0.65) * 100, 1)},
            "alerts": {"active_count": active_alerts_count}
        },
        "recent_alerts": recent_alerts,
        "top_recommendations": top_recs
    }

@router.get("/digital-twin")
def get_digital_twin_state(current_user: dict = Depends(get_current_user)):
    db = get_db()
    if db is None:
        raise HTTPException(status_code=500, detail="Database unavailable")

    active_src = get_active_source(db)
    buildings = fetch_records(db.buildings, sort_key="building_id", reverse=False)
    facilities = fetch_records(db.facilities, sort_key="facility_id", reverse=False)
    active_alerts = fetch_records(db.alerts, query={"status": "active"}, sort_key="created_at", reverse=True)
    active_src_alerts = [a for a in active_alerts if a.get("source") == active_src]

    for b in buildings:
        bid = b["building_id"]

        # Normalize coordinates
        lat = float(b.get("lat") or b.get("coordinates", {}).get("lat", 12.9720))
        lng = float(b.get("lng") or b.get("coordinates", {}).get("lng", 77.5940))
        b["lat"] = lat
        b["lng"] = lng
        b["coordinates"] = {"lat": lat, "lng": lng}

        # Query latest records prioritizing active dataset source
        latest_e = fetch_records(db.energy_data, query={"building_id": bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
        if not latest_e:
            latest_e = fetch_records(db.energy_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=1)

        latest_w = fetch_records(db.water_data, query={"building_id": bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
        if not latest_w:
            latest_w = fetch_records(db.water_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=1)

        latest_o = fetch_records(db.occupancy_data, query={"building_id": bid, "source": active_src}, sort_key="timestamp", reverse=True, limit=1)
        if not latest_o:
            latest_o = fetch_records(db.occupancy_data, query={"building_id": bid}, sort_key="timestamp", reverse=True, limit=1)

        e_rec = latest_e[0] if latest_e else None
        w_rec = latest_w[0] if latest_w else None
        o_rec = latest_o[0] if latest_o else None

        e_val = round(e_rec["value"], 1) if e_rec else 0.0
        w_val = round(w_rec["value"], 1) if w_rec else 0.0
        o_count = o_rec["occupancy_count"] if (o_rec and "occupancy_count" in o_rec) else 0
        b_cap = b.get("capacity", 500) or 500

        if o_rec and "occupancy_rate" in o_rec:
            o_rate = round(o_rec["occupancy_rate"] * 100, 1)
        elif o_rec and "occupancy_count" in o_rec:
            o_rate = round((o_count / b_cap) * 100, 1)
        else:
            o_rate = 0.0

        b["metrics"] = {
            "energy_kwh": e_val,
            "water_litres": w_val,
            "occupancy_count": o_count,
            "occupancy_rate": o_rate
        }

        b_alerts = [a for a in active_src_alerts if a.get("building_id") == bid]

        # Real-time status threshold rules:
        # Energy: >= 150 kWh Critical, >= 70 kWh Warning
        # Water: >= 500 L Critical, >= 250 L Warning
        # Occupancy: >= 90% Critical, >= 75% Warning
        reasons = []
        actions = []
        is_critical = False
        is_warning = False

        if e_val >= 150.0:
            reasons.append(f"High Energy Load ({e_val} kWh >= 150 kWh)")
            actions.append("Recommend HVAC/equipment audit; consider load shedding during peak hours.")
            is_critical = True
        elif e_val >= 70.0:
            reasons.append(f"Elevated Energy Load ({e_val} kWh >= 70 kWh)")
            actions.append("Recommend HVAC/equipment audit; consider load shedding during peak hours.")
            is_warning = True

        if w_val >= 500.0:
            reasons.append(f"Critical Water Discharge ({w_val} L >= 500 L)")
            actions.append("Possible pipe leak - recommend immediate plumbing inspection, especially if flow is elevated during off-peak hours.")
            is_critical = True
        elif w_val >= 250.0:
            reasons.append(f"Elevated Water Discharge ({w_val} L >= 250 L)")
            actions.append("Possible pipe leak - recommend immediate plumbing inspection, especially if flow is elevated during off-peak hours.")
            is_warning = True

        if o_rate >= 90.0:
            reasons.append(f"Critical High Occupancy ({o_rate}% >= 90%)")
            actions.append("Approaching capacity - recommend staggering schedules or restricting further entry.")
            is_critical = True
        elif o_rate >= 75.0:
            reasons.append(f"High Occupancy Rate ({o_rate}% >= 75%)")
            actions.append("Approaching capacity - recommend staggering schedules or restricting further entry.")
            is_warning = True

        if is_critical:
            b["status"] = "critical"
        elif is_warning:
            b["status"] = "warning"
        else:
            b["status"] = "normal"

        b["status_reasons"] = reasons
        b["recommended_actions"] = list(dict.fromkeys(actions))
        b["active_alerts_count"] = len(b_alerts)

    return {
        "source": active_src,
        "buildings": buildings,
        "facilities": facilities,
        "active_alerts": active_src_alerts
    }
