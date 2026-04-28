import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import utils and services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import db_client
from bson import ObjectId

def realign():
    print("--- STARTING CLINICAL DATA RE-ALIGNMENT ---")
    
    if db_client.db is None:
        print("CRITICAL: MongoDB not connected.")
        return

    # 1. Map patients to their doctors
    # Format: {patient_id: doctor_id, patient_name: doctor_id}
    registry = {}
    doctors_by_name = {}
    
    # Pre-fetch all doctors for name-based matching
    doctors = list(db_client.db.users.find({"role": "doctor"}))
    for d in doctors:
        d_id = d.get("user_id") or str(d["_id"])
        if d.get("name"):
            doctors_by_name[d["name"]] = d_id
    
    patients = list(db_client.db.patients.find({}))
    for p in patients:
        p_id = p.get("user_id") or str(p["_id"])
        doc_id = p.get("treating_doctor")
        if doc_id:
            registry[p_id] = doc_id
            if p.get("name"):
                registry[p["name"]] = doc_id

    print(f"Registry loaded: {len(registry)} mappings found.")

    # 2. Audit Medical Records
    records = list(db_client.db.medical_records.find({}))
    print(f"Auditing {len(records)} medical records...")
    
    fixed_count = 0
    for r in records:
        update_fields = {}
        
        p_id = r.get("patient_id")
        p_name = r.get("patient_name")
        curr_doc_id = r.get("treating_doctor_id")
        curr_doc_name = r.get("treating_doctor")
        
        # Link orphan by ID
        if (not curr_doc_id or curr_doc_id == "Guest") and p_id in registry:
            update_fields["treating_doctor_id"] = registry[p_id]
        
        # Link orphan by Name
        if (not curr_doc_id or curr_doc_id == "Guest") and not update_fields.get("treating_doctor_id") and p_name in registry:
            update_fields["treating_doctor_id"] = registry[p_name]
            
        # Fix missing doctor name if ID exists
        if curr_doc_id and not curr_doc_name:
            doc = db_client.db.users.find_one({"$or": [{"user_id": curr_doc_id}, {"_id": curr_doc_id}]})
            if doc:
                update_fields["treating_doctor"] = doc.get("name")
        
        # Fix missing doctor ID if name is known
        if (not curr_doc_id or curr_doc_id == "Guest") and curr_doc_name in doctors_by_name:
            update_fields["treating_doctor_id"] = doctors_by_name[curr_doc_name]

        if update_fields:
            db_client.db.medical_records.update_one({"_id": r["_id"]}, {"$set": update_fields})
            # Also update predictions collection for total sync
            db_client.db.predictions.update_one(
                {"$or": [{"_id": r["_id"]}, {"timestamp": r.get("timestamp")}]}, 
                {"$set": update_fields}
            )
            fixed_count += 1

    print(f"Re-alignment complete. Fixed {fixed_count} records.")
    print("--- REALIGNMENT FINISHED ---")

if __name__ == "__main__":
    realign()
