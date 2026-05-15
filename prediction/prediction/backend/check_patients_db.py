import os
import pymongo
import certifi

client = pymongo.MongoClient(os.environ.get("MONGO_URI", ""), tlsCAFile=certifi.where())
db = client["DiseasePredictionValidation"]

patients = list(db.patients.find({}))
for p in patients:
    print(f"Patient {p.get('name')} (ID: {p.get('user_id', p.get('_id'))}): treating_doctor = {p.get('treating_doctor')}")
