import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from app.db import get_db, fetch_records

def main():
    db = get_db()
    if db is None:
        print("DB unavailable")
        return
    buildings = fetch_records(db.buildings, sort_key="building_id")
    for b in buildings:
        print(b)

if __name__ == "__main__":
    main()
