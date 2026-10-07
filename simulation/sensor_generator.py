import random
import math
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

BUILDINGS = [
    {"building_id": "B001", "name": "Academic Block A", "category": "academic", "capacity": 1500, "floors": 5, "area_sqft": 75000, "coordinates": {"lat": 12.9716, "lng": 77.5946}},
    {"building_id": "B002", "name": "Academic Block B", "category": "academic", "capacity": 1200, "floors": 4, "area_sqft": 60000, "coordinates": {"lat": 12.9722, "lng": 77.5952}},
    {"building_id": "B003", "name": "Central Library", "category": "library", "capacity": 800, "floors": 3, "area_sqft": 45000, "coordinates": {"lat": 12.9730, "lng": 77.5940}},
    {"building_id": "B004", "name": "Administrative Complex", "category": "admin", "capacity": 300, "floors": 3, "area_sqft": 30000, "coordinates": {"lat": 12.9710, "lng": 77.5935}},
    {"building_id": "B005", "name": "Student Hostel North", "category": "hostel", "capacity": 600, "floors": 6, "area_sqft": 50000, "coordinates": {"lat": 12.9740, "lng": 77.5960}},
    {"building_id": "B006", "name": "Student Hostel South", "category": "hostel", "capacity": 600, "floors": 6, "area_sqft": 50000, "coordinates": {"lat": 12.9705, "lng": 77.5965}},
    {"building_id": "B007", "name": "Campus Canteen & Food Court", "category": "canteen", "capacity": 500, "floors": 2, "area_sqft": 25000, "coordinates": {"lat": 12.9725, "lng": 77.5930}},
    {"building_id": "B008", "name": "Indoor Sports Complex", "category": "sports", "capacity": 400, "floors": 2, "area_sqft": 35000, "coordinates": {"lat": 12.9735, "lng": 77.5970}},
    {"building_id": "B009", "name": "Advanced Research Labs", "category": "labs", "capacity": 350, "floors": 4, "area_sqft": 40000, "coordinates": {"lat": 12.9700, "lng": 77.5950}},
    {"building_id": "B010", "name": "Technology Innovation Hub", "category": "labs", "capacity": 450, "floors": 4, "area_sqft": 45000, "coordinates": {"lat": 12.9745, "lng": 77.5938}},
]

FACILITIES = [
    {"facility_id": "F001", "name": "Main Auditorium", "building_id": "B001", "type": "auditorium", "capacity": 500},
    {"facility_id": "F002", "name": "Conference Hall 1", "building_id": "B004", "type": "conference", "capacity": 100},
    {"facility_id": "F003", "name": "AI & Robotics Lab", "building_id": "B010", "type": "lab", "capacity": 60},
    {"facility_id": "F004", "name": "Gymnasium & Fitness", "building_id": "B008", "type": "gym", "capacity": 150},
    {"facility_id": "F005", "name": "Central Server Room", "building_id": "B009", "type": "datacenter", "capacity": 20},
]

