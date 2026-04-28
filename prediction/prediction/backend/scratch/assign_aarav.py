import os
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

patient_name = "Aarav Gupta"
patient_email = "pat_57584fb2" # From previous search
doctor_id = "dr_946ce432" # Rajiv Malhotra's ID
doctor_name = "Rajiv Malhotra"

print(f"Assigning {patient_name} ({patient_email}) to {doctor_name} ({doctor_id})")

# 1. Update/Insert into master 'patients' collection
res = db.patients.update_one(
    {"user_id": patient_email}, 
    {"$set": {
        "name": patient_name,
        "treating_doctor": doctor_id,
        "assigned_at": datetime.utcnow(),
        "status": "active"
    }}
)
print(f"Patients collection update: {res.modified_count} updated")

# 2. Update all medical records to match
res_med = db.medical_records.update_many(
    {"patient_name": patient_name},
    {"$set": {
        "treating_doctor": doctor_name,
        "treating_doctor_id": doctor_id
    }}
)
print(f"Medical Records updated: {res_med.modified_count}")

# 3. Update predictions
res_pred = db.predictions.update_many(
    {"patient_name": patient_name},
    {"$set": {
        "treating_doctor": doctor_name,
        "treating_doctor_id": doctor_id
    }}
)
print(f"Predictions updated: {res_pred.modified_count}")

print("Clinical Anchor Secured.")
