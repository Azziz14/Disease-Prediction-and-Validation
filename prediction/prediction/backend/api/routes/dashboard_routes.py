from flask import Blueprint, request, jsonify
from utils.db import db_client
import traceback
from datetime import datetime, timedelta
import random

dashboard_bp = Blueprint('dashboard', __name__)

# ═══════════════════════════════════════════════════════
# DEMO DATA — used when MongoDB is unavailable
# Provides realistic patient records for dashboard demos
# ═══════════════════════════════════════════════════════

DEMO_PATIENTS = [
    {
        "id": "PT-001", "name": "Rajesh Kumar", "age": 58, "gender": "Male",
        "disease": "diabetes", "risk": "High",
        "glucose": 245, "bloodPressure": 142, "bmi": 34.2,
        "confidence": 0.91,
        "prescribed_medicines": ["Metformin 1000mg", "Glipizide 5mg", "Empagliflozin 10mg"],
        "symptoms": ["Frequent urination", "Blurred vision", "Fatigue"],
        "doctor": "Dr. Sharma", "last_visit": "2026-04-14",
        "notes": "HbA1c at 9.2%. Needs aggressive management. Follow-up in 2 weeks."
    },
    {
        "id": "PT-002", "name": "Priya Patel", "age": 45, "gender": "Female",
        "disease": "heart", "risk": "High",
        "glucose": 110, "bloodPressure": 165, "bmi": 29.8,
        "confidence": 0.87,
        "prescribed_medicines": ["Atorvastatin 40mg", "Aspirin 81mg", "Lisinopril 10mg", "Metoprolol 25mg"],
        "symptoms": ["Chest pain on exertion", "Shortness of breath", "Palpitations"],
        "doctor": "Dr. Mehta", "last_visit": "2026-04-13",
        "notes": "ECG shows ST depression. Scheduled for stress test. High cardiovascular risk."
    },
    {
        "id": "PT-003", "name": "Anita Desai", "age": 32, "gender": "Female",
        "disease": "mental", "risk": "High",
        "glucose": 95, "bloodPressure": 118, "bmi": 22.1,
        "confidence": 0.84,
        "prescribed_medicines": ["Sertraline 50mg", "Hydroxyzine 25mg", "Melatonin 3mg"],
        "symptoms": ["Severe anxiety", "Insomnia", "Panic attacks", "Loss of appetite"],
        "doctor": "Dr. Singh", "last_visit": "2026-04-12",
        "notes": "GAD-7 score 18 (severe). Started SSRI therapy. CBT referral made."
    },
    {
        "id": "PT-004", "name": "Amit Verma", "age": 52, "gender": "Male",
        "disease": "diabetes", "risk": "Moderate",
        "glucose": 155, "bloodPressure": 128, "bmi": 28.5,
        "confidence": 0.73,
        "prescribed_medicines": ["Metformin 500mg", "Sitagliptin 100mg"],
        "symptoms": ["Increased thirst", "Mild fatigue"],
        "doctor": "Dr. Sharma", "last_visit": "2026-04-11",
        "notes": "Pre-diabetic trending upward. Lifestyle modification advised. Recheck in 3 months."
    },
    {
        "id": "PT-005", "name": "Sneha Gupta", "age": 67, "gender": "Female",
        "disease": "heart", "risk": "Moderate",
        "glucose": 105, "bloodPressure": 138, "bmi": 26.7,
        "confidence": 0.69,
        "prescribed_medicines": ["Atorvastatin 20mg", "Amlodipine 5mg"],
        "symptoms": ["Occasional dizziness", "Mild edema in ankles"],
        "doctor": "Dr. Mehta", "last_visit": "2026-04-10",
        "notes": "Cholesterol borderline high at 235 mg/dL. Monitor BP weekly."
    },
    {
        "id": "PT-006", "name": "Vikram Joshi", "age": 28, "gender": "Male",
        "disease": "mental", "risk": "Moderate",
        "glucose": 88, "bloodPressure": 120, "bmi": 23.4,
        "confidence": 0.65,
        "prescribed_medicines": ["Escitalopram 10mg", "Vitamin D3 2000 IU"],
        "symptoms": ["Work-related stress", "Difficulty concentrating", "Irritability"],
        "doctor": "Dr. Singh", "last_visit": "2026-04-09",
        "notes": "PHQ-9 score 12 (moderate depression). Workplace accommodation recommended."
    },
    {
        "id": "PT-007", "name": "Meera Reddy", "age": 40, "gender": "Female",
        "disease": "diabetes", "risk": "Low",
        "glucose": 102, "bloodPressure": 118, "bmi": 24.1,
        "confidence": 0.82,
        "prescribed_medicines": ["No pharmacological intervention"],
        "symptoms": ["None reported"],
        "doctor": "Dr. Sharma", "last_visit": "2026-04-08",
        "notes": "All values within normal range. Routine check-up. Continue healthy lifestyle."
    },
    {
        "id": "PT-008", "name": "Suresh Nair", "age": 55, "gender": "Male",
        "disease": "heart", "risk": "Low",
        "glucose": 92, "bloodPressure": 122, "bmi": 25.0,
        "confidence": 0.78,
        "prescribed_medicines": ["No pharmacological intervention"],
        "symptoms": ["None"],
        "doctor": "Dr. Mehta", "last_visit": "2026-04-07",
        "notes": "Healthy cardiac profile. Continue annual lipid panel. Exercise regimen adequate."
    },
    {
        "id": "PT-009", "name": "Kavita Sharma", "age": 35, "gender": "Female",
        "disease": "diabetes", "risk": "High",
        "glucose": 220, "bloodPressure": 135, "bmi": 36.8,
        "confidence": 0.93,
        "prescribed_medicines": ["Metformin 1000mg", "Insulin Glargine 20U", "Empagliflozin 25mg"],
        "symptoms": ["Rapid weight gain", "Numbness in feet", "Frequent infections"],
        "doctor": "Dr. Sharma", "last_visit": "2026-04-14",
        "notes": "Type 2 diabetes with neuropathy onset. Urgent endocrinology referral."
    },
    {
        "id": "PT-010", "name": "Rohan Pillai", "age": 72, "gender": "Male",
        "disease": "heart", "risk": "High",
        "glucose": 115, "bloodPressure": 175, "bmi": 31.2,
        "confidence": 0.95,
        "prescribed_medicines": ["Atorvastatin 80mg", "Clopidogrel 75mg", "Ramipril 5mg", "Furosemide 40mg", "Bisoprolol 5mg"],
        "symptoms": ["Chest tightness", "Severe edema", "Dyspnea at rest"],
        "doctor": "Dr. Mehta", "last_visit": "2026-04-14",
        "notes": "NYHA Class III heart failure. Ejection fraction 35%. Cardiology consult STAT."
    },
    {
        "id": "PT-011", "name": "Deepa Iyer", "age": 22, "gender": "Female",
        "disease": "mental", "risk": "Low",
        "glucose": 90, "bloodPressure": 110, "bmi": 21.5,
        "confidence": 0.76,
        "prescribed_medicines": ["No pharmacological intervention"],
        "symptoms": ["Mild exam stress"],
        "doctor": "Dr. Singh", "last_visit": "2026-04-06",
        "notes": "GAD-7 score 4 (minimal). Recommended mindfulness and regular exercise."
    },
    {
        "id": "PT-012", "name": "Arjun Malhotra", "age": 48, "gender": "Male",
        "disease": "diabetes", "risk": "Moderate",
        "glucose": 148, "bloodPressure": 130, "bmi": 30.1,
        "confidence": 0.71,
        "prescribed_medicines": ["Metformin 500mg", "Glimepiride 2mg"],
        "symptoms": ["Increased hunger", "Slow wound healing"],
        "doctor": "Dr. Sharma", "last_visit": "2026-04-10",
        "notes": "Newly diagnosed T2DM. Started on oral hypoglycemics. Diet counseling done."
    },
]

