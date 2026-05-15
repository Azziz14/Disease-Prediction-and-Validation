import sys
import os
import traceback

# Adjust Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.db import db_client

def debug_dashboard():
    if db_client.db is None:
        print("Database not connected.")
        return

    print("--- MongoDB Collection Counts ---")
    try:
        print(f"patients: {db_client.db.patients.count_documents({})}")
        print(f"predictions: {db_client.db.predictions.count_documents({})}")
        print(f"medical_records: {db_client.db.medical_records.count_documents({})}")
        print(f"users (doctors): {db_client.db.users.count_documents({'role': 'doctor'})}")
    except Exception as e:
        print(f"Error counting: {e}")

    print("\n--- Attempting to Execute Route Logic ---")
    try:
        data = {}
        # 1. Fetch All Raw Data first
        all_patients = list(db_client.db.patients.find({}))
        patient_registry = {}
        for p in all_patients:
            uid = p.get('user_id') or str(p.get('_id'))
            if uid:
                patient_registry[str(uid).strip().lower()] = p

        all_records = list(db_client.db.medical_records.find({}))
        all_preds = list(db_client.db.predictions.find({}))
        
        combined_records = all_records + [p for p in all_preds if str(p.get('_id')) not in {str(r.get('_id')) for r in all_records}]
        
        def sort_key(rec):
            val = rec.get('timestamp') or rec.get('date') or ''
            if hasattr(val, 'isoformat'):
                return val.isoformat()
            return str(val)
        
        combined_records.sort(key=sort_key, reverse=True)
        
        latest_records_map = {}
        for r in combined_records:
            pid = r.get('patient_id') or r.get('user_id')
            if pid:
                pid_str = str(pid).strip().lower()
                if pid_str not in latest_records_map:
                    latest_records_map[pid_str] = r

        all_known_ids = set(patient_registry.keys()) | set(latest_records_map.keys())

        # 2. Compile Statistics
        total_doctors = db_client.db.users.count_documents({"role": "doctor"})
        pred_count = db_client.db.predictions.count_documents({})
        rec_count = db_client.db.medical_records.count_documents({})
        
        data['total_patients'] = len(all_known_ids)
        data['total_doctors'] = total_doctors
        data['total_predictions'] = max(pred_count, rec_count)
        
        print(f"Data counts computed -> patients={len(all_known_ids)}, docs={total_doctors}, preds={data['total_predictions']}")

        # 3. Format Patient Table
        formatted_patients = []
        for p_id in all_known_ids:
            p_info = patient_registry.get(p_id, {})
            latest_r = latest_records_map.get(p_id, {})
            raw_ts = latest_r.get("timestamp") or latest_r.get("date") or "N/A"
            last_v = str(raw_ts).split('T')[0] if 'T' in str(raw_ts) else str(raw_ts)

            formatted_patients.append({
                "id": p_id,
                "name": p_info.get("name") or latest_r.get("patient_name") or "Unknown Patient",
                "age": p_info.get("age", 45),
                "gender": p_info.get("gender", "M"),
                "disease": latest_r.get("disease", "General"),
                "doctor": latest_r.get("treating_doctor", "System"),
                "risk": latest_r.get("risk", "Low"),
                "confidence": latest_r.get("confidence", 0.85),
                "glucose": latest_r.get("glucose", 100),
                "bloodPressure": latest_r.get("blood_pressure", 120),
                "bmi": latest_r.get("bmi", 22),
                "last_visit": last_v,
                "prescribed_medicines": latest_r.get("auto_medications") or latest_r.get("matched_drugs") or ["No prescription"],
                "symptoms": ["General inquiry"],
                "notes": "Electronic health record updated."
            })
        data['patients'] = formatted_patients
        
        # 4. Standardized Recent Predictions
        recent = list(db_client.db.predictions.find().sort("timestamp", -1).limit(30))
        if not recent: recent = list(db_client.db.medical_records.find().sort("timestamp", -1).limit(30))
        for r in recent: 
            r['_id'] = str(r['_id'])
            r['timestamp'] = str(r.get('timestamp') or r.get('date') or '')
        data['recent_predictions'] = recent
        
        # 5. Doctor Registry
        doctors = list(db_client.db.users.find({"role": "doctor"}))
        doctor_registry = []
        for d in doctors:
            d_id = d.get("user_id") or str(d.get("_id"))
            doctor_registry.append({
                "id": d_id,
                "name": d.get("name"),
                "email": d.get("email"),
                "rank": d.get("clinical_rank", 90),
                "errors": d.get("wrong_prescription_count", 0),
                "performance_signal": d.get("performance_signal", "green"),
                "admin_signal_note": d.get("admin_signal_note", ""),
                "patients": []
            })
        data['doctor_registry'] = doctor_registry
        
        # Calculate risk distribution from predictions
        risk_counts = {'High': 0, 'Moderate': 0, 'Low': 0}
        disease_counts = {}
        for pred in recent:
            risk = pred.get('risk', 'Low')
            if risk in risk_counts:
                risk_counts[risk] += 1
            disease = pred.get('disease', 'general')
            disease_counts[disease] = disease_counts.get(disease, 0) + 1
        
        data['risk_distribution'] = risk_counts
        data['disease_distribution'] = disease_counts
        
        print("SUCCESS! No exception thrown.")
        print("Final compiled keys:", list(data.keys()))
    except Exception:
        print("CRITICAL CRASH DETECTED!")
        traceback.print_exc()

if __name__ == "__main__":
    debug_dashboard()
