import sys, os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
from utils.db import db_client

db = db_client.db

users = ["Rajiv Malhotra", "Aarav Gupta", "Ishaan Verma"]
for name in users:
    print(f"\n--- {name} ---")
    u = db.users.find_one({"name": name})
    if u:
        print(f"  _id: {str(u['_id'])}")
        print(f"  user_id: {u.get('user_id')}")
        print(f"  email: {u.get('email')}")
        print(f"  role: {u.get('role')}")
    else:
        print("  Not found")
