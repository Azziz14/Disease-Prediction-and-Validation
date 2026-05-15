import sys
import os

# Add backend to path so we can import db config
sys.path.append(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\backend")

from api.config import db_client

def inspect_db():
    print("--- DOCTOR FLAGS ---")
    flags = list(db_client.db.doctor_flags.find())
    for f in flags:
        print(f"Flag ID: {f.get('_id')}")
        print(f"  doctor_id: {f.get('doctor_id')} (type: {type(f.get('doctor_id')).__name__})")
        print(f"  status: {f.get('status')}")
        print(f"  reason: {f.get('reason')}")
        
    print("\n--- DOCTORS IN USERS DB ---")
    doctors = list(db_client.db.users.find({"role": "doctor"}))
    for d in doctors:
        print(f"Doc: {d.get('name')}")
        print(f"  _id: {d.get('_id')} (type: {type(d.get('_id')).__name__})")
        print(f"  user_id: {d.get('user_id')} (type: {type(d.get('user_id')).__name__})")
        print(f"  email: {d.get('email')}")

if __name__ == '__main__':
    inspect_db()
