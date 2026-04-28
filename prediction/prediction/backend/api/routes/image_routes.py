from flask import Blueprint, request, jsonify
from services.runtime_services import get_image_classifier

image_bp = Blueprint('image', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@image_bp.route('/image-predict', methods=['POST'])
def predict_image():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file uploaded. Use form field 'image'."}), 400

        file = request.files['image']

        if file.filename == '':
            return jsonify({"error": "Empty filename."}), 400

        if not allowed_file(file.filename):
            return jsonify({
                "error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400

        image_bytes = file.read()

        if len(image_bytes) > MAX_FILE_SIZE:
            return jsonify({"error": "File too large. Maximum size is 10MB."}), 400

        if len(image_bytes) == 0:
            return jsonify({"error": "Empty file uploaded."}), 400

        classifier = get_image_classifier()
        result = classifier.predict(image_bytes)

        # 1. Save to MongoDB Dashboard
        from utils.db import db_client
        import datetime
        patient_id = request.form.get("patient_id", "web_user")
        record_id = None
        if db_client.db is not None:
            try:
                record_doc = {
                    "patient_id": patient_id,
                    "disease": "Dermatology",
                    "risk": result["severity"],
                    "confidence": result["confidence"],
                    "input_method": "image_scan",
                    "timestamp": datetime.datetime.utcnow(),
                    "classification": result["classification"],
                    "recommendations": {
                        "lifestyle": [result["description"]],
                        "medical": [result["recommended_action"]],
                        "precautions": ["URGENT: Consult professional dermatology for definitive biopsy."] if result["severity"] == "Critical" else ["Monitor daily."]
                    }
                }
                insert_res = db_client.db.medical_records.insert_one(record_doc)
                record_id = str(insert_res.inserted_id)
                print(f"[IMAGE] Saved scan result: {record_id}")
            except Exception as dberr:
                print(f"[DB ERROR] Image save failed: {dberr}")

        return jsonify({
            "status": "success",
            "record_id": record_id,
            "classification": result["classification"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "description": result["description"],
            "recommended_action": result["recommended_action"],
            "differential_diagnosis": result["differential_diagnosis"],
            "disclaimer": "This is an AI-assisted analysis and should not replace professional medical diagnosis."
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to process image."}), 500
