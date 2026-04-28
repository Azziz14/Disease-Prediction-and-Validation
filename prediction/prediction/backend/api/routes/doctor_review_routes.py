from flask import Blueprint, request, jsonify
from utils.db import db_client
from datetime import datetime, timedelta
import traceback

doctor_review_bp = Blueprint('doctor_review', __name__)

@doctor_review_bp.route('/doctor-performance', methods=['GET'])
def get_doctor_performance():
    """Get performance metrics for all doctors."""
    try:
        if db_client.db is not None:
            # Get all doctors
            doctors = list(db_client.db.users.find({"role": "doctor"}))
            
            performance_data = []
            
            for doctor in doctors:
                doctor_id = str(doctor["_id"])
                
                # Get patient assignments
                assignments = list(db_client.db.patient_assignments.find({"doctor_id": doctor_id}))
                
                # Get predictions for this doctor's patients
                patient_ids = [assign["patient_id"] for assign in assignments]
                predictions = list(db_client.db.predictions.find({"patient_id": {"$in": patient_ids}}))
                
                # Calculate performance metrics
                total_patients = len(assignments)
                total_assessments = len(predictions)
                
                # Risk distribution
                high_risk = len([p for p in predictions if p.get("risk") == "High"])
                moderate_risk = len([p for p in predictions if p.get("risk") == "Moderate"])
                low_risk = len([p for p in predictions if p.get("risk") == "Low"])
                
                # Average confidence
                avg_confidence = sum(p.get("confidence", 0) for p in predictions) / len(predictions) if predictions else 0
                
                # Calculate score based on multiple factors
                score = calculate_doctor_score(total_patients, total_assessments, avg_confidence, {
                    "high_risk": high_risk,
                    "moderate_risk": moderate_risk,
                    "low_risk": low_risk
                })
                
                # Get recent activity (last 30 days)
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                recent_predictions = [p for p in predictions if datetime.fromisoformat(p.get("timestamp", "").replace('Z', '+00:00')) > thirty_days_ago]
                
                performance_data.append({
                    "doctor_id": doctor_id,
                    "doctor_name": doctor.get("name", "Unknown Doctor"),
                    "doctor_email": doctor.get("email", ""),
                    "total_patients": total_patients,
                    "total_assessments": total_assessments,
                    "recent_assessments": len(recent_predictions),
                    "risk_distribution": {
                        "high": high_risk,
                        "moderate": moderate_risk,
                        "low": low_risk
                    },
                    "average_confidence": round(avg_confidence, 3),
                    "performance_score": round(score, 2),
                    "flagged": score < 60,  # Flag doctors with score below 60
                    "status": get_performance_status(score)
                })
            
            return jsonify({"status": "success", "data": performance_data})
        
        else:
            return jsonify({"status": "success", "data": []})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch doctor performance: {str(e)}"}), 500

