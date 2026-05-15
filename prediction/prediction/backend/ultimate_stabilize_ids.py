import sys
sys.stdout.reconfigure(encoding='utf-8')

from utils.db import db_client
from bson import ObjectId

def stabilize_all_ids():
    if db_client.db is None:
        print("No DB Connection!")
        return

    print("==================================================")
    print("STABILIZATION: PURGING ANCHOR CONFLICTS & SYNCING")
    print("==================================================\n")

    # Clear out all messy duplicates in patients to allow fresh anchor points
    db_client.db.patients.delete_many({})
    print("Cleared old 'patients' registry to eliminate unique key constraint collisions.")

    db_client.db.patient_assignments.delete_many({})
    print("Cleared 'patient_assignments' registry.\n")

    users = list(db_client.db.users.find())
    
    doctor_map = {}
    patient_count = 0
    doctor_count = 0

    # Phase 1: Stabilize Doctors
    print("Phase 1: Anchoring Physicians...")
    for user in users:
        if user.get("role") == "doctor":
            u_id = user.get("user_id") or str(user["_id"])
            name = user.get("name")
            
            if not user.get("user_id"):
                db_client.db.users.update_one({"_id": user["_id"]}, {"$set": {"user_id": u_id}})
                
            doctor_map[name] = u_id
            
            # Sync in the 'doctors' collection (clear duplicates if exist)
            db_client.db.doctors.delete_many({"name": name})
            db_client.db.doctors.insert_one({"user_id": u_id, "name": name})
            print(f"Linked Doctor: {name} -> ID: {u_id}")
            doctor_count += 1

    print("\nPhase 2: Anchoring Patients...")
    for user in users:
        if user.get("role") == "patient":
            u_id = user.get("user_id") or str(user["_id"])
            name = user.get("name")

            if not user.get("user_id"):
                 db_client.db.users.update_one({"_id": user["_id"]}, {"$set": {"user_id": u_id}})
            
            # Create perfectly linked identity anchor in master patients registry
            db_client.db.patients.insert_one({
                "user_id": u_id,
                "name": name,
                "status": "active"
            })
            print(f"Anchored Patient: {name} -> ID: {u_id}")
            patient_count += 1

    print("\nPhase 3: Resolving Assignments and Treatment Anchors...")
    clinical_matrix = [
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
    
    assigned_count = 0
    for doc_name, pat_name in clinical_matrix:
        d_id = doctor_map.get(doc_name)
        pat_user = db_client.db.users.find_one({"name": pat_name, "role": "patient"})
        
        if d_id and pat_user:
            p_id = pat_user.get("user_id") or str(pat_user["_id"])
            
            db_client.db.patients.update_one(
                {"user_id": p_id},
                {"$set": {"treating_doctor": d_id}}
            )
            
            db_client.db.patient_assignments.insert_one({
                "doctor_id": d_id,
                "patient_id": p_id,
                "patient_name": pat_name,
                "status": "active"
            })
            assigned_count += 1
            print(f"Matrix Bound: Patient '{pat_name}' <-> Doctor '{doc_name}'")

    print(f"\n==================================================")
    print(f"SUCCESS: Synchronized {doctor_count} Doctors, {patient_count} Patients, Rebuilt {assigned_count} Assignments.")
    print("==================================================")

if __name__ == "__main__":
    stabilize_all_ids()
