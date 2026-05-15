import pymongo
import certifi

client = pymongo.MongoClient("mongodb+srv://ashishking554_db_user:Azziizz%4014@diseasepredictionvalida.dlayq9m.mongodb.net/?appName=DiseasePredictionValidation", tlsCAFile=certifi.where())
db = client["DiseasePredictionValidation"]

patient_id = "usr_d9afbd184471"
doctor_id = "dr_10534145"

# Update treating_doctor in patients collection
result = db.patients.update_one(
    {"$or": [{"user_id": patient_id}, {"_id": patient_id}, {"name": "Ashish"}]},
    {"$set": {"treating_doctor": doctor_id}}
)

print(f"Matched {result.matched_count} patients, modified {result.modified_count} patients.")

# Insert into patient_assignments if not exists
assignment_exists = db.patient_assignments.find_one({"patient_id": patient_id, "doctor_id": doctor_id})
if not assignment_exists:
    from datetime import datetime
    db.patient_assignments.insert_one({
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "assigned_at": datetime.utcnow()
    })
    print("Created assignment record.")
else:
    print("Assignment already exists.")
