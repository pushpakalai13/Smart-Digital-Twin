import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
backend_dir = os.path.join(root_dir, "backend")
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db import get_db, fetch_records

db = get_db()
if db is not None:
    b_docs = fetch_records(db.buildings)
    print(f"Total building documents in DB: {len(b_docs)}")
    
    seen_bids = {}
    duplicates_to_delete = []
    
    for doc in b_docs:
        bid = doc.get("building_id")
        name = doc.get("name")
        source = doc.get("source", "simulated")
        print(f"Doc ID: {doc.get('_id', 'N/A')} | building_id: {bid} | name: {name} | sqft: {doc.get('area_sqft')} | source: {source}")
        
        # Check if bid or normalized name already seen
        norm_key = (bid or "").strip().upper()
        if norm_key in seen_bids:
            # Duplicate found! Keep the one with source='uploaded' or most detailed area_sqft, mark other as duplicate
            prev_doc = seen_bids[norm_key]
            print(f"  --> DUPLICATE DETECTED for key '{norm_key}'!")
            if source == "uploaded":
                # Mark previous as duplicate to delete, update seen_bids to current
                duplicates_to_delete.append(prev_doc)
                seen_bids[norm_key] = doc
            else:
                duplicates_to_delete.append(doc)
        else:
            seen_bids[norm_key] = doc

    print(f"\nFound {len(duplicates_to_delete)} duplicate building document(s) to remove.")
    
    for d in duplicates_to_delete:
        bid = d.get("building_id")
        area = d.get("area_sqft")
        # Delete duplicate by bid and area_sqft or dataset_id
        if "dataset_id" in d:
            res = db.buildings.delete_many({"building_id": bid, "dataset_id": d["dataset_id"]})
        else:
            res = db.buildings.delete_many({"building_id": bid, "area_sqft": area})
        print(f"Deleted duplicate building doc: building_id={bid}, area={area}, deleted_count={res.deleted_count}")

    final_docs = fetch_records(db.buildings)
    print(f"\nFinal unique building count in DB: {len(final_docs)}")
    for b in final_docs:
        print(f" - [{b.get('building_id')}] {b.get('name')} | Area: {b.get('area_sqft')} sqft | Category: {b.get('category')}")
