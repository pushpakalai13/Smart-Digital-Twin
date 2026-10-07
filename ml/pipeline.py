import os
import sys
import json
import logging
from datetime import datetime, timezone
import pandas as pd
import numpy as np
import joblib

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, IsolationForest
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db

logger = logging.getLogger("smart_campus.ml")
logging.basicConfig(level=logging.INFO)

MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODEL_DIR, exist_ok=True)

def prepare_features(df, value_col="value"):
    """Engineers time-series features: hour, dayofweek, month, is_weekend, lag_1."""
    if df.empty or value_col not in df.columns or "timestamp" not in df.columns:
        return None, None

    df["dt"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("dt").reset_index(drop=True)

    df["hour"] = df["dt"].dt.hour
    df["dayofweek"] = df["dt"].dt.dayofweek
    df["month"] = df["dt"].dt.month
    df["is_weekend"] = df["dayofweek"].apply(lambda d: 1 if d >= 5 else 0)

    if "building_id" in df.columns:
        df["b_code"] = pd.factorize(df["building_id"])[0]
    else:
        df["b_code"] = 0

    df["lag_1"] = df.groupby("b_code")[value_col].shift(1)
    df = df.dropna().reset_index(drop=True)

    feature_cols = ["hour", "dayofweek", "month", "is_weekend", "b_code", "lag_1"]
    X = df[feature_cols]
    y = df[value_col]
    return X, y

def train_and_eval_target(df, target_name, value_col="value"):
    X, y = prepare_features(df, value_col)
    if X is None or len(X) < 50:
        logger.warning(f"Insufficient data to train ML model for target: {target_name}")
        return None

    split_idx = int(len(X) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    candidates = {
        "linear_regression": LinearRegression(),
        "random_forest": RandomForestRegressor(n_estimators=50, random_state=42),
        "xgboost": XGBRegressor(n_estimators=50, max_depth=5, learning_rate=0.1, random_state=42)
    }

    best_name = None
    best_model = None
    best_r2 = -float("inf")
    metrics_all = {}

    for name, model in candidates.items():
        try:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            r2 = float(r2_score(y_test, preds))
            mae = float(mean_absolute_error(y_test, preds))
            rmse = float(np.sqrt(mean_squared_error(y_test, preds)))

            metrics_all[name] = {"r2": round(r2, 4), "mae": round(mae, 4), "rmse": round(rmse, 4)}

            if r2 > best_r2:
                best_r2 = r2
                best_name = name
                best_model = model
        except Exception as e:
            logger.error(f"Error training {name} for {target_name}: {e}")

    if best_model is not None:
        model_filename = f"{target_name}_forecaster.joblib"
        joblib.dump(best_model, os.path.join(MODEL_DIR, model_filename))
        logger.info(f"Selected best model for {target_name}: '{best_name}' (R2={best_r2:.4f})")
        return {
            "selected_model": best_name,
            "metrics": metrics_all[best_name],
            "comparison": metrics_all,
            "model_path": model_filename
        }
    return None

def train_anomaly_detector(df, target_name, value_col="value"):
    X, _ = prepare_features(df, value_col)
    if X is None or len(X) < 50:
        return None

    iso = IsolationForest(contamination=0.02, random_state=42)
    iso.fit(X)
    model_filename = f"{target_name}_anomaly_detector.joblib"
    joblib.dump(iso, os.path.join(MODEL_DIR, model_filename))
    return model_filename

def run_ml_pipeline(source="simulated"):
    logger.info(f"Starting ML Training Pipeline (Source mode: '{source}')...")
    db = get_db()
    if db is None:
        logger.error("Database connection unavailable for ML pipeline.")
        return False

    query = {"source": source} if source else {}

    # Fetch docs safely for PyMongo and Mongita
    energy_docs = list(db.energy_data.find(query))
    water_docs = list(db.water_data.find(query))
    traffic_docs = list(db.traffic_data.find(query))
    occupancy_docs = list(db.occupancy_data.find(query))

    for d in energy_docs: d.pop("_id", None)
    for d in water_docs: d.pop("_id", None)
    for d in traffic_docs: d.pop("_id", None)
    for d in occupancy_docs: d.pop("_id", None)

    metrics_summary = {}

    if energy_docs:
        df_e = pd.DataFrame(energy_docs)
        metrics_summary["energy"] = train_and_eval_target(df_e, "energy", "value")
        train_anomaly_detector(df_e, "energy", "value")

    if water_docs:
        df_w = pd.DataFrame(water_docs)
        metrics_summary["water"] = train_and_eval_target(df_w, "water", "value")
        train_anomaly_detector(df_w, "water", "value")

    if traffic_docs:
        df_t = pd.DataFrame(traffic_docs)
        metrics_summary["traffic"] = train_and_eval_target(df_t, "traffic", "value")

    if occupancy_docs:
        df_o = pd.DataFrame(occupancy_docs)
        val_col = "occupancy_count" if "occupancy_count" in df_o.columns else ("value" if "value" in df_o.columns else "occupancy_rate")
        metrics_summary["occupancy"] = train_and_eval_target(df_o, "occupancy", val_col)
        train_anomaly_detector(df_o, "occupancy", val_col)

    metrics_summary["last_trained"] = datetime.now(timezone.utc).isoformat()
    metrics_summary["source"] = source
    metrics_path = os.path.join(MODEL_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_summary, f, indent=2)

    logger.info(f"ML Pipeline complete. Metrics written to: {metrics_path}")
    return True

def compute_campus_efficiency_score(db, source=None) -> float:
    try:
        if source is None:
            setting = db.settings.find_one({"key": "data_source"})
            source = setting.get("value", "simulated") if setting else "simulated"

        active_alerts = db.alerts.count_documents({"status": "active", "source": source})
        if active_alerts == 0 and source != "uploaded":
            active_alerts = db.alerts.count_documents({"status": "active"})

        score = 98.0 - (active_alerts * 1.2)
        return max(60.0, min(100.0, round(score, 1)))
    except Exception:
        return 92.5

def generate_automated_recommendations(db):
    recs = []
    recent_anomalies = list(db.anomalies.find({"status": "active"}))[:10]
    for a in recent_anomalies:
        if a.get("metric") == "water":
            recs.append({
                "rec_id": f"REC-AUTO-{len(recs)+100}",
                "building_id": a["building_id"],
                "building_name": a["building_name"],
                "category": "water",
                "title": "Immediate Pipe & Meter Leakage Inspection",
                "description": f"AI model flagged unusual water discharge ({a['value']} L). Recommend dispatching maintenance team.",
                "impact": "High (Leak Prevention)",
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            })
        elif a.get("metric") == "energy":
            recs.append({
                "rec_id": f"REC-AUTO-{len(recs)+100}",
                "building_id": a["building_id"],
                "building_name": a["building_name"],
                "category": "energy",
                "title": "HVAC Cooling Optimization & Load Shifting",
                "description": f"Unusual off-peak energy consumption ({a['value']} kWh). Recommend setting thermostat target to 24°C.",
                "impact": "Medium (Energy Reduction)",
                "status": "pending",
                "created_at": datetime.now(timezone.utc).isoformat()
            })

    if recs:
        for r in recs:
            db.recommendations.update_one(
                {"rec_id": r["rec_id"]},
                {"$set": r},
                upsert=True
            )

if __name__ == "__main__":
    run_ml_pipeline("simulated")
