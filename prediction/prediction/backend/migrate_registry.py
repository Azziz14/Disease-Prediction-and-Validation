from utils.db import db_client
from bson import ObjectId
from datetime import datetime

def sync_registry():
    if db_client.db is None:
        print("No database connection.")
        return

    # 1. Definitive ID Mapping from Research
    doctors = {
        "Rajiv Malhotra": "69e80f3b9d1175f220760881",
        "Ananya Sharma": "69e80f3b9d1175f220760883",
        "Vikram Sethi": "69e80f3b9d1175f220760885",
        "Priya Kapoor": "69e80f3b9d1175f220760887"
    }

    patients = {
        "Aarav Gupta": "69e80f3b9d1175f220760889",
        "Ishaan Verma": "69e80f3b9d1175f22076088b",
        "Saanvi Reddy": "69e80f3b9d1175f22076088d",
        "Vivaan Khurana": "69e80f3c9d1175f22076088f",
        "Diya Iyer": "69e80f3c9d1175f220760891",
        "Reyansh Das": "69e80f3c9d1175f220760893",
        "Myra Singh": "69e80f3c9d1175f220760895",
        "Arjun Roy": "69e80f3d9d1175f220760897",
        "Advik Joshi": "69e80f3d9d1175f220760899",
        "Anika Nair": "69e80f3d9d1175f22076089b"
    }

    assignments = [
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

    print("--- Clearing Existing Assignments ---")
    db_client.db.patient_assignments.delete_many({})
    print("Cleared patient_assignments collection.\n")

    print("--- Syncing Clinical Registry ---")
    count = 0
    for doc_name, pat_name in assignments:
        doc_id = doctors.get(doc_name)
        user_id = patients.get(pat_name)

        if not doc_id or not user_id:
            print(f"ERROR: Missing ID for {doc_name} or {pat_name}")
            continue

        # A. Ensure patient record exists in 'patients' collection
        pat_record = db_client.db.patients.find_one({"user_id": user_id})
        if not pat_record:
            pat_record = db_client.db.patients.find_one({"name": pat_name})

        if not pat_record:
            new_patient = {
                "user_id": user_id,
                "name": pat_name,
                "treating_doctor": doc_id,
                "created_at": datetime.utcnow()
            }
            inserted = db_client.db.patients.insert_one(new_patient)
            pat_obj_id = inserted.inserted_id
            print(f"[NEW PATIENT] Created record for {pat_name}")
        else:
            db_client.db.patients.update_one(
                {"_id": pat_record["_id"]},
                {"$set": {"treating_doctor": doc_id, "name": pat_name}}
            )
            pat_obj_id = pat_record["_id"]
            print(f"[UPDATED] {pat_name} treating doctor set to {doc_name}")

        new_assignment = {
            "doctor_id": doc_id,
            "patient_id": str(pat_obj_id),
            "patient_name": pat_name,
            "assigned_date": datetime.utcnow(),
            "status": "active"
        }
        db_client.db.patient_assignments.insert_one(new_assignment)
        print(f"[ASSIGNED] {pat_name} -> {doc_name}")
        count += 1

    print(f"\n--- SYNC COMPLETE: {count} Assignments Created ---")

if __name__ == "__main__":
    sync_registry()