@doctor_review_bp.route('/flag-doctor', methods=['POST'])
def flag_doctor():
    """Flag a doctor for review."""
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    reason = data.get('reason', '')
    flagged_by = data.get('flagged_by', 'admin')
    
    if not doctor_id:
        return jsonify({"error": "doctor_id is required"}), 400
    
    try:
        if db_client.db is not None:
            # Create flag record
            flag_record = {
                "doctor_id": doctor_id,
                "reason": reason,
                "flagged_by": flagged_by,
                "flagged_date": datetime.utcnow(),
                "status": "active",
                "review_notes": ""
            }
            
            db_client.db.doctor_flags.insert_one(flag_record)
            
            return jsonify({
                "status": "success",
                "message": "Doctor flagged for review successfully"
            })
        
        else:
            return jsonify({
                "status": "success",
                "message": "Doctor flagged successfully (fallback mode)"
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to flag doctor: {str(e)}"}), 500

@doctor_review_bp.route('/doctor-flags', methods=['GET'])
def get_doctor_flags():
    """Get all flagged doctors for admin review."""
    try:
        if db_client.db is not None:
            flags = list(db_client.db.doctor_flags.find({"status": "active"}))
            
            # Get doctor details
            doctor_ids = [flag["doctor_id"] for flag in flags]
            doctors = list(db_client.db.users.find({"_id": {"$in": doctor_ids}}))
            doctor_map = {str(doc["_id"]): doc for doc in doctors}
            
            result = []
            for flag in flags:
                doctor = doctor_map.get(flag["doctor_id"])
                result.append({
                    "flag_id": str(flag["_id"]),
                    "doctor_id": flag["doctor_id"],
                    "doctor_name": doctor.get("name", "Unknown Doctor") if doctor else "Unknown Doctor",
                    "doctor_email": doctor.get("email", "") if doctor else "",
                    "reason": flag.get("reason", ""),
                    "flagged_by": flag.get("flagged_by", ""),
                    "flagged_date": flag.get("flagged_date"),
                    "status": flag.get("status", "active"),
                    "review_notes": flag.get("review_notes", "")
                })
            
            return jsonify({"status": "success", "data": result})
        
        else:
            return jsonify({"status": "success", "data": []})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch doctor flags: {str(e)}"}), 500

@doctor_review_bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Submit feedback for a doctor from a patient."""
    data = request.get_json()
    patient_id = data.get('patient_id')
    patient_name = data.get('patient_name', 'Anonymous')
    doctor_id = data.get('doctor_id')
    message = data.get('message')
    rating = data.get('rating', 5) # Default to 5 stars if not provided
    
    if not doctor_id or not message:
        return jsonify({"error": "doctor_id and message are required"}), 400
    
    try:
        if db_client.db is not None:
            # Verify patient is assigned to this doctor
            patient = db_client.db.patients.find_one({"$or": [{"user_id": patient_id}, {"name": patient_name}]})
            if not patient or patient.get("treating_doctor") != doctor_id:
                 # Fallback check if ID format differs
                 if not patient or str(patient.get("treating_doctor")) != str(doctor_id):
                    return jsonify({"error": "You can only provide feedback for your assigned physician."}), 403

            feedback_record = {
                "patient_id": patient_id,
                "patient_name": patient_name,
                "doctor_id": doctor_id,
                "message": message,
                "rating": rating,
                "timestamp": datetime.utcnow(),
                "status": "pending"
            }
            
            db_client.db.doctor_feedback.insert_one(feedback_record)
            
            return jsonify({
                "status": "success",
                "message": "Feedback submitted successfully. It will be reviewed by the administration."
            })
        
        return jsonify({"error": "Database offline"}), 500
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@doctor_review_bp.route('/all-feedback', methods=['GET'])
def get_all_feedback():
    """Admin only: Get all patient feedback."""
    try:
        if db_client.db is not None:
            feedback_list = list(db_client.db.doctor_feedback.find().sort("timestamp", -1))
            
            # Get doctor details for each feedback
            doctor_ids = list(set([f["doctor_id"] for f in feedback_list]))
            doctors = list(db_client.db.users.find({"$or": [{"user_id": {"$in": doctor_ids}}, {"_id": {"$in": doctor_ids}}]}))
            doctor_map = {str(doc.get("user_id") or doc["_id"]): doc.get("name", "Unknown") for doc in doctors}
            
            for f in feedback_list:
                f["_id"] = str(f["_id"])
                f["doctor_name"] = doctor_map.get(str(f["doctor_id"]), "Unknown Doctor")
                if isinstance(f.get("timestamp"), datetime):
                    f["timestamp"] = f["timestamp"].isoformat()
            
            return jsonify({"status": "success", "data": feedback_list})
        
        return jsonify({"status": "success", "data": []})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@doctor_review_bp.route('/resolve-flag', methods=['POST'])
def resolve_flag():
    """Resolve a doctor flag."""
    data = request.get_json()
    flag_id = data.get('flag_id')
    resolution_notes = data.get('resolution_notes', '')
    resolved_by = data.get('resolved_by', 'admin')
    
    if not flag_id:
        return jsonify({"error": "flag_id is required"}), 400
    
    try:
        if db_client.db is not None:
            # Update flag status
            result = db_client.db.doctor_flags.update_one(
                {"_id": flag_id},
                {
                    "$set": {
                        "status": "resolved",
                        "resolution_notes": resolution_notes,
                        "resolved_by": resolved_by,
                        "resolved_date": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                return jsonify({
                    "status": "success",
                    "message": "Flag resolved successfully"
                })
            else:
                return jsonify({"error": "Flag not found"}), 404
        
        else:
            return jsonify({
                "status": "success",
                "message": "Flag resolved successfully (fallback mode)"
            })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to resolve flag: {str(e)}"}), 500

def calculate_doctor_score(total_patients, total_assessments, avg_confidence, risk_distribution):
    """Calculate a performance score for a doctor based on multiple factors."""
    score = 0
    
    # Base score for having patients (0-20 points)
    if total_patients > 0:
        score += min(20, total_patients * 2)  # 2 points per patient, max 20
    
    # Assessment frequency (0-20 points)
    if total_patients > 0:
        assessments_per_patient = total_assessments / total_patients
        score += min(20, assessments_per_patient * 5)  # 5 points per assessment per patient, max 20
    
    # Average confidence (0-20 points)
    score += avg_confidence * 20
    
    # Risk management (0-40 points)
    total_risk_patients = risk_distribution["high"] + risk_distribution["moderate"] + risk_distribution["low"]
    if total_risk_patients > 0:
        # Better scores for identifying high-risk patients (they need more attention)
        high_risk_ratio = risk_distribution["high"] / total_risk_patients
        moderate_risk_ratio = risk_distribution["moderate"] / total_risk_patients
        
        # Reward for identifying high-risk patients (they're being monitored)
        score += high_risk_ratio * 20  # Up to 20 points for high-risk identification
        score += moderate_risk_ratio * 10  # Up to 10 points for moderate-risk
        score += (risk_distribution["low"] / total_risk_patients) * 10  # Up to 10 points for low-risk management
    
    return min(100, score)  # Cap at 100

def get_performance_status(score):
    """Get performance status based on score."""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Average"
    elif score >= 50:
        return "Needs Improvement"
    else:
        return "Poor"
