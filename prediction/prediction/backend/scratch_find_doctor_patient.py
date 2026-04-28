from utils.db import db_client
from bson import ObjectId
import json

def find_entities():
    if db_client.db is None:
        print("No database connection")
        return

    # Find doctor named Vikram Sethi
    doctor = db_client.db.users.find_one({"name": {"$regex": "Vikram Sethi", "$options": "i"}})
    if not doctor:
        # Check all doctors
        print("Doctor 'Vikram Sethi' not found. Searching for all doctors...")
        doctors = list(db_client.db.users.find({"role": "doctor"}))
        for d in doctors:
            print(f"Doctor: {d.get('name')} (ID: {d.get('_id')})")
    else:
        print(f"Found Doctor: {doctor.get('name')} (ID: {str(doctor.get('_id'))})")

    # Find patients
    print("\nSearching for patients...")
    patients = list(db_client.db.patients.find().limit(5))
    for p in patients:
         print(f"Patient: {p.get('name')} (ID: {str(p.get('_id'))})")

if __name__ == "__main__":
    find_entities()