def generate_simulation_data(days=180):
    """Generates 6 months of hourly synthetic sensor data with patterns and ~1.5% anomalies."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    timestamps = []
    curr = start_date.replace(minute=0, second=0, microsecond=0)
    while curr <= end_date:
        timestamps.append(curr)
        curr += timedelta(hours=1)

    energy_records = []
    water_records = []
    traffic_records = []
    occupancy_records = []
    parking_records = []
    facility_records = []
    anomaly_records = []

    random.seed(42)
    np.random.seed(42)

    for dt in timestamps:
        ts_str = dt.isoformat()
        hour = dt.hour
        is_weekend = dt.weekday() >= 5
        month = dt.month
        # Seasonal factor (higher in summer/hottest months like May/June)
        seasonal_mult = 1.0 + 0.15 * math.sin((month - 3) * math.pi / 6)

        # Parking (Campus wide)
        base_parking = 300 if is_weekend else 750
        if 8 <= hour <= 18:
            park_factor = math.sin((hour - 8) * math.pi / 10)
        else:
            park_factor = 0.1
        parking_val = max(10, int(base_parking * park_factor + random.gauss(0, 25)))
        parking_records.append({
            "timestamp": ts_str,
            "total_slots": 1000,
            "occupied_slots": min(1000, parking_val),
            "occupancy_rate": round(min(1.0, parking_val / 1000.0), 4),
            "source": "simulated"
        })

        for b in BUILDINGS:
            bid = b["building_id"]
            cat = b["category"]
            sqft = b["area_sqft"]
            cap = b["capacity"]

            # Occupancy pattern
            if is_weekend:
                if cat == "hostel":
                    occ_pct = 0.65 + 0.2 * math.sin(hour * math.pi / 12)
                elif cat == "sports":
                    occ_pct = 0.40 if 9 <= hour <= 20 else 0.05
                else:
                    occ_pct = 0.08 + random.uniform(0, 0.05)
            else:
                if cat in ["academic", "admin", "labs"]:
                    occ_pct = 0.85 * math.sin((hour - 7) * math.pi / 11) if 8 <= hour <= 18 else 0.05
                elif cat == "library":
                    occ_pct = 0.80 * math.sin((hour - 8) * math.pi / 13) if 8 <= hour <= 21 else 0.03
                elif cat == "canteen":
                    occ_pct = 0.90 if 12 <= hour <= 14 or 19 <= hour <= 21 else 0.15
                elif cat == "hostel":
                    occ_pct = 0.85 if hour <= 7 or hour >= 20 else 0.30
                else:
                    occ_pct = 0.50 if 10 <= hour <= 19 else 0.05

            occ_pct = max(0.01, min(1.0, occ_pct + random.gauss(0, 0.04)))
            occupancy_val = int(cap * occ_pct)

            # Base Energy (kWh)
            base_kwh = (sqft / 1000.0) * (2.5 + occ_pct * 4.0) * seasonal_mult
            # Base Water (Litres)
            base_litres = occupancy_val * random.uniform(12.0, 18.0) + (sqft / 500.0)
            # Base Traffic (vehicles near building)
            base_traffic = int(occupancy_val * 0.25 * (1.2 if 8 <= hour <= 10 or 17 <= hour <= 19 else 0.4))

            # Inject ~1.5% Anomaly
            is_energy_anomaly = random.random() < 0.015
            is_water_anomaly = random.random() < 0.015

            if is_energy_anomaly:
                energy_val = base_kwh * random.uniform(2.5, 4.0)
                anomaly_records.append({
                    "building_id": bid,
                    "building_name": b["name"],
                    "timestamp": ts_str,
                    "metric": "energy",
                    "value": round(energy_val, 2),
                    "expected_value": round(base_kwh, 2),
                    "severity": "high" if energy_val > base_kwh * 3 else "medium",
                    "description": f"Unusual energy spike of {round(energy_val, 1)} kWh detected in {b['name']} during off-peak hours.",
                    "status": "active",
                    "source": "simulated"
                })
            else:
                energy_val = max(5.0, base_kwh + random.gauss(0, base_kwh * 0.08))

            if is_water_anomaly:
                water_val = base_litres * random.uniform(3.0, 5.0)
                anomaly_records.append({
                    "building_id": bid,
                    "building_name": b["name"],
                    "timestamp": ts_str,
                    "metric": "water",
                    "value": round(water_val, 2),
                    "expected_value": round(base_litres, 2),
                    "severity": "high",
                    "description": f"Continuous high water flow ({round(water_val, 1)} L) detected in {b['name']} - possible pipe leakage.",
                    "status": "active",
                    "source": "simulated"
                })
            else:
                water_val = max(10.0, base_litres + random.gauss(0, base_litres * 0.1))

            traffic_val = max(0, base_traffic + int(random.gauss(0, 5)))

            energy_records.append({
                "building_id": bid,
                "timestamp": ts_str,
                "value": round(energy_val, 2),
                "unit": "kWh",
                "source": "simulated"
            })
            water_records.append({
                "building_id": bid,
                "timestamp": ts_str,
                "value": round(water_val, 2),
                "unit": "L",
                "source": "simulated"
            })
            traffic_records.append({
                "building_id": bid,
                "timestamp": ts_str,
                "value": float(traffic_val),
                "unit": "vehicles",
                "source": "simulated"
            })
            occupancy_records.append({
                "building_id": bid,
                "timestamp": ts_str,
                "occupancy_count": occupancy_val,
                "capacity": cap,
                "occupancy_rate": round(occ_pct, 4),
                "source": "simulated"
            })

        for f in FACILITIES:
            fid = f["facility_id"]
            f_cap = f["capacity"]
            f_occ = int(f_cap * max(0.0, min(1.0, math.sin(hour * math.pi / 12) * (0.1 if is_weekend else 0.7) + random.gauss(0, 0.05))))
            facility_records.append({
                "facility_id": fid,
                "timestamp": ts_str,
                "occupied_seats": f_occ,
                "total_capacity": f_cap,
                "utilization_rate": round(f_occ / max(1, f_cap), 4),
                "source": "simulated"
            })

    return {
        "buildings": BUILDINGS,
        "facilities": FACILITIES,
        "energy": energy_records,
        "water": water_records,
        "traffic": traffic_records,
        "occupancy": occupancy_records,
        "parking": parking_records,
        "facility_utilization": facility_records,
        "anomalies": anomaly_records
    }
