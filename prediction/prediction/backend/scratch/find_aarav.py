import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

print("--- SEARCHING FOR AARAV GUPTA ---")
patient = db.patients.find_one({"name": {"$regex": "aarav", "$options": "i"}})
if patient:
    print(f"FOUND IN patients: {patient}")
else:
    print("NOT FOUND IN patients")

med_record = db.medical_records.find_one({"patient_name": {"$regex": "aarav", "$options": "i"}})
if med_record:
    print(f"FOUND IN medical_records: {med_record}")
else:
    print("NOT FOUND IN medical_records")

print("\n--- SEARCHING FOR DOCTORS ---")
doctors = list(db.users.find({"role": "doctor"}))
for d in doctors:
    print(f"DOCTOR: {d.get('name')} ({d.get('email')})")

print("\n--- SEARCHING FOR ASSIGNMENTS ---")
assignments = list(db.patient_assignments.find().limit(5))
for a in assignments:
    print(f"ASSIGNMENT: {a}")
