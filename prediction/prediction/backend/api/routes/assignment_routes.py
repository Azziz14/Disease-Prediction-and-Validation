from flask import Blueprint, request, jsonify
from utils.db import db_client
from datetime import datetime
import traceback
from bson import ObjectId

assignment_bp = Blueprint('assignment', __name__)

@assignment_bp.route('/doctor-patients', methods=['GET'])
def get_doctor_patients():
    """UNIFIED & ROBUST: Fetch doctor patients using Mirror-ID Resolution."""
    doctor_id = request.args.get('doctor_id')
    
    if not doctor_id:
        return jsonify({"error": "doctor_id is required"}), 400
    
    try:
        if db_client.db is not None:
            # Resolve ALL possible ID formats this doctor could be stored under
            doc_ids = [doctor_id]
            try:
                doc_ids.append(ObjectId(doctor_id))
            except:
                pass
            
            # Find the user document to get all their ID variants
            user_doc = db_client.db.users.find_one({
                "$or": [
                    {"id": doctor_id},
                    {"user_id": doctor_id},
                    {"_id": doctor_id}
                ]
            })
            if user_doc:
                if user_doc.get("id"): doc_ids.append(user_doc["id"])
                if user_doc.get("user_id"): doc_ids.append(user_doc["user_id"])
                doc_ids.append(str(user_doc["_id"]))

            # Deduplicate
            doc_ids = list(set(str(d) for d in doc_ids))

            # Fetch patients whose treating_doctor matches ANY of the doctor's IDs
            patients = list(db_client.db.patients.find({"treating_doctor": {"$in": doc_ids}}))
            
            result = []
            for patient in patients:
                p_id = patient.get("user_id") or patient.get("id") or str(patient["_id"])
                
                # Prefer the real name from the users collection (authoritative source)
                user_doc = db_client.db.users.find_one({"user_id": p_id})
                p_name = (user_doc.get("name") if user_doc else None) or patient.get("name", "Unknown Patient")
                
                # Fetch recent predictions for this patient
                predictions = list(db_client.db.predictions.find({"patient_id": p_id}).sort("timestamp", -1).limit(5))
                for pred in predictions: pred["_id"] = str(pred["_id"])

                result.append({
                    # Return BOTH naming conventions so frontend works regardless
                    "id": p_id,
                    "name": p_name,
                    "patient_id": p_id,
                    "patient_name": p_name,
                    "assigned_date": str(patient.get("created_at", "")),
                    "predictions": predictions
                })
            
            return jsonify({"status": "success", "data": result})
        
        else:
            return jsonify({"status": "success", "data": []})
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed to fetch doctor patients: {str(e)}"}), 500

@assignment_bp.route('/assign-patient', methods=['POST'])
def assign_patient_to_doctor():
    """UNIFIED: Permanent Anchor in Master Patients Collection."""
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_query = data.get('patient_id')
    patient_name = data.get('patient_name', '')
    
    if not doctor_id or not patient_query:
        return jsonify({"error": "doctor_id and patient_id are required"}), 400
    
    try:
        if db_client.db is not None:
            # Ensure we update the MASTER record
            # Try finding existing patient by ID, Email, or Name
            patient_doc = db_client.db.patients.find_one({"user_id": patient_query})
            if not patient_doc:
                try: patient_doc = db_client.db.patients.find_one({"_id": ObjectId(patient_query)})
                except: pass
            
            if not patient_doc:
                patient_doc = db_client.db.patients.find_one({"name": patient_name})

            if patient_doc:
                # Fetch doctor name for retroactive record update
                doc_name = "Unspecified Physician"
                doc_doc = db_client.db.users.find_one({"$or": [{"user_id": doctor_id}, {"_id": doctor_id}]})
                if doc_doc: doc_name = doc_doc.get("name", doc_name)

                db_client.db.patients.update_one(
                    {"_id": patient_doc["_id"]},
                    {"$set": {"treating_doctor": doctor_id, "name": patient_name}}
                )
                
                # RETROACTIVE SYNC: Update all existing records to appear in new doctor's dashboard
                p_id = patient_doc.get("user_id") or str(patient_doc["_id"])
                sync_filter = {"$or": [{"patient_id": p_id}, {"patient_name": patient_name}]}
                db_client.db.medical_records.update_many(sync_filter, {"$set": {"treating_doctor_id": doctor_id, "treating_doctor": doc_name}})
                db_client.db.predictions.update_many(sync_filter, {"$set": {"treating_doctor_id": doctor_id, "treating_doctor": doc_name}})
            else:
                # New entry in master registry
                db_client.db.patients.insert_one({
                    "user_id": patient_query if patient_query.startswith("pat_") else f"pat_{ObjectId().hex[:8]}",
                    "name": patient_name,
                    "treating_doctor": doctor_id,
                    "created_at": datetime.utcnow()
                })
            
            return jsonify({ "status": "success", "message": "Clinical Anchor Secured" })
        return jsonify({ "status": "success", "message": "Fallback" })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed: {str(e)}"}), 500

