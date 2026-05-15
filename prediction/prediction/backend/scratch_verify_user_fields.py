from utils.db import db_client

def verify():
    if db_client.db is None: return
    u = db_client.db.users.find_one({"email": "aarav@carepredict.ai"})
    print("Aarav User in DB:", {k: str(v) for k, v in u.items()})
    
    p = db_client.db.patients.find_one({"user_id": u.get("_id")}) or db_client.db.patients.find_one({"name": "Aarav Gupta"})
    print("Aarav Patient in DB:", {k: str(v) for k, v in p.items()} if p else "NOT FOUND")

if __name__ == "__main__":
    verify()
