"""Debug: Find missing patient and all messages for Rajiv Malhotra."""
import sys, os, re
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from utils.db import db_client

db = db_client.db
if db is None:
    print("DB OFFLINE"); sys.exit(1)

# All patients in DB
print("ALL PATIENTS + treating_doctor values:")
all_patients = list(db.patients.find({}))
for p in all_patients:
    p['_id'] = str(p['_id'])
    print(f"  name={p.get('name','?')!r:25s}  user_id={p.get('user_id','?')!r:20s}  treating_doctor={p.get('treating_doctor','<unset>')!r}")

# All users with role doctor
print("\nALL DOCTORS:")
doctors = list(db.users.find({"role": "doctor"}))
for d in doctors:
    d['_id'] = str(d['_id'])
    print(f"  name={d.get('name','?')!r:25s}  user_id={d.get('user_id','?')!r:20s}  id={d.get('id','?')!r}")

# All messages (trimmed)
print("\nALL UNIVERSAL MESSAGES (last 20):")
msgs = list(db.universal_messages.find({}).sort("timestamp", -1).limit(20))
for m in msgs:
    msg_preview = repr(m.get('message',''))[:50]
    print(f"  sender={m.get('sender_id','?')!r:20s}  recip={m.get('recipient_id','?')!r:20s}  role={m.get('sender_role','?')!r}  msg={msg_preview}")
print(f"Total messages in DB: {db.universal_messages.count_documents({})}")