DEMO_PREDICTIONS = [
    {"patient_id": "PT-001", "disease": "diabetes", "risk": "High", "confidence": 0.91, "timestamp": "2026-04-14T09:30:00", "input_method": "structured"},
    {"patient_id": "PT-002", "disease": "heart", "risk": "High", "confidence": 0.87, "timestamp": "2026-04-13T14:15:00", "input_method": "voice"},
    {"patient_id": "PT-010", "disease": "heart", "risk": "High", "confidence": 0.95, "timestamp": "2026-04-14T11:00:00", "input_method": "structured"},
    {"patient_id": "PT-009", "disease": "diabetes", "risk": "High", "confidence": 0.93, "timestamp": "2026-04-14T10:45:00", "input_method": "structured"},
    {"patient_id": "PT-003", "disease": "mental", "risk": "High", "confidence": 0.84, "timestamp": "2026-04-12T16:30:00", "input_method": "voice"},
    {"patient_id": "PT-004", "disease": "diabetes", "risk": "Moderate", "confidence": 0.73, "timestamp": "2026-04-11T08:20:00", "input_method": "structured"},
    {"patient_id": "PT-005", "disease": "heart", "risk": "Moderate", "confidence": 0.69, "timestamp": "2026-04-10T13:00:00", "input_method": "structured"},
    {"patient_id": "PT-006", "disease": "mental", "risk": "Moderate", "confidence": 0.65, "timestamp": "2026-04-09T10:30:00", "input_method": "voice"},
    {"patient_id": "PT-012", "disease": "diabetes", "risk": "Moderate", "confidence": 0.71, "timestamp": "2026-04-10T15:45:00", "input_method": "structured"},
    {"patient_id": "PT-007", "disease": "diabetes", "risk": "Low", "confidence": 0.82, "timestamp": "2026-04-08T09:00:00", "input_method": "structured"},
    {"patient_id": "PT-008", "disease": "heart", "risk": "Low", "confidence": 0.78, "timestamp": "2026-04-07T11:30:00", "input_method": "structured"},
    {"patient_id": "PT-011", "disease": "mental", "risk": "Low", "confidence": 0.76, "timestamp": "2026-04-06T14:00:00", "input_method": "structured"},
]


