import sys
import os
from datetime import datetime, timedelta
import random
from werkzeug.security import generate_password_hash
from uuid import uuid4

# Add parent dir to path for imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from utils.db import db_client
from services.recommendation_service import RecommendationService

def seed_clinical_world():
    if db_client.db is None:
        print("MongoDB not available. Seeding failed.")
        return

    # 1. Clear existing data (optional, but good for clean demo)
    # db_client.db.users.delete_many({"email": {"$regex": "@carepredict.ai"}})
    # db_client.db.medical_records.delete_many({})
    # db_client.db.predictions.delete_many({})

    password_hash = generate_password_hash("Password@123")
    rec_service = RecommendationService()

    doctors = [
        {"name": "Rajiv Malhotra", "email": "rajiv@carepredict.ai", "specialty": "Cardiology", "rank": 98, "errors": 0},
        {"name": "Ananya Sharma", "email": "ananya@carepredict.ai", "specialty": "Diabetology", "rank": 94, "errors": 0},
        {"name": "Vikram Sethi", "email": "vikram@carepredict.ai", "specialty": "Psychiatry", "rank": 72, "errors": 3},
        {"name": "Priya Kapoor", "email": "priya@carepredict.ai", "specialty": "General Medicine", "rank": 91, "errors": 1},
    ]

    doc_ids = []
    for d in doctors:
        u_id = f"dr_{uuid4().hex[:8]}"
        db_client.db.users.update_one(
            {"email": d["email"]},
            {"$set": {
                "user_id": u_id,
                "email": d["email"],
                "name": d["name"],
                "role": "doctor",
                "password_hash": password_hash,
                "clinical_rank": d["rank"],
                "wrong_prescription_count": d["errors"],
                "specialty": d["specialty"],
                "created_at": datetime.utcnow().isoformat()
            }},
            upsert=True
        )
        db_client.db.doctors.update_one({"user_id": u_id}, {"$set": {"user_id": u_id}}, upsert=True)
        doc_ids.append((u_id, d["name"]))

    patients = [
        ("Aarav Gupta", "aarav@carepredict.ai", 0),  # Dr Rajiv
        ("Ishaan Verma", "ishaan@carepredict.ai", 0), # Dr Rajiv
        ("Saanvi Reddy", "saanvi@carepredict.ai", 1), # Dr Ananya
        ("Vivaan Khurana", "vivaan@carepredict.ai", 1), # Dr Ananya
        ("Diya Iyer", "diya@carepredict.ai", 1),       # Dr Ananya
        ("Reyansh Das", "reyansh@carepredict.ai", 2),  # Dr Vikram (Risk!)
        ("Myra Singh", "myra@carepredict.ai", 2),      # Dr Vikram
        ("Arjun Roy", "arjun@carepredict.ai", 3),      # Dr Priya
        ("Advik Joshi", "advik@carepredict.ai", 3),    # Dr Priya
        ("Anika Nair", "anika@carepredict.ai", 3),     # Dr Priya
    ]

    for name, email, d_idx in patients:
        u_id = f"pat_{uuid4().hex[:8]}"
        doc_id, doc_name = doc_ids[d_idx]
        
        db_client.db.users.update_one(
            {"email": email},
            {"$set": {
                "user_id": u_id,
                "email": email,
                "name": name,
                "role": "patient",
                "password_hash": password_hash,
                "created_at": datetime.utcnow().isoformat()
            }},
            upsert=True
        )
        db_client.db.patients.update_one({"user_id": u_id}, {"$set": {"user_id": u_id, "treating_doctor": doc_id}}, upsert=True)

        # Generate History Trends
        diseases = ["heart", "diabetes", "mental", "heart", "diabetes", "mental", "mental", "diabetes", "heart", "diabetes"]
        disease = diseases[patients.index((name, email, d_idx))]
        
        for i in range(5):
            days_ago = (4-i) * 5
            timestamp = datetime.utcnow() - timedelta(days=days_ago)
            
            # Fetch professional protocols
            recs = rec_service.get_recommendations(disease)
            
            # Simulated "Wrong Medication" for Dr. Vikram
            is_faulty = (doc_name == "Vikram Sethi" and i == 2)
            
            record = {
                "patient_id": u_id,
                "patient_name": name,
                "timestamp": timestamp.isoformat(),
                "date": timestamp.isoformat(),
                "disease": disease,
                "risk": random.choice(["Low", "Moderate", "High"]),
                "confidence": 0.75 + (random.random() * 0.2),
                "treating_doctor": doc_name,
                "treating_doctor_id": doc_id,
                "flagged": is_faulty,
                "recommendations": recs,
                "auto_medications": recs.get("medical", [])
            }
            if is_faulty:
                record["issue"] = "AI Consensus Mismatch: Doctor prescribed contraindicated vasodilator for patient with acute hypotension risk."
                record["risk"] = "High"

            db_client.db.predictions.insert_one(record)
            db_client.db.medical_records.insert_one(record)

    print("Clinical Simulation Seeding Complete.")

if __name__ == "__main__":
    seed_clinical_world()
