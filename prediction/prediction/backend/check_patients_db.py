import pymongo
import certifi

client = pymongo.MongoClient("mongodb+srv://ashishking554_db_user:Azziizz%4014@diseasepredictionvalida.dlayq9m.mongodb.net/?appName=DiseasePredictionValidation", tlsCAFile=certifi.where())
db = client["DiseasePredictionValidation"]

patients = list(db.patients.find({}))
for p in patients:
    print(f"Patient {p.get('name')} (ID: {p.get('user_id', p.get('_id'))}): treating_doctor = {p.get('treating_doctor')}")