def _get_demo_data(role, user_id=None):
    """Return demo data when MongoDB is not available."""
    data = {}
    
    if role == 'admin':
        data['total_patients'] = len(DEMO_PATIENTS)
        data['total_doctors'] = 3
        data['total_predictions'] = len(DEMO_PREDICTIONS)
        data['recent_predictions'] = sorted(DEMO_PREDICTIONS, key=lambda x: x['timestamp'], reverse=True)[:10]
        data['patients'] = DEMO_PATIENTS
        
        # Risk distribution
        data['risk_distribution'] = {
            'High': len([p for p in DEMO_PATIENTS if p['risk'] == 'High']),
            'Moderate': len([p for p in DEMO_PATIENTS if p['risk'] == 'Moderate']),
            'Low': len([p for p in DEMO_PATIENTS if p['risk'] == 'Low']),
        }
        
        # Disease distribution
        data['disease_distribution'] = {
            'diabetes': len([p for p in DEMO_PATIENTS if p['disease'] == 'diabetes']),
            'heart': len([p for p in DEMO_PATIENTS if p['disease'] == 'heart']),
            'mental': len([p for p in DEMO_PATIENTS if p['disease'] == 'mental']),
        }

    elif role == 'doctor':
        data['patients_count'] = len(DEMO_PATIENTS)
        data['patients'] = DEMO_PATIENTS
        data['recent_records'] = sorted(DEMO_PATIENTS, key=lambda x: x['last_visit'], reverse=True)[:10]

    else:  # patient
        patient = next((p for p in DEMO_PATIENTS if p['id'] == user_id), DEMO_PATIENTS[0])
        data['medical_records'] = [patient]
        data['predictions'] = [p for p in DEMO_PREDICTIONS if p['patient_id'] == (user_id or 'PT-001')]
        data['prescriptions'] = [{"medicines": patient['prescribed_medicines'], "date": patient['last_visit']}]

    return data


@dashboard_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    role = request.args.get('role', 'patient')
    user_id = request.args.get('user_id')
    
    try:
        # Try MongoDB first
        if db_client.db is not None:
            data = {}
            
            if role == 'admin':
                data['total_patients'] = db_client.db.patients.count_documents({})
                data['total_doctors'] = db_client.db.doctors.count_documents({})
                data['total_predictions'] = db_client.db.predictions.count_documents({})
                recent_preds = list(db_client.db.predictions.find().sort("timestamp", -1).limit(5))
                for p in recent_preds: p['_id'] = str(p['_id'])
                data['recent_predictions'] = recent_preds
                
            elif role == 'doctor':
                data['patients_count'] = db_client.db.patients.count_documents({})
                recent_records = list(db_client.db.medical_records.find().sort("date", -1).limit(10))
                for r in recent_records: r['_id'] = str(r['_id'])
                data['recent_records'] = recent_records
                
            else:
                if not user_id:
                    return jsonify({"error": "user_id required for patient dashboard"}), 400
                patient_records = list(db_client.db.medical_records.find({"patient_id": user_id}).sort("date", -1))
                for pr in patient_records: pr['_id'] = str(pr['_id'])
                data['medical_records'] = patient_records
                patient_preds = list(db_client.db.predictions.find({"patient_id": user_id}).sort("timestamp", -1))
                for p in patient_preds: p['_id'] = str(p['_id'])
                data['predictions'] = patient_preds
                patient_prescriptions = list(db_client.db.prescriptions.find({"patient_id": user_id}).sort("date_uploaded", -1))
                for p in patient_prescriptions: p['_id'] = str(p['_id'])
                data['prescriptions'] = patient_prescriptions

            # If DB returned empty data for admin, fall back to demo
            if role == 'admin' and data.get('total_patients', 0) == 0:
                data = _get_demo_data(role, user_id)

            return jsonify({"status": "success", "data": data})
        
        else:
            # MongoDB not available — use demo data
            data = _get_demo_data(role, user_id)
            return jsonify({"status": "success", "data": data})

    except Exception as e:
        traceback.print_exc()
        # Fallback to demo on any error
        data = _get_demo_data(role, user_id)
        return jsonify({"status": "success", "data": data})
