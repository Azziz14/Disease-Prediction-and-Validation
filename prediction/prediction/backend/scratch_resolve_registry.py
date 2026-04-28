from utils.db import db_client
import json

def resolve_registry():
    if db_client.db is None:
        print("No database connection.")
        return

    doctors_to_find = ['Rajiv Malhotra', 'Ananya Sharma', 'Vikram Sethi', 'Priya Kapoor']
    patients_to_find = ['Aarav Gupta', 'Ishaan Verma', 'Saanvi Reddy', 'Vivaan Khurana', 'Diya Iyer', 'Reyansh Das', 'Myra Singh', 'Arjun Roy', 'Advik Joshi', 'Anika Nair']

    # 1. Resolve Doctors from 'users' collection (role: doctor)
    doctor_map = {}
    print("--- Resolving Doctors ---")
    for name in doctors_to_find:
        # Search by name regex
        doc = db_client.db.users.find_one({"name": {"$regex": name, "$options": "i"}, "role": "doctor"})
        if doc:
            doctor_map[name] = str(doc['_id'])
            print(f"FOUND: {name} -> {str(doc['_id'])}")
        else:
            # Try partial search if full name fails
            first_name = name.split()[0]
            doc = db_client.db.users.find_one({"name": {"$regex": first_name, "$options": "i"}, "role": "doctor"})
            if doc:
                doctor_map[name] = str(doc['_id'])
                print(f"FOUND (Partial): {name} matches {doc.get('name')} -> {str(doc['_id'])}")
            else:
                print(f"NOT FOUND: {name}")

    # 2. Resolve Patients from 'patients' collection
    # Note: If 'patients' collection doesn't have names, we might need to check 'users' collection first
    patient_map = {}
    print("\n--- Resolving Patients ---")
    for name in patients_to_find:
        # First check patients collection directly
        pat = db_client.db.patients.find_one({"name": {"$regex": name, "$options": "i"}})
        if pat:
            patient_map[name] = str(pat['_id'])
            print(f"FOUND in patients: {name} -> {str(pat['_id'])}")
        else:
            # Check users collection for the name, then find patient record by user_id
            user = db_client.db.users.find_one({"name": {"$regex": name, "$options": "i"}, "role": "patient"})
            if user:
                # Find patient record linked to this user
                # Common field might be 'user_id' string matching user Object ID, or matching a custom ID
                pat = db_client.db.patients.find_one({"user_id": str(user['_id'])})
                if not pat:
                    # Some systems use 'pat_...' as user_id field in patients
                    # Need to check if there's a link
                    pass
                
                if pat:
                    patient_map[name] = str(pat['_id'])
                    print(f"FOUND via users->patients: {name} -> {str(pat['_id'])}")
                else:
                    # If user exists but no patient record, we might need to create it later
                    print(f"FOUND USER ONLY: {name} (User ID: {str(user['_id'])}). Missing patient record.")
            else:
                print(f"NOT FOUND ANYWHERE: {name}")

    # Output results for implementation planning
    print("\n--- Final Resolved Map ---")
    print(json.dumps({"doctors": doctor_map, "patients": patient_map}, indent=2))

if __name__ == "__main__":
    resolve_registry()
