from flask import Blueprint, request, jsonify
from services.prediction_runtime import get_prediction_service, get_report_service
import concurrent.futures
import logging

diagnosis_bp = Blueprint('diagnosis', __name__)

# Global singleton — avoids reloading heavy models per request
@diagnosis_bp.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "Invalid JSON format"}), 400

        features = data.get("features", [])
        prescription = data.get("prescription", "")
        disease_context = data.get("disease", "diabetes")

        if not features or len(features) != 8:
            return jsonify({"error": "Exactly 8 structural features are required for inference."}), 400

        # Prescription is now OPTIONAL — if not provided, we auto-suggest medications
        # Run unified ML + NLP + Drug pipeline
        predictor = get_prediction_service()
        report_gen = get_report_service()
        import concurrent.futures
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(predictor.handle_prediction, features, prescription, disease_type=disease_context)
                result = future.result(timeout=30)
        except concurrent.futures.TimeoutError:
            return jsonify({"error": "Analysis timeout (30s). Try shorter input or check logs."}), 408
        except Exception as pred_e:
            import logging
            logging.error(f"Prediction failed: {pred_e}")
            raise

        # Generate health report
        try:
            report = report_gen.generate_report(result, features, prescription)
        except Exception as report_e:
            import logging
            logging.error(f"Report generation failed: {report_e}")
            report = {}

        # 5. GENERATIVE AUTO-MEDICATIONS (Dynamic AI vs Static Fallback)
        auto_medications = result.get("recommendations", {}).get("medications", [])
        
        if not auto_medications:
            try:
                from services.voice_intake_service import VoiceIntakeService
                vis = VoiceIntakeService()
                auto_medications = vis.get_auto_medications(disease_context, result["risk"])
            except Exception:
                pass

        # Structured API response matching spec
        response_payload = {
            "risk": result["risk"],
            "confidence": result["confidence"],
            "disease": result["disease"],
            "explanation": result["explanation"],
            "model_metadata": result.get("model_metadata", {}),
            "entities": result.get("entities", {}),
            "matched_drugs": result["matched_drugs"],
            "suggestions": result["suggestions"],
            "drug_interactions": result["drug_interactions"],
            "drug_details": result["drug_details"],
            "report": report,
            "auto_medications": auto_medications,
            "abnormalities": result.get("abnormalities", []),
            "recommendations": result.get("recommendations", {}),
            "prescription_evaluation": result.get("prescription_evaluation"),
            # Multi-disease risk summary
            "diabetes_risk": result["risk"] if disease_context == "diabetes" else "Low",
            "heart_risk": result["risk"] if disease_context == "heart" else "Low",
            "mental_risk": result["risk"] if disease_context == "mental" else "Low"
        }

        # Log to Unified Clinical Vault (Medical Records)
        try:
            from utils.db import db_client
            import datetime
            if db_client.db is not None:
                patient_id = data.get("patient_id", "web_user").strip().lower()
                patient_name = data.get("patient_name", "Unknown Patient")
                treating_doctor = data.get("treating_doctor", "Unspecified Physician")
                treating_doctor_id = data.get("treating_doctor_id", "").strip().lower()
                if not treating_doctor_id and treating_doctor != "Unspecified Physician":
                    # Fallback to name-based lookup if ID is missing but name exists
                    doc_user = db_client.db.users.find_one({"name": treating_doctor, "role": "doctor"})
                    if doc_user:
                        treating_doctor_id = doc_user.get("email") or str(doc_user["_id"])

                record_doc = {
                    "patient_id": patient_id,
                    "patient_name": patient_name,
                    "treating_doctor": treating_doctor,
                    "treating_doctor_id": treating_doctor_id or "unspecified_physician",
                    "disease": result["disease"],
                    "risk": result["risk"],
                    "confidence": result["confidence"],
                    "timestamp": datetime.datetime.utcnow(),
                    "date": datetime.datetime.utcnow().isoformat(), 
                    "auto_medications": auto_medications,
                    "recommendations": result.get("recommendations", {}),
                    "drug_interactions": result.get("drug_interactions", []),
                    "matched_drugs": result.get("matched_drugs", []),
                    "prescription_evaluation": result.get("prescription_evaluation", {}),
                    "input_method": "manual_protocol", 
                    "glucose": features[1] if result["disease"] == "diabetes" else None,
                    "blood_pressure": features[2] if result["disease"] == "diabetes" else (features[3] if result["disease"] == "heart" else None)
                }
                
                db_client.db.medical_records.insert_one(record_doc)
                db_client.db.predictions.insert_one(record_doc) # Maintain redundancy in legacy collection
        except Exception as db_e:
            import logging
            logging.error(f"Vault Backup Failure: {db_e}")

        return jsonify(response_payload)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error during inference."}), 500
