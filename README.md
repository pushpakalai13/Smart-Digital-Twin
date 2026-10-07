# AI Digital Twin for Smart Campus - Predictive Intelligence Platform

> Multi-Resource Predictive Intelligence Platform for Energy, Water, Traffic, Parking, and Facility Operations.

---

## Quick Start (Ready-to-Run in 2 Commands)

### Windows
```cmd
scripts\setup.bat
scripts\start.bat
```

### macOS / Linux
```bash
chmod +x scripts/*.sh
./scripts/setup.sh
./scripts/start.sh
```

---

## Connect MongoDB Atlas (Required Database Setup)

Follow these steps to link your free MongoDB Atlas M0 cluster:

1. **Create Free Atlas Cluster**: Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) and deploy a free **M0 Shared Cluster**.
2. **Create Database User**: Navigate to **Database Access** -> **Add New Database User**. Choose **Password Authentication**, enter a username and password, and assign the `Read and write to any database` role.
3. **Configure Network Access**: Navigate to **Network Access** -> **Add IP Address**. Click **Allow Access from Anywhere** (`0.0.0.0/0`) for development.
4. **Copy Connection String**: Go to **Database** -> **Connect** -> **Drivers**. Select **Python** (version 3.6 or later) and copy the `mongodb+srv://...` string.
5. **URL-Encode Password**: If your password contains special characters (e.g. `@`, `#`, `$`, `%`, `&`, `+`), ensure they are URL-encoded (or rely on `db.py` auto-encoding).
6. **Save to Environment File**: Paste the connection string into `backend/.env`:
   ```ini
   MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
   MONGODB_DB_NAME=smart_campus
   ```
7. **Verify Atlas Connection**: Run the standalone diagnostic tool:
   ```bash
   python scripts/test_atlas.py
   ```

*(Offline Demo Hatch: If you need to run offline without Atlas credentials, set `USE_EMBEDDED_DB=true` in `backend/.env` to switch to local file storage).*

---

## Technical Stack

| Tier | Technologies |
| :--- | :--- |
| **Frontend** | React (Vite), Recharts, Leaflet + OpenStreetMap, Lucide React, Axios, React Dropzone, Tailwind/CSS System |
| **Backend** | Python 3.10+, FastAPI, Pydantic v2, PyMongo + dnspython, Uvicorn, Python-Multipart, OpenPyXL, Certifi |
| **AI / ML** | Pandas, NumPy, scikit-learn, XGBoost, Joblib |
| **Database** | MongoDB Atlas (Primary required DB) / Mongita (Embedded offline fallback) |
| **Security** | JWT Tokens, bcrypt password hashing, Role-based Access Control (Admin, Staff) |

---

## Architecture Overview

```
                          ┌────────────────────────┐
                          │   React (Vite) UI      │
                          │ Leaflet + Recharts     │
                          └───────────┬────────────┘
                                      │ REST API / JWT
                                      ▼
                          ┌────────────────────────┐
                          │   FastAPI Backend      │
                          │   Router Pipeline      │
                          └─────┬────────────┬─────┘
                                │            │
                      ┌─────────▼──┐      ┌──▼───────────┐
                      │ ML Engine  │      │ PyMongo + TLS│
                      │ XGBoost/RF │      └──────┬───────┘
                      └────────────┘             │
                                                 ▼
                                     ┌──────────────────────┐
                                     │ MongoDB Atlas Cloud  │
                                     └──────────────────────┘
```

---

## Demo Accounts

| Role | Email | Password | Privileges |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@smartcampus.edu` | `ALxM21AllspN` | Full access: Dataset Upload, CSV Import, Data Delete, ML Retrain |
| **Staff** | `staff@smartcampus.edu` | `SLxM21AllspF` | Operational view: Dashboard, Digital Twin, Analytics, Alerts Resolve |

---

## Machine Learning Methodology & Performance

The platform evaluates three distinct regressors (**Linear Regression**, **Random Forest**, and **XGBoost**) for time-series load forecasting. The best-performing model is dynamically chosen per metric by highest $R^2$ score.

| Target Metric | Selected Model | $R^2$ Score | MAE | RMSE | Anomaly Detector |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Energy Load (kWh)** | XGBoost Regressor | `0.606` | `8.45` | `11.20` | Isolation Forest |
| **Water Demand (L)** | XGBoost Regressor | `0.775` | `42.10` | `58.30` | Isolation Forest |
| **Traffic Flow (Vehicles)** | Random Forest | `0.954` | `5.60` | `7.80` | Dynamic Threshold |

---

## API Documentation Summary

| Method | Path | Description | Access |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/auth/login` | User login token generation | Public |
| `GET` | `/api/health` | Health check & Atlas ping status | Public |
| `GET` | `/api/dashboard` | KPI metrics, efficiency score & sparklines | Authenticated |
| `GET` | `/api/digital-twin` | Geospatial campus map state & live telemetry | Authenticated |
| `GET` | `/api/energy/predict/{id}`| 24h AI energy load forecast | Authenticated |
| `GET` | `/api/water/predict/{id}` | 24h AI water demand forecast | Authenticated |
| `PUT` | `/api/alerts/{id}/resolve`| Resolve active anomaly alert | Authenticated |
| `POST` | `/api/datasets/upload` | Multipart CSV/XLSX file upload & validation | Admin Only |
| `POST` | `/api/datasets/{id}/import`| Commit validated data to Atlas in batches | Admin Only |
| `DELETE`|`/api/datasets/{id}` | Rollback dataset & remove document rows | Admin Only |
| `POST` | `/api/ml/retrain` | Trigger ML model retraining background job | Admin Only |

---

## Sample CSV Dataset Formats

All sample files are stored in `/sample_data/` and accessible via the Data Management tab.

### Energy Dataset (`energy_sample.csv`)
```csv
building_id,timestamp,value,unit
B001,2026-09-01T08:00:00,145.5,kWh
B001,2026-09-01T09:00:00,210.0,kWh
```

### Water Dataset (`water_sample.csv`)
```csv
building_id,timestamp,value,unit
B001,2026-09-01T08:00:00,1200.5,L
B005,2026-09-01T08:00:00,3400.0,L
```

---

## Troubleshooting Guide

1. **MongoDB Atlas Connection Timeout / ServerSelectionTimeoutError**:
   - Ensure your IP address is whitelisted under **Network Access** in Atlas (`0.0.0.0/0` for dev).
   - If your password contains `@` or `#`, encode them (e.g. `@` -> `%40`).
2. **PyMongo TLS / SSL Certificate Error**:
   - The application relies on `certifi` CA bundle. Ensure `certifi` is installed (`pip install certifi`).
3. **Port 8000 or 5173 Already in Use**:
   - Kill existing processes using the ports or change `VITE_API_URL` and uvicorn port in `.env`.
