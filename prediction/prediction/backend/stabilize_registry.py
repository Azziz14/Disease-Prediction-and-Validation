from utils.db import db_client
from datetime import datetime

def sync_registry_v3_internal_ids():
    if db_client.db is None:
        print("No database connection.")
        return

    # 1. Definitive Internal ID Mapping (The 'user_id' fields)
    doctors = {
        "Rajiv Malhotra": "dr_10534145",
        "Ananya Sharma": "dr_aaed605e",
        "Vikram Sethi": "dr_f5ba4b3d",
        "Priya Kapoor": "dr_8023d9d3"
    }

    patients = {
        "Aarav Gupta": "pat_a388885b",
        "Ishaan Verma": "pat_45141b5a",
        "Saanvi Reddy": "pat_b21e99e3",
        "Vivaan Khurana": "pat_c504bd53",
        "Diya Iyer": "pat_75c7530c",
        "Reyansh Das": "pat_8ccef2b8",
        "Myra Singh": "pat_a14029a6",
        "Arjun Roy": "pat_cade20a7",
        "Advik Joshi": "pat_99048628",
        "Anika Nair": "pat_0241e945"
    }

    registry_assignments = [
        ("Rajiv Malhotra", "Aarav Gupta"),
        ("Rajiv Malhotra", "Ishaan Verma"),
        ("Ananya Sharma", "Saanvi Reddy"),
        ("Ananya Sharma", "Vivaan Khurana"),
        ("Ananya Sharma", "Diya Iyer"),
        ("Vikram Sethi", "Reyansh Das"),
        ("Vikram Sethi", "Myra Singh"),
        ("Priya Kapoor", "Arjun Roy"),
        ("Priya Kapoor", "Advik Joshi"),
        ("Priya Kapoor", "Anika Nair")
    ]

    print("--- Clearing ALL Existing Assignments (Clinical Stabilization) ---")
    db_client.db.patient_assignments.delete_many({})
    
    print("--- Mapping Registry to Internal IDs ---")
    count = 0
    for doc_name, pat_name in registry_assignments:
        doc_internal_id = doctors.get(doc_name)
        pat_internal_id = patients.get(pat_name)

        if not doc_internal_id or not pat_internal_id:
            print(f"FAILED to map {doc_name} or {pat_name}")
            continue

        # A. Find or Create the linking 'patients' record
        # The system logic expects 'patient_id' in assignments to be the MongoDB _id of the record in 'patients' collection
        # But it also looks for that record by 'user_id' internally.
        
        pat_record = db_client.db.patients.find_one({"user_id": pat_internal_id})
        if not pat_record:
            # Create a shell record if missing
            new_patient = {
                "user_id": pat_internal_id,
                "name": pat_name,
                "treating_doctor": doc_internal_id,
                "created_at": datetime.utcnow()
            }
            inserted = db_client.db.patients.insert_one(new_patient)
            pat_obj_id = str(inserted.inserted_id)
            print(f"[NEW RECORD] Created clinical marker for {pat_name}")
        else:
            # Update treating doctor for consistency
            db_client.db.patients.update_one(
                {"_id": pat_record["_id"]},
                {"$set": {"treating_doctor": doc_internal_id, "name": pat_name}}
            )
            pat_obj_id = str(pat_record["_id"])
            print(f"[SYNCED] Updating {pat_name} treating doctor to {doc_name}")

        # B. Insert Assignment using the INTERNAL DOCTOR ID
        # Many parts of the frontend (DoctorDashboard.tsx) fetch via `user_id=${user?.id}`
        # Therefore, 'doctor_id' in assignments MUST be the internal 'dr_...' string.
        new_assignment = {
            "doctor_id": doc_internal_id,
            "patient_id": pat_obj_id,
            "patient_name": pat_name,
            "assigned_date": datetime.utcnow(),
            "status": "active"
        }
        db_client.db.patient_assignments.insert_one(new_assignment)
        print(f"[ASSIGNED] {pat_name} -> {doc_name} (ID: {doc_internal_id})")
        count += 1

    print(f"\n--- MISSION COMPLETE: {count} IDENTITIES STABILIZED ---")

if __name__ == "__main__":
    sync_registry_v3_internal_ids()
