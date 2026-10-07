import sys
import os
from datetime import datetime, timezone
import logging

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import get_db, init_indexes
from app.core.security import hash_password
from simulation.sensor_generator import generate_simulation_data

logger = logging.getLogger("smart_campus.seeder")
logging.basicConfig(level=logging.INFO)

def seed_database(force=False):
    db = get_db()
    if db is None:
        logger.error("Database connection unavailable. Aborting seed operation.")
        return False

    init_indexes(db)

    user_count = db.users.count_documents({})
    energy_count = db.energy_data.count_documents({})

    if not force and user_count > 0 and energy_count > 0:
        logger.info(f"Database already seeded ({user_count} users, {energy_count} energy records). Skipping seed step.")
        return True

    logger.info("Starting fresh database seeding process...")

    # 1. Seed Demo Accounts
    logger.info("Seeding demo user accounts...")
    db.users.delete_many({})
    demo_users = [
        {
            "email": "admin@smartcampus.edu",
            "password_hash": hash_password("ALxM21AllspN"),
            "name": "System Administrator",
            "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "email": "staff@smartcampus.edu",
            "password_hash": hash_password("SLxM21AllspF"),
            "name": "Campus Operations Staff",
            "role": "staff",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    db.users.insert_many(demo_users)

    # 2. Seed System Settings
    logger.info("Seeding system settings...")
    db.settings.delete_many({"key": "data_source"})
    db.settings.insert_one({
        "key": "data_source",
        "value": "simulated",
        "updated_at": datetime.now(timezone.utc).isoformat()
    })

    # 3. Generate Simulation Datasets (90 days)
    logger.info("Generating 90 days of synthetic IoT sensor data...")
    sim_data = generate_simulation_data(days=90)

    # 4. Seed Buildings & Facilities
    logger.info("Seeding building metadata and facility records...")
    db.buildings.delete_many({})
    db.buildings.insert_many(sim_data["buildings"])

    db.facilities.delete_many({})
    db.facilities.insert_many(sim_data["facilities"])

    # 5. Chunked batch insertion (batch 5000)
    def batch_insert(collection, records, name):
        collection.delete_many({})
        total = len(records)
        chunk_size = 5000
        inserted = 0
        for i in range(0, total, chunk_size):
            chunk = records[i:i + chunk_size]
            collection.insert_many(chunk)
            inserted += len(chunk)
        logger.info(f"  -> Inserted {inserted} records into '{name}' collection.")

    logger.info("Batch seeding sensor metrics into database...")
    batch_insert(db.energy_data, sim_data["energy"], "energy_data")
    batch_insert(db.water_data, sim_data["water"], "water_data")
    batch_insert(db.traffic_data, sim_data["traffic"], "traffic_data")
    batch_insert(db.occupancy_data, sim_data["occupancy"], "occupancy_data")
    batch_insert(db.parking_data, sim_data["parking"], "parking_data")
    batch_insert(db.facility_utilization, sim_data["facility_utilization"], "facility_utilization")

    # 6. Seed Anomalies, Alerts & Recommendations
    logger.info("Seeding anomalies, alerts and AI recommendations...")
    db.anomalies.delete_many({})
    if sim_data["anomalies"]:
        batch_insert(db.anomalies, sim_data["anomalies"][:500], "anomalies")

    db.alerts.delete_many({})
    initial_alerts = []
    for idx, anomaly in enumerate(sim_data["anomalies"][:25]):
        initial_alerts.append({
            "alert_id": f"ALT-{1000 + idx}",
            "building_id": anomaly["building_id"],
            "building_name": anomaly["building_name"],
            "type": anomaly["metric"],
            "severity": anomaly["severity"],
            "message": anomaly["description"],
            "status": "active",
            "created_at": anomaly["timestamp"],
            "resolution_notes": None
        })
    if initial_alerts:
        db.alerts.insert_many(initial_alerts)

    db.recommendations.delete_many({})
    sample_recommendations = [
        {
            "rec_id": "REC-101",
            "building_id": "B001",
            "building_name": "Academic Block A",
            "category": "energy",
            "title": "Automated HVAC Idle Shutdown",
            "description": "Schedule HVAC automatic setback between 19:00 and 06:00. Estimated savings: 140 kWh/day.",
            "impact": "High (15% energy reduction)",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "rec_id": "REC-102",
            "building_id": "B005",
            "building_name": "Student Hostel North",
            "category": "water",
            "title": "Submetering Inspection for Suspected Leak",
            "description": "Nighttime baseload flow is 3.2x normal. Inspect 2nd-floor washroom pressure valves.",
            "impact": "Critical (Prevents ~1,200L daily waste)",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        },
        {
            "rec_id": "REC-103",
            "building_id": "B007",
            "building_name": "Campus Canteen",
            "category": "traffic",
            "title": "Stagger Lunch Shift Hours",
            "description": "Peak occupancy reaches 94% between 12:30 and 13:15. Staggering department lunch breaks will optimize space and ventilation.",
            "impact": "Medium (Improves comfort score)",
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
    ]
    db.recommendations.insert_many(sample_recommendations)

    logger.info("==========================================================================")
    logger.info("DATABASE SEEDING SUCCESSFULLY COMPLETED!")
    logger.info(f" Total records inserted: ~{len(sim_data['energy']) * 4 + len(sim_data['parking'])}")
    logger.info(" Admin login: admin@smartcampus.edu / ALxM21AllspN")
    logger.info(" Staff login: staff@smartcampus.edu / SLxM21AllspF")
    logger.info("==========================================================================")

    return True

if __name__ == "__main__":
    seed_database(force=True)
