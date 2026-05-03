from flask import Blueprint, request, jsonify
from utils.db import db_client
import traceback
from datetime import datetime, timedelta
import random

dashboard_bp = Blueprint('dashboard', __name__)

# ═══════════════════════════════════════════════════════
# PERFORMANCE CACHE — 10-second lifetime
# ═══════════════════════════════════════════════════════
_DASHBOARD_CACHE = {}
_CACHE_TIMEOUT = 10 # seconds

def _get_cached_data(cache_key):
    if cache_key in _DASHBOARD_CACHE:
        data, ts = _DASHBOARD_CACHE[cache_key]
        if (datetime.now() - ts).total_seconds() < _CACHE_TIMEOUT:
            return data
    return None

def _set_cached_data(cache_key, data):
    _DASHBOARD_CACHE[cache_key] = (data, datetime.now())

def _get_fallback_data(role, user_id=None):
    """Return empty-state data when MongoDB is not available."""
    data = {}
    
    if role == 'admin':
        data['total_patients'] = 0
        data['total_doctors'] = 0
        data['total_predictions'] = 0
        data['recent_predictions'] = []
        data['patients'] = []
        data['risk_distribution'] = {'High': 0, 'Moderate': 0, 'Low': 0}
        data['disease_distribution'] = {'diabetes': 0, 'heart': 0, 'mental': 0}

    elif role == 'doctor':
        data['patients_count'] = 0
        data['patients'] = []
        data['recent_records'] = []

    else:  # patient
        data['medical_records'] = []
        data['predictions'] = []
        data['prescriptions'] = []

    return data


@dashboard_bp.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    role = request.args.get('role', 'patient')
    user_id = request.args.get('user_id')
    role_str = str(role or '').strip().lower()
    is_clinical = 'admin' in role_str or 'doctor' in role_str

    try:
        # Try MongoDB first
        if db_client.db is not None:
            data = {}
            
            if is_clinical:
                # 1. Fetch All Raw Data first
                all_patients = list(db_client.db.patients.find({}))
                patient_registry = {str(p.get('user_id')): p for p in all_patients if p.get('user_id')}
                
                pipeline = [{"$sort": {"timestamp": -1}}, {"$group": {"_id": "$patient_id", "latest": {"$first": "$$ROOT"}}}]
                latest_records_map = {str(res['_id']): res['latest'] for res in list(db_client.db.medical_records.aggregate(pipeline))}
                
                all_known_ids = set(patient_registry.keys()) | set(latest_records_map.keys())

                # 2. Compile Statistics
                total_doctors = db_client.db.users.count_documents({"role": "doctor"})
                pred_count = db_client.db.predictions.count_documents({})
                rec_count = db_client.db.medical_records.count_documents({})
                
                data['total_patients'] = len(all_known_ids)
                data['total_doctors'] = total_doctors
                data['total_predictions'] = max(pred_count, rec_count)
                
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
                for pred in recent_preds:
                    risk = pred.get('risk', 'Low')
                    if risk in risk_counts:
                        risk_counts[risk] += 1
                    disease = pred.get('disease', 'general')
                    disease_counts[disease] = disease_counts.get(disease, 0) + 1
                
                data['risk_distribution'] = risk_counts
                data['disease_distribution'] = disease_counts
                
            elif role == 'doctor':
                # Simplified Master Registry Access for Doctors
                # Since historical data may not have treating_doctor_id, we show all records
                dashboard_filter = {} # Show all clinical records to doctor
                
                data['patients_count'] = db_client.db.patients.count_documents({})
                
                # Fetch recent records (Admin-like visibility for clinical staff)
                recent_records = list(db_client.db.medical_records.find(dashboard_filter).sort("timestamp", -1).limit(40))
                for r in recent_records:
                    r['_id'] = str(r['_id'])
                    if 'timestamp' in r and r['timestamp']:
                        r['timestamp'] = r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp'])
                data['recent_records'] = recent_records
                
                # Fetch notifications/pings
                notifications = list(db_client.db.notifications.find({"to_user_id": user_id, "read": False}).sort("timestamp", -1))
                for n in notifications: n['_id'] = str(n['_id'])
                data['notifications'] = notifications

                # Fetch flagging status
                flags = list(db_client.db.doctor_flags.find({"doctor_id": user_id, "status": "active"}))
                data['is_flagged'] = len(flags) > 0
                data['active_flags'] = [{ "reason": f.get("reason"), "date": f.get("flagged_date").isoformat() if hasattr(f.get("flagged_date"), "isoformat") else str(f.get("flagged_date")) } for f in flags]

                # Fetch performance signal
                user_doc = db_client.db.users.find_one({"$or": [{"user_id": user_id}, {"email": user_id}]})
                data['performance_signal'] = user_doc.get('performance_signal', 'green') if user_doc else 'green'
                data['admin_signal_note'] = user_doc.get('admin_signal_note', '') if user_doc else ''
                
            else: # patient
                if not user_id:
                    return jsonify({"error": "user_id required"}), 400
                
                # Fetch user name for naming-based legacy fallback
                user_doc = db_client.db.users.find_one({"$or": [{"user_id": user_id}, {"_id": user_id}, {"email": user_id}]})
                user_name = user_doc.get("name") if user_doc else None
                
                # UINIFIED SEARCH: Search by ID, Email, or Name to bridge legacy session gaps
                id_search = {
                    "$or": [
                        {"patient_id": user_id}, 
                        {"user_id": user_id},
                        {"patient_id": user_doc['email']} if user_doc else None,
                        {"patient_name": {"$regex": user_name, "$options": "i"}} if user_name else None
                    ]
                }
                # Filter out None values
                id_search["$or"] = [x for x in id_search["$or"] if x]
                
                # OPTIMIZATION: Disable cache for patients to ensure real-time results
                cache_key = None 
                
                # Fetch records with resilient ID + Name search
                patient_records = list(db_client.db.medical_records.find(id_search).sort("timestamp", -1))
                for pr in patient_records:
                    pr['_id'] = str(pr['_id'])
                    if 'timestamp' in pr and pr['timestamp']:
                        pr['timestamp'] = pr['timestamp'].isoformat() if hasattr(pr['timestamp'], 'isoformat') else str(pr['timestamp'])
                data['medical_records'] = patient_records
                
                patient_preds = list(db_client.db.predictions.find(id_search).sort("timestamp", -1))
                for p in patient_preds:
                    p['_id'] = str(p['_id'])
                    if 'timestamp' in p and p['timestamp']:
                        p['timestamp'] = p['timestamp'].isoformat() if hasattr(p['timestamp'], 'isoformat') else str(p['timestamp'])
                data['predictions'] = patient_preds
                
                patient_prescriptions = list(db_client.db.prescriptions.find(id_search).sort("date_uploaded", -1))
                for p in patient_prescriptions:
                    p['_id'] = str(p['_id'])
                    if 'date_uploaded' in p and p['date_uploaded']:
                        p['date_uploaded'] = p['date_uploaded'].isoformat() if hasattr(p['date_uploaded'], 'isoformat') else str(p['date_uploaded'])
                data['prescriptions'] = patient_prescriptions

            # If DB returned empty data for admin, fall back to demo
            if role == 'admin' and data.get('total_patients', 0) == 0:
                data = _get_fallback_data(role, user_id)

            # Update cache before success
            _set_cached_data(cache_key, data)
            return jsonify({"status": "success", "data": data})
        
        else:
            # MongoDB not available — use demo data
            data = _get_fallback_data(role, user_id)
            return jsonify({"status": "success", "data": data})

    except Exception as e:
        traceback.print_exc()
        # Fallback to demo on any error
        data = _get_fallback_data(role, user_id)
        return jsonify({"status": "success", "data": data})


