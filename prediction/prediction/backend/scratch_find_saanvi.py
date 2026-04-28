from utils.db import db_client
from bson import ObjectId
import json

def find_details():
    if db_client.db is None:
        print("No database connection")
        return

    # Find patient Saanvi Reddy
    patient = db_client.db.patients.find_one({"name": {"$regex": "Saanvi", "$options": "i"}})
    if patient:
        print(f"Found Patient: {patient.get('name')} (ID: {str(patient.get('_id'))})")
    else:
        print("Patient 'Saanvi' not found.")
        # Print first 5 patients with any data
        pats = list(db_client.db.patients.find().limit(5))
        for p in pats:
            print(f"ID: {p.get('_id')}, Data: {p}")

    # Check current assignments
    print("\nExisting Assignments:")
    assigns = list(db_client.db.patient_assignments.find())
    for a in assigns:
        print(f"Doctor: {a.get('doctor_id')}, Patient: {a.get('patient_id')}, Name: {a.get('patient_name')}")

if __name__ == "__main__":
    find_details()
