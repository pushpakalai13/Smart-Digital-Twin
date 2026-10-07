import sys
import os

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(backend_dir)

from app.db import get_db

db = get_db()
print("Connected to DB:", type(db))

docs = list(db.energy_data.find({"building_id": "B001"}))
print(f"Fetched {len(docs)} documents for B001")
for d in docs:
    d.pop("_id", None)

docs.sort(key=lambda x: str(x.get("timestamp", "")), reverse=True)
print("Top 2 sorted timestamps:", [d["timestamp"] for d in docs[:2]])
print("Sample record:", docs[0])
