import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client[os.getenv('MONGODB_DB_NAME')]

print("--- SEARCHING FOR MISATTRIBUTED RECORDS (Patient=Doctor) ---")
# Find records where patient_id is Rajiv's email
rajiv_email = "rajiv@carepredict.ai"
mis_recs = list(db.medical_records.find({"patient_id": rajiv_email, "treating_doctor_id": rajiv_email}))

for r in mis_recs:
    print(f"ID: {r['_id']} | Name: {r.get('patient_name')} | Disease: {r.get('disease')}")

print(f"\nFound {len(mis_recs)} misattributed records.")
