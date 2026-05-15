import pymongo
import certifi

client = pymongo.MongoClient("mongodb+srv://ashishking554_db_user:Azziizz%4014@diseasepredictionvalida.dlayq9m.mongodb.net/?appName=DiseasePredictionValidation", tlsCAFile=certifi.where())
db = client["DiseasePredictionValidation"]

print("--- DOCTOR FLAGS ---")
flags = list(db.doctor_flags.find())
for f in flags:
    print(f"Flag ID: {f.get('_id')}")
    print(f"  doctor_id: {f.get('doctor_id')} (type: {type(f.get('doctor_id')).__name__})")
    print(f"  status: {f.get('status')}")
    print(f"  reason: {f.get('reason')}")
    
print("\n--- DOCTORS IN USERS DB ---")
doctors = list(db.users.find({"role": "doctor"}))
for d in doctors:
    print(f"Doc: {d.get('name')}")
    print(f"  _id: {d.get('_id')} (type: {type(d.get('_id')).__name__})")
    print(f"  user_id: {d.get('user_id')} (type: {type(d.get('user_id')).__name__})")
    print(f"  email: {d.get('email')}")
