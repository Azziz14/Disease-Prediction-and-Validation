import certifi
import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient("mongodb+srv://ashishking554_db_user:Azziizz%4014@diseasepredictionvalida.dlayq9m.mongodb.net/?appName=DiseasePredictionValidation", tlsCAFile=certifi.where())
db = client["DiseasePredictionValidation"]

user_id = '69e80f3b9d1175f220760881'

user_query = {"$or": [{"user_id": user_id}, {"email": user_id}]}
try:
    user_query["$or"].append({"_id": ObjectId(user_id)})
except Exception as e:
    print(f"Error making objectid: {e}")

print(f"user_query: {user_query}")
user_doc = db.users.find_one(user_query)

if user_doc:
    print(f"Found user! Name: {user_doc.get('name')}")
else:
    print("User NOT found!")

possible_ids = [str(user_id)]
if user_doc:
    if user_doc.get("user_id"): possible_ids.append(str(user_doc.get("user_id")))
    if user_doc.get("_id"): possible_ids.append(str(user_doc.get("_id")))

print(f"possible_ids: {possible_ids}")

flags = list(db.doctor_flags.find({
    "doctor_id": {"$in": possible_ids}, 
    "status": "active"
}))

print(f"Flags found: {len(flags)}")
for f in flags:
    print(f" - {f.get('reason')} (status: {f.get('status')})")

