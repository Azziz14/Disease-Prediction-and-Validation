from flask import Blueprint, request, jsonify
from services.prediction_service import PredictionService
from services.report_service import ReportService

diagnosis_bp = Blueprint('diagnosis', __name__)

# Global singleton — avoids reloading heavy models per request
predictor = PredictionService()
report_gen = ReportService()


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
        result = predictor.handle_prediction(features, prescription, disease_type=disease_context)

        # Generate health report
        report = report_gen.generate_report(result, features, prescription)

        # Auto-suggest medications if no prescription was provided
        auto_medications = []
        if not prescription or len(prescription.strip()) == 0:
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

        # Log to Database
        try:
            from utils.db import db_client
            import datetime
            if db_client.db is not None:
                db_client.db.predictions.insert_one({
                    "patient_id": data.get("patient_id", "guest"),
                    "disease": result["disease"],
                    "risk": result["risk"],
                    "confidence": result["confidence"],
                    "timestamp": datetime.datetime.utcnow()
                })
        except Exception as db_e:
            import logging
            logging.error(f"Failed to log prediction to DB: {db_e}")

        return jsonify(response_payload)

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error during inference."}), 500