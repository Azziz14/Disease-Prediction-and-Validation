import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from utils.db import db_client

db = db_client.db

print("=== ALL MESSAGES ===")
msgs = list(db.universal_messages.find({}).sort("timestamp", 1))
for m in msgs:
    print(f"  sender_id={m.get('sender_id')!r:25} recip={m.get('recipient_id')!r:25} role={m.get('sender_role')!r} msg={repr(m.get('message',''))[:40]}")

print("\n=== USER ACCOUNTS (role=patient) ===")
for u in db.users.find({"role": "patient"}):
    print(f"  name={u.get('name')!r:20} user_id={u.get('user_id')!r}")

print("\n=== PATIENTS COLLECTION ===")
for p in db.patients.find({}):
    print(f"  name={p.get('name')!r:20} user_id={p.get('user_id')!r}  treating_doctor={p.get('treating_doctor','<none>')!r}")