@assignment_bp.route('/unassign-patient', methods=['POST'])
def unassign_patient_from_doctor():
    data = request.get_json()
    doctor_id = data.get('doctor_id')
    patient_id = data.get('patient_id')
    
    if not doctor_id or not patient_id:
        return jsonify({"error": "doctor_id and patient_id are required"}), 400
    
    try:
        if db_client.db is not None:
            db_client.db.patients.update_one(
                {"$or": [{"user_id": patient_id}, {"name": patient_id}]}, 
                {"$unset": {"treating_doctor": ""}}
            )
            return jsonify({ "status": "success", "message": "Identity Cleared" })
        return jsonify({ "status": "success", "message": "Fallback" })
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Failed: {str(e)}"}), 500

@assignment_bp.route('/all-assignments', methods=['GET'])
def get_all_assignments():
    try:
        if db_client.db is not None:
            patients = list(db_client.db.patients.find({"treating_doctor": {"$exists": True, "$ne": ""}}))
            result = []
            for pat in patients:
                d_id = pat.get("treating_doctor")
                d_user = db_client.db.users.find_one({"$or": [{"user_id": d_id}, {"_id": d_id}]})
                result.append({
                    "assignment_id": str(pat["_id"]),
                    "doctor_id": d_id,
                    "doctor_name": d_user.get("name", "Unknown") if d_user else "Unknown",
                    "doctor_email": d_user.get("email", "") if d_user else "",
                    "patient_id": pat.get("user_id") or str(pat["_id"]),
                    "patient_name": pat.get("name", "Unknown"),
                    "assigned_date": pat.get("created_at"),
                    "status": "active"
                })
            return jsonify({"status": "success", "data": result})
        return jsonify({"status": "success", "data": []})
    except:
        return jsonify({"error": "Fail"}), 500

@assignment_bp.route('/patient-assignment', methods=['GET'])
def get_patient_assignment():
    """Retrieve the assigned doctor for a specific patient."""
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({"error": "patient_id required"}), 400
        
    try:
        if db_client.db is not None:
            # Search patients collection first (by user_id, _id, or name)
            patient = db_client.db.patients.find_one({
                "$or": [
                    {"user_id": patient_id},
                    {"_id": patient_id},
                    {"name": patient_id}
                ]
            })

            # If not in patients collection, check if user has direct assignment in users collection
            if not patient:
                user_doc = db_client.db.users.find_one({
                    "$or": [{"id": patient_id}, {"user_id": patient_id}]
                })
                if user_doc:
                    # Use user's user_id to find patient record
                    uid = user_doc.get("user_id") or user_doc.get("id")
                    patient = db_client.db.patients.find_one({"user_id": uid})

            if not patient:
                return jsonify({"status": "success", "assigned": False})
                
            doc_id = patient.get("treating_doctor")
            if not doc_id:
                return jsonify({"status": "success", "assigned": False})

            # Find doctor by any ID format
            doc = db_client.db.users.find_one({
                "$or": [
                    {"user_id": doc_id},
                    {"id": doc_id},
                    {"_id": doc_id}
                ]
            })
            return jsonify({
                "status": "success", 
                "assigned": True,
                "doctor_id": doc_id,
                "doctor_name": doc.get("name", "Unknown Practitioner") if doc else "Unknown Practitioner"
            })
        return jsonify({"error": "DB offline"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
