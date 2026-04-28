from utils.db import db_client

def optimize_db():
    print("Initializing Database Indexing...")
    if db_client.db is None:
        print("Error: Database connection unavailable.")
        return

    # 1. Medical Records
    print("Indexing medical_records...")
    db_client.db.medical_records.create_index([("patient_id", 1), ("timestamp", -1)])
    db_client.db.medical_records.create_index([("treating_doctor_id", 1)])
    db_client.db.medical_records.create_index([("patient_name", 1)])

    # 2. Predictions
    print("Indexing predictions...")
    db_client.db.predictions.create_index([("user_id", 1), ("timestamp", -1)])
    db_client.db.predictions.create_index([("patient_id", 1)])

    # 3. Users
    print("Indexing users...")
    db_client.db.users.create_index([("user_id", 1)], unique=True)
    db_client.db.users.create_index([("role", 1)])
    db_client.db.users.create_index([("name", 1)])

    print("DB Optimization Complete. Clinical repository is now fully indexed.")

if __name__ == "__main__":
    optimize_db()
