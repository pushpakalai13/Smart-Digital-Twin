import sys
import os
import certifi

# Path configuration to backend
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, ".env"))

from app.core.config import settings
from app.db import mask_uri, encode_mongo_uri
from pymongo import MongoClient

def test_atlas_connection():
    print("==========================================================================")
    print("           MongoDB Atlas Connection Verification Script                  ")
    print("==========================================================================")

    if settings.USE_EMBEDDED_DB:
        print("Notice: USE_EMBEDDED_DB is set to 'true'. Embedded Mongita storage active.")
        print("Result: OK (Embedded Local DB)")
        return True

    uri = settings.MONGODB_URI
    db_name = settings.MONGODB_DB_NAME

    if not uri or "<username>" in uri:
        print("[ERROR] MONGODB_URI is empty or still contains placeholders in backend/.env!")
        print("Please edit backend/.env and replace <username> and <password> with your Atlas database credentials.")
        return False

    final_uri = encode_mongo_uri(uri)
    print(f"Connecting to MongoDB Atlas target: {mask_uri(final_uri)} ...")

    try:
        client = MongoClient(
            final_uri,
            serverSelectionTimeoutMS=8000,
            tlsCAFile=certifi.where()
        )
        # Ping
        ping_res = client.admin.command("ping")
        server_info = client.server_info()
        version = server_info.get("version", "unknown")

        db = client[db_name]
        collections = db.list_collection_names()

        print("\n[SUCCESS] Connected to MongoDB Atlas!")
        print(f" -> Server MongoDB Version : {version}")
        print(f" -> Database Name          : {db_name}")
        print(f" -> Collections Count      : {len(collections)}")
        print(f" -> Existing Collections   : {', '.join(collections) if collections else '(None - ready for seeding)'}")
        print("==========================================================================")
        return True

    except Exception as err:
        print("\n[FAILURE] Could not establish connection to MongoDB Atlas!")
        print(f"Detailed Error: {err}\n")
        print("---------------- Troubleshooting Recommendations ----------------")
        print("1. Check Password: If password contains special characters like @, #, $, %, ensure they are URL-encoded.")
        print("2. Check Network Access: Log in to Atlas -> Network Access -> Add IP Address -> 'Allow Access from Anywhere' (0.0.0.0/0) for dev.")
        print("3. Check Database User: Log in to Atlas -> Database Access -> Ensure user exists with ReadWrite permissions.")
        print("4. Check Cluster Status: Ensure cluster is not paused or updating.")
        print("5. Double check the URI format in backend/.env")
        print("==========================================================================")
        return False

if __name__ == "__main__":
    success = test_atlas_connection()
    sys.exit(0 if success else 1)
