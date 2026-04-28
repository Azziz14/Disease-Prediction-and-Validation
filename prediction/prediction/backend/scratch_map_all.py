from utils.db import db_client
import json

def get_mapping():
    if db_client.db is None:
        print("No DB")
        return
    
    doctors = list(db_client.db.users.find({"role": "doctor"}))
    patients = list(db_client.db.patients.find())
    
    print("--- DOCTORS ---")
    for d in doctors:
        print(f"{d.get('name')} | {d.get('email')} | ID: {str(d.get('_id'))}")
    
    print("\n--- PATIENTS ---")
    for p in patients:
        print(f"{p.get('name')} | {p.get('user_id')} | ID: {str(p.get('_id'))}")

if __name__ == "__main__":
    get_mapping()
