"""Fix: sync patient names from users collection to patients collection and retroactive predictions."""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from utils.db import db_client

db = db_client.db

# Sync names: for each patient in patients collection, find the matching user and copy the real name
print("=== Syncing patient names from users collection ===")
patients = list(db.patients.find({}))
for p in patients:
    uid = p.get("user_id")
    if not uid:
        continue
    user = db.users.find_one({"user_id": uid})
    if user and user.get("name") and user["name"] != p.get("name"):
        old_name = p.get("name")
        new_name = user["name"]
        db.patients.update_one({"_id": p["_id"]}, {"$set": {"name": new_name}})
        print(f"  Updated patient name: {old_name!r} -> {new_name!r} (user_id={uid})")
    else:
        print(f"  OK: {p.get('name')!r} (user_id={uid})")

# Also sync predictions: update patient_name in predictions where patient_id matches
print("\n=== Syncing names in predictions collection ===")
for p in db.patients.find({}):
    uid = p.get("user_id")
    name = p.get("name")
    if not uid or not name:
        continue
    result = db.predictions.update_many(
        {"patient_id": uid, "patient_name": {"$ne": name}},
        {"$set": {"patient_name": name}}
    )
    if result.modified_count:
        print(f"  Fixed {result.modified_count} predictions for {name!r} ({uid})")

print("\nDone!")
