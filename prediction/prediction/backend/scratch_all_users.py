from utils.db import db_client

def check_users():
    if db_client.db is None:
        print("No connection")
        return
        
    print("Listing all user accounts:")
    users = list(db_client.db.users.find())
    for u in users:
        print(f"Name: {u.get('name')}, Email: {u.get('email')}, Role: {u.get('role')}, ID: {u.get('id') or u.get('_id')}")

if __name__ == "__main__":
    check_users()
