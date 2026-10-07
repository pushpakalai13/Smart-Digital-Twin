import os
import random
import math
from datetime import datetime, timedelta

sample_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sample_data"))
os.makedirs(sample_dir, exist_ok=True)

buildings = ["B001", "B002", "B003", "B004", "B005", "B006", "B007", "B008", "B009", "B010"]

start_dt = datetime(2026, 9, 1, 0, 0, 0)

# 1. ENERGY CLEAN
energy_clean_lines = ["building_id,timestamp,value,unit\n"]
for i in range(168):
    dt = start_dt + timedelta(hours=i)
    b_id = buildings[i % 5]
    hr = dt.hour
    is_wknd = dt.weekday() >= 5
    mult = 0.5 if is_wknd else (1.8 if 8 <= hr <= 18 else 0.6)
    val = round(120.0 * mult + random.gauss(0, 10), 2)
    energy_clean_lines.append(f"{b_id},{dt.isoformat()},{max(15.0, val)},kWh\n")

with open(os.path.join(sample_dir, "energy_sample_clean.csv"), "w") as f:
    f.writelines(energy_clean_lines)

# 1. ENERGY WITH ERRORS
energy_err_lines = list(energy_clean_lines)
energy_err_lines[15] = f"B999,{start_dt + timedelta(hours=15)},210.5,kWh\n"  # Unknown building ID warning
energy_err_lines[42] = f"B001,INVALID_DATE_2026,240.0,kWh\n"  # Invalid timestamp error
energy_err_lines[88] = f"B002,{(start_dt + timedelta(hours=88)).isoformat()},-150.0,kWh\n"  # Negative value error
energy_err_lines[110] = f"B003,{(start_dt + timedelta(hours=110)).isoformat()},ABC_VAL,kWh\n"  # Non-numeric error

with open(os.path.join(sample_dir, "energy_sample_with_errors.csv"), "w") as f:
    f.writelines(energy_err_lines)


# 2. WATER CLEAN
water_clean_lines = ["building_id,timestamp,value,unit\n"]
for i in range(168):
    dt = start_dt + timedelta(hours=i)
    b_id = buildings[i % 6]
    hr = dt.hour
    is_wknd = dt.weekday() >= 5
    mult = 0.7 if is_wknd else (2.0 if 7 <= hr <= 10 or 17 <= hr <= 21 else 0.4)
    val = round(950.0 * mult + random.gauss(0, 50), 2)
    water_clean_lines.append(f"{b_id},{dt.isoformat()},{max(50.0, val)},L\n")

with open(os.path.join(sample_dir, "water_sample_clean.csv"), "w") as f:
    f.writelines(water_clean_lines)

# 2. WATER WITH ERRORS
water_err_lines = list(water_clean_lines)
water_err_lines[20] = f"UNKNOWN_BLD,{(start_dt + timedelta(hours=20)).isoformat()},1200.0,L\n"
water_err_lines[50] = f"B001,BAD_TIMESTAMP_STRING,1500.0,L\n"
water_err_lines[95] = f"B005,{(start_dt + timedelta(hours=95)).isoformat()},-800.0,L\n"

with open(os.path.join(sample_dir, "water_sample_with_errors.csv"), "w") as f:
    f.writelines(water_err_lines)


# 3. TRAFFIC CLEAN
traffic_clean_lines = ["building_id,timestamp,value,unit\n"]
for i in range(168):
    dt = start_dt + timedelta(hours=i)
    b_id = buildings[i % 4]
    hr = dt.hour
    is_wknd = dt.weekday() >= 5
    val = 15 if is_wknd else (110 if 8 <= hr <= 10 or 17 <= hr <= 19 else 35)
    traffic_clean_lines.append(f"{b_id},{dt.isoformat()},{val},vehicles\n")

with open(os.path.join(sample_dir, "traffic_sample_clean.csv"), "w") as f:
    f.writelines(traffic_clean_lines)