@dashboard_bp.route('/admin-patients', methods=['GET'])
def get_all_patients():
    """Get all patients with their associated doctors for admin dashboard."""
    try:
        if db_client.db is not None:
            # Get all patients
            patients = list(db_client.db.patients.find({}))
            for patient in patients:
                patient['_id'] = str(patient['_id'])
                
            # Get all predictions to extract patient information
            predictions = list(db_client.db.predictions.find({}))
            for pred in predictions:
                pred['_id'] = str(pred['_id'])
                
            # Get all users to map doctor information
            users = list(db_client.db.users.find({}))
            user_map = {str(user['_id']): user for user in users}
            
            # Combine patient data with predictions and doctor info
            patient_data = []
            patient_counter = 1001  # Start patient IDs from 1001
            
            for pred in predictions:
                # Generate or use existing patient ID
                existing_patient_id = pred.get('patient_id')
                if existing_patient_id and existing_patient_id.startswith('pat_'):
                    # Convert existing random ID to numeric
                    try:
                        patient_id = str(abs(hash(existing_patient_id)) % 100000 + 1000)
                    except:
                        patient_id = str(patient_counter)
                        patient_counter += 1
                else:
                    patient_id = str(patient_counter)
                    patient_counter += 1
                
                patient_info = {
                    'patient_id': patient_id,
                    'patient_name': pred.get('patient_name', f'Patient {patient_id}'),
                    'doctor_id': pred.get('doctor_id', ''),
                    'doctor_name': '',
                    'doctor_email': '',
                    'timestamp': pred.get('timestamp', ''),
                    'disease': pred.get('disease', 'diabetes'),
                    'risk': pred.get('risk', 'Low'),
                    'confidence': pred.get('confidence', 0),
                    'glucose': pred.get('glucose', 0),
                    'blood_pressure': pred.get('blood_pressure', 0),
                    'bmi': pred.get('bmi', 0),
                    'matched_drugs': pred.get('matched_drugs', []),
                    'recommendations': pred.get('recommendations', {}),
                    'auto_medications': pred.get('auto_medications', [])
                }
                
                # Add doctor information if available
                doctor_id = pred.get('doctor_id')
                if doctor_id and doctor_id in user_map:
                    doctor = user_map[doctor_id]
                    patient_info['doctor_name'] = doctor.get('name', 'Unknown Doctor')
                    patient_info['doctor_email'] = doctor.get('email', 'unknown@doctor.com')
                
                patient_data.append(patient_info)
            
            # Standardize timestamps for sort stability
            for x in patient_data:
                ts = x.get('timestamp', '')
                x['timestamp'] = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
            
            # Sort by timestamp (most recent first)
            patient_data.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            return jsonify({
                "status": "success", 
                "data": {
                    "patients": patient_data,
                    "total_count": len(patient_data)
                }
            })
        
        else:
            # MongoDB not available - return empty data
            return jsonify({
                "status": "success",
                "data": {
                    "patients": [],
                    "total_count": 0
                }
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "error": f"Failed to fetch patient data: {str(e)}"
        }), 500
