"""
Fix:
1. Reassign 'Unknown Patient' (pat_45141b5a) treating_doctor -> dr_10534145 (Rajiv Malhotra)
2. Fix the broken message that has recipient_id='👤' -> pat_45141b5a
3. Fix 'Ashish' and 'anupam' (real user accounts) if they have a treating_doctor in messages
"""
import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from utils.db import db_client

db = db_client.db
if db is None:
    print("DB OFFLINE"); sys.exit(1)

# ── FIX 1: Correct treating_doctor for pat_45141b5a ────────────────────────
result = db.patients.update_one(
    {"user_id": "pat_45141b5a"},
    {"$set": {"treating_doctor": "dr_10534145", "name": "Unknown Patient"}}
)
print(f"[FIX 1] Updated pat_45141b5a treating_doctor -> dr_10534145: matched={result.matched_count}")

# ── FIX 2: Fix the broken message with recipient_id = emoji '👤' ─────────────
result2 = db.universal_messages.update_many(
    {"recipient_id": "\U0001f464"},   # the 👤 emoji
    {"$set": {"recipient_id": "pat_45141b5a"}}
)
print(f"[FIX 2] Fixed emoji recipient messages: modified={result2.modified_count}")

# ── FIX 3: Update pat_45141b5a's messages that went to 'Unspecified Physician' ─
result3 = db.universal_messages.update_many(
    {"recipient_id": "Unspecified Physician"},
    {"$set": {"recipient_id": "dr_10534145"}}
)
print(f"[FIX 3] Fixed 'Unspecified Physician' recipient messages: modified={result3.modified_count}")

# ── VERIFY ─────────────────────────────────────────────────────────────────────
print("\n--- AFTER FIX: Patients for Rajiv Malhotra (dr_10534145) ---")
patients = list(db.patients.find({"treating_doctor": "dr_10534145"}))
for p in patients:
    print(f"  name={p.get('name')!r}  user_id={p.get('user_id')!r}")

print(f"\n--- AFTER FIX: Messages between Rajiv and his patients ---")
msgs = list(db.universal_messages.find({
    "$or": [
        {"sender_id": "dr_10534145"},
        {"recipient_id": "dr_10534145"},
        {"sender_id": "pat_45141b5a"},
        {"recipient_id": "pat_45141b5a"},
    ]
}).sort("timestamp", 1))
for m in msgs:
    print(f"  {m.get('sender_id')} -> {m.get('recipient_id')}: {repr(m.get('message',''))[:60]}")
print(f"Total: {len(msgs)} messages")