# 3. TRAFFIC WITH ERRORS
traffic_err_lines = list(traffic_clean_lines)
traffic_err_lines[30] = f"B888,{(start_dt + timedelta(hours=30)).isoformat()},85,vehicles\n"
traffic_err_lines[70] = f"B001,2026-99-99T99:99,90,vehicles\n"
traffic_err_lines[120] = f"B004,{(start_dt + timedelta(hours=120)).isoformat()},-45,vehicles\n"

with open(os.path.join(sample_dir, "traffic_sample_with_errors.csv"), "w") as f:
    f.writelines(traffic_err_lines)


# 4. OCCUPANCY CLEAN
occ_clean_lines = ["building_id,timestamp,occupancy_count,capacity,occupancy_rate\n"]
for i in range(168):
    dt = start_dt + timedelta(hours=i)
    b_id = buildings[i % 5]
    cap = 1000
    hr = dt.hour
    occ = int(cap * (0.8 if 9 <= hr <= 17 else 0.1))
    occ_clean_lines.append(f"{b_id},{dt.isoformat()},{occ},{cap},{round(occ/cap, 4)}\n")

with open(os.path.join(sample_dir, "occupancy_sample_clean.csv"), "w") as f:
    f.writelines(occ_clean_lines)

# 4. OCCUPANCY WITH ERRORS
occ_err_lines = list(occ_clean_lines)
occ_err_lines[25] = f"B999,{(start_dt + timedelta(hours=25)).isoformat()},500,1000,0.5\n"
occ_err_lines[60] = f"B001,INVALID_DATE,400,1000,0.4\n"
occ_err_lines[105] = f"B002,{(start_dt + timedelta(hours=105)).isoformat()},-200,1000,0.2\n"

with open(os.path.join(sample_dir, "occupancy_sample_with_errors.csv"), "w") as f:
    f.writelines(occ_err_lines)


# 5. PARKING CLEAN
park_clean_lines = ["timestamp,total_slots,occupied_slots,occupancy_rate\n"]
for i in range(168):
    dt = start_dt + timedelta(hours=i)
    hr = dt.hour
    occ_slots = int(1000 * (0.85 if 8 <= hr <= 17 else 0.2))
    park_clean_lines.append(f"{dt.isoformat()},1000,{occ_slots},{round(occ_slots/1000.0, 4)}\n")

with open(os.path.join(sample_dir, "parking_sample_clean.csv"), "w") as f:
    f.writelines(park_clean_lines)

# 5. PARKING WITH ERRORS
park_err_lines = list(park_clean_lines)
park_err_lines[18] = f"CORRUPTED_TIMESTAMP,1000,500,0.5\n"
park_err_lines[75] = f"{(start_dt + timedelta(hours=75)).isoformat()},1000,-300,-0.3\n"

with open(os.path.join(sample_dir, "parking_sample_with_errors.csv"), "w") as f:
    f.writelines(park_err_lines)


# 6. BUILDINGS CLEAN
bld_clean_lines = [
    "building_id,name,category,capacity,floors,area_sqft,lat,lng\n",
    "B011,New BioTech Innovation Complex,labs,600,5,65000,12.9755,77.5960\n",
    "B012,Student Activity & Cultural Center,sports,400,3,35000,12.9712,77.5978\n",
    "B013,Graduate Computing & Data Center,labs,500,4,48000,12.9740,77.5945\n",
    "B014,Campus Wellness & Medical Clinic,admin,250,2,22000,12.9708,77.5930\n"
]
with open(os.path.join(sample_dir, "buildings_sample_clean.csv"), "w") as f:
    f.writelines(bld_clean_lines)

# 6. BUILDINGS WITH ERRORS
bld_err_lines = [
    "building_id,name,category,capacity,floors,area_sqft,lat,lng\n",
    "B011,New BioTech Innovation Complex,labs,600,5,65000,12.9755,77.5960\n",
    "B012,BAD_LATLNG_BUILDING,sports,-400,3,35000,999.00,999.00\n",  # Negative capacity
    "B013,INVALID_LAT_BUILDING,labs,500,4,48000,INVALID_LAT,77.5945\n" # Invalid coordinate
]
with open(os.path.join(sample_dir, "buildings_sample_with_errors.csv"), "w") as f:
    f.writelines(bld_err_lines)

print("Generated 12 clean and error sample datasets successfully in sample_data/")
