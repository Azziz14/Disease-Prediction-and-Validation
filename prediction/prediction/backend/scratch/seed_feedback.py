import sys
import os
from datetime import datetime

# Adjust Python path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import db_client

def seed_samples():
    if db_client.db is None:
        print("Database connection failed.")
        return

    print("Checking existing doctor feedback in MongoDB...")
    count = db_client.db.doctor_feedback.count_documents({})
    print(f"Found {count} existing feedback records.")

    # Retrieve actual doctor IDs to reference
    doctors = list(db_client.db.users.find({"role": "doctor"}))
    if not doctors:
        print("No doctors registered. Please register at least one doctor account.")
        return

    doc = doctors[0]
    doc_id = str(doc["_id"])
    doc_name = doc.get("name", "Unknown Physician")
    
    samples = [
        {
            "patient_id": "pat_sample1",
            "patient_name": "Amit Kumar",
            "doctor_id": doc_id,
            "doctor_name": doc_name,
            "message": "Extremely detailed explanations during the neural predictive scan. Very professional clinical oversight.",
            "rating": 5,
            "timestamp": datetime.utcnow(),
            "status": "pending"
        },
        {
            "patient_id": "pat_sample2",
            "patient_name": "Neha Sharma",
            "doctor_id": doc_id,
            "doctor_name": doc_name,
            "message": "The automated medication prescription aligned perfectly with our discussions. Reassuring and accurate care.",
            "rating": 4,
            "timestamp": datetime.utcnow(),
            "status": "pending"
        }
    ]

    if count == 0:
        print(f"Seeding {len(samples)} sample clinical reviews targeting Dr. {doc_name} ({doc_id})...")
        db_client.db.doctor_feedback.insert_many(samples)
        print("Seed complete!")
    else:
        print("Feedback collection already populated. Skipping seed.")

if __name__ == "__main__":
    seed_samples()
