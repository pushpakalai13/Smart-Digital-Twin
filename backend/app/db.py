import logging
import urllib.parse
from typing import Tuple, Dict, Any, Optional, List
import certifi
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from app.core.config import settings

logger = logging.getLogger("smart_campus.db")
logging.basicConfig(level=logging.INFO)

_client: Optional[Any] = None
_db: Optional[Any] = None
_db_status: str = "disconnected"

def mask_uri(uri: str) -> str:
    """Mask credentials in MongoDB connection string for safe logging."""
    if not uri:
        return "<EMPTY_URI>"
    try:
        if "://" in uri:
            prefix, rest = uri.split("://", 1)
            if "@" in rest:
                creds, host_part = rest.split("@", 1)
                return f"{prefix}://****:****@{host_part}"
    except Exception:
        pass
    return "mongodb+srv://****:****@masked_host"

def encode_mongo_uri(uri: str) -> str:
    """Auto URL-encode username and password in MongoDB connection URI if unencoded."""
    if not uri or "://" not in uri or "@" not in uri:
        return uri
    try:
        scheme, rest = uri.split("://", 1)
        creds, host_and_params = rest.split("@", 1)
        if ":" in creds:
            username, password = creds.split(":", 1)
            username_unquoted = urllib.parse.unquote(username)
            password_unquoted = urllib.parse.unquote(password)
            encoded_user = urllib.parse.quote_plus(username_unquoted)
            encoded_pass = urllib.parse.quote_plus(password_unquoted)
            return f"{scheme}://{encoded_user}:{encoded_pass}@{host_and_params}"
    except Exception as e:
        logger.warning(f"URI encoding attempt skipped: {e}")
    return uri

def init_db() -> Tuple[Any, str]:
    global _client, _db, _db_status

    if settings.USE_EMBEDDED_DB:
        logger.info("USE_EMBEDDED_DB=true is enabled. Initializing Mongita file-based store...")
        try:
            from mongita import MongitaClientDisk
            import os
            data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "mongita_db")
            os.makedirs(data_dir, exist_ok=True)
            _client = MongitaClientDisk(host=data_dir)
            _db = _client[settings.MONGODB_DB_NAME]
            _db_status = "connected"
            logger.info(f"Mongita embedded DB connected at: {data_dir}")
            init_indexes(_db)
            return _db, _db_status
        except Exception as err:
            logger.error(f"Failed to initialize Mongita embedded database: {err}")
            _db_status = "disconnected"
            return None, _db_status

    raw_uri = settings.MONGODB_URI
    if not raw_uri:
        logger.error("MONGODB_URI is not configured in environment variables.")
        _db_status = "disconnected"
        return None, _db_status

    final_uri = encode_mongo_uri(raw_uri)
    logger.info(f"Attempting MongoDB Atlas connection to: {mask_uri(final_uri)}")

    try:
        _client = MongoClient(
            final_uri,
            serverSelectionTimeoutMS=8000,
            retryWrites=True,
            tlsCAFile=certifi.where()
        )
        _client.admin.command('ping')
        _db = _client[settings.MONGODB_DB_NAME]
        _db_status = "connected"
        logger.info(f"Successfully connected to MongoDB Atlas database: '{settings.MONGODB_DB_NAME}'")
        init_indexes(_db)
        return _db, _db_status
    except (ConnectionFailure, ServerSelectionTimeoutError) as err:
        _db_status = "disconnected"
        logger.error("==========================================================================")
        logger.error("MONGODB ATLAS CONNECTION FAILED!")
        logger.error(f"Error details: {err}")
        logger.error("==========================================================================")
        return None, _db_status
    except Exception as err:
        _db_status = "disconnected"
        logger.error(f"Unexpected MongoDB connection error: {err}")
        return None, _db_status

def get_db():
    global _db, _db_status
    if _db is None or _db_status != "connected":
        _db, _db_status = init_db()
    return _db

def get_db_status() -> str:
    global _db_status
    return _db_status

def fetch_records(collection, query: Optional[dict] = None, sort_key: str = "timestamp", reverse: bool = True, limit: Optional[int] = None) -> List[dict]:
    """Universal helper to query, sanitize ObjectId, sort and slice collection records for PyMongo and Mongita."""
    if query is None:
        query = {}
    docs = list(collection.find(query))
    for d in docs:
        d.pop("_id", None)
    if sort_key:
        docs.sort(key=lambda x: str(x.get(sort_key, "")), reverse=reverse)
    if limit:
        docs = docs[:limit]
    return docs

def init_indexes(db_instance):
    if db_instance is None:
        return
    try:
        is_mongita = settings.USE_EMBEDDED_DB
        if is_mongita:
            db_instance.users.create_index("email")
            db_instance.buildings.create_index("building_id")
            db_instance.facilities.create_index("facility_id")
            db_instance.energy_data.create_index("building_id")
            db_instance.water_data.create_index("building_id")
            db_instance.traffic_data.create_index("building_id")
            db_instance.occupancy_data.create_index("building_id")
            db_instance.parking_data.create_index("timestamp")
            db_instance.facility_utilization.create_index("facility_id")
            db_instance.predictions.create_index("prediction_type")
            db_instance.alerts.create_index("status")
            db_instance.anomalies.create_index("building_id")
            db_instance.recommendations.create_index("status")
            db_instance.datasets.create_index("created_at")
            db_instance.settings.create_index("key")
        else:
            db_instance.users.create_index("email", unique=True)
            db_instance.buildings.create_index("building_id", unique=True)
            db_instance.facilities.create_index("facility_id", unique=True)

            db_instance.energy_data.create_index([("building_id", 1), ("timestamp", -1)])
            db_instance.energy_data.create_index("dataset_id")
            db_instance.energy_data.create_index("source")

            db_instance.water_data.create_index([("building_id", 1), ("timestamp", -1)])
            db_instance.water_data.create_index("dataset_id")
            db_instance.water_data.create_index("source")

            db_instance.traffic_data.create_index([("building_id", 1), ("timestamp", -1)])
            db_instance.traffic_data.create_index("dataset_id")
            db_instance.traffic_data.create_index("source")

            db_instance.occupancy_data.create_index([("building_id", 1), ("timestamp", -1)])
            db_instance.parking_data.create_index([("timestamp", -1)])
            db_instance.facility_utilization.create_index([("facility_id", 1), ("timestamp", -1)])

            db_instance.predictions.create_index([("prediction_type", 1), ("prediction_date", 1)])
            db_instance.alerts.create_index([("status", 1), ("created_at", -1)])
            db_instance.anomalies.create_index([("building_id", 1), ("timestamp", -1)])
            db_instance.recommendations.create_index([("status", 1), ("created_at", -1)])

            db_instance.datasets.create_index([("created_at", -1)])
            db_instance.settings.create_index("key", unique=True)

        logger.info("Database indexes successfully initialized.")
    except Exception as e:
        logger.warning(f"Index creation notice: {e}")
