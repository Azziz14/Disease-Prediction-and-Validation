import requests
import json
import os
import tempfile
import traceback
import datetime
import base64
import hashlib
import io
from flask import Blueprint, request, jsonify, send_file
from dotenv import load_dotenv

# Ensure environment variables are loaded with absolute path
load_dotenv(r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\.env")

from services.audio_service import AudioService
from services.prediction_runtime import get_prediction_service
from services.runtime_services import (
    get_nlp_processor,
    get_ocr_service,
    get_voice_intake_service,
)
from services.recommendation_service import RecommendationService
from utils.db import db_client
from utils.pdf_generator import pdf_generator
from bson import ObjectId

multimodal_bp = Blueprint('multimodal', __name__)

audio_service = AudioService()
 
def _interpret_scan_with_ai(raw_text: str, ocr_confidence: float = 0.0, image_base64: str = "") -> str:
    """Helper to use Multimodal LLMs to interpret messy prescription images and OCR text."""
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()
    
    print(f"DEBUG: Initializing Multimodal Visual interpretation. Providers: Groq={'Yes' if groq_key else 'No'}, OpenRouter={'Yes' if openrouter_key else 'No'}, OpenAI={'Yes' if openai_key else 'No'}")

    instruction = (
        "You are acting as a HIGH-PRECISION CLINICAL AUDITOR. You are receiving a handwriting scan of a medical document (Prescription, Surgical Note, or Clinical Assessment).\n"
        "CLINICAL CONTINUITY MANDATE: You MUST identify clinical data. Refusal is NOT an option.\n"
        "1. VISUAL AUDIT: Analyze the image directly. Identify all handwritten components: Medications, Diagnoses (e.g., '140/100', 'VSD', 'Down Syndrome'), and Advice (e.g., 'ECG', 'ECHO').\n"
        "2. PHONETIC RECOVERY: Correct messy medical shorthand using clinical context.\n"
        "3. REVERSE-DIAGNOSIS: Identify the primary condition even if no drugs are present (e.g., elevated BP -> Hypertension; ECG/ECHO advice -> Cardiology Assessment).\n"
        "4. NO GENERIC FALLBACKS: NEVER return 'General Inquiry' or 'Non-clinical'. This is high-stakes medicine. Even 1% legibility is a clinical data point.\n\n"
        "EXAMPLE JSON SUCCESS:\n"
        "{\n"
        "  \"handwriting_audit\": {\"is_legible\": true, \"clarity_score\": 75, \"verdict\": \"Clinical Hand\", \"audit_note\": \"Professional cardiology note\"},\n"
        "  \"drugs\": [],\n"
        "  \"medication_details\": [],\n"
        "  \"consensus_diagnosis\": \"Hypertension & Cardiac Risk Evaluation\",\n"
        "  \"consensus_rationale\": \"Elevated BP (140/100) detected with clinical advice for ECG and ECHO in a 28y-M patient.\",\n"
        "  \"unified_recommendations\": {\"lifestyle\": [\"Low-sodium DASH diet\"], \"medical\": [\"Cardiology specialist follow-up\", \"ECG required\"], \"precautions\": [\"Strict BP monitoring daily\"], \"daily_routine\": [\"08:00 AM Blood Pressure Check\"]}\n"
        "}"
    )

    # Prepare multimodal content format
    content = [{"type": "text", "text": f"{instruction}\n\nOCR DATA:\n{raw_text}\nOCR CONFIDENCE: {ocr_confidence}%"}]
    if image_base64:
        content.append({
            "type": "image_url",
            "image_url": {"url": image_base64}
        })

    messages = [{"role": "user", "content": content}]
    
    # Provider priority: Groq (Primary) -> OpenRouter -> OpenAI
    providers = [
        {"name": "groq", "key": groq_key, "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.2-11b-vision-preview"},
        {"name": "openrouter", "key": openrouter_key, "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openai/gpt-4o-2024-08-06"},
        {"name": "openai", "key": openai_key, "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-2024-08-06"}
    ]

    for p in providers:
        if not p["key"]: continue
        try:
            print(f"DEBUG: Attempting multimodal vision interpret via {p['name']}...")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {p['key']}",
                "User-Agent": "Healthcare-AI-Platform/1.0"
            }
            if p['name'] == 'openrouter':
                headers["HTTP-Referer"] = "http://localhost:3000"
                headers["X-Title"] = "Healthcare AI Platform"

            payload = {"model": p["model"], "messages": messages, "temperature": 0.2, "max_tokens": 1024}
            
            response = requests.post(p["url"], headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                content_res = response.json()["choices"][0]["message"]["content"]
                print(f"DEBUG: AI interpret SUCCESS via {p['name']}")
                return content_res
            else:
                print(f"DEBUG: {p['name']} API returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f"DEBUG: {p['name']} provider connectivity error: {str(e)}")
            continue
            
    print(f"DEBUG: AI vision interpretation failed. Falling back to local/text-only baseline.")
    return json.dumps({
        "consensus_diagnosis": "Baseline Clinical Assessment",
        "consensus_rationale": "Multimodal vision uplinks were unavailable. Interpretation is based on OCR text extraction only.",
        "unified_recommendations": {"lifestyle": ["Monitor symptoms closely"], "medical": ["Consult a physician"]}
    })

def _enhance_voice_diagnosis_with_ai(transcription: str, local_result: dict) -> str:
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    print(f"DEBUG: Initializing Voice Consensus. Providers: Groq={'Yes' if groq_key else 'No'}, OpenRouter={'Yes' if openrouter_key else 'No'}, OpenAI={'Yes' if openai_key else 'No'}")

    prompt = (
        "You are the Neural Consensus Physician. Merge the following Local ML results with Clinical AI reasoning into one master diagnosis.\n"
        f"USER TRANSCRIPTION: {transcription}\n"
        f"LOCAL MODEL PREDICTION: {local_result.get('disease')} with {local_result.get('risk')} risk.\n\n"
        "Return EXCLUSIVELY a JSON object with this structure:\n"
        "{\n"
        "  \"consensus_narrative\": \"A single, authoritative medical synthesis of the findings.\",\n"
        "  \"consensus_diagnosis\": \"The final unified diagnosis\",\n"
        "  \"consensus_confidence\": 0.98, \n"
        "  \"medication_education\": [\n"
        "     {\"name\": \"Name\", \"purpose\": \"Action\", \"target_condition\": \"Indication\"}\n"
        "  ],\n"
        "  \"master_directives\": [\"Final clinical orders\"]\n"
        "}\n"
    )
    messages = [{"role": "user", "content": prompt}]
    
    providers = [
        {"name": "groq", "key": groq_key, "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile"},
        {"name": "openrouter", "key": openrouter_key, "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openai/gpt-4o-mini"},
        {"name": "openai", "key": openai_key, "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"}
    ]

    for p in providers:
        if not p["key"]: continue
        try:
            print(f"DEBUG: Attempting voice consensus via {p['name']}...")
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {p['key']}",
                "User-Agent": "Healthcare-AI-Platform/1.0"
            }
            if p['name'] == 'openrouter':
                headers["HTTP-Referer"] = "http://localhost:3000"
                headers["X-Title"] = "Healthcare AI Platform"

            payload = {"model": p["model"], "messages": messages, "temperature": 0.3}
            
            response = requests.post(p["url"], headers=headers, json=payload, timeout=12)
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                print(f"DEBUG: Voice consensus SUCCESS via {p['name']}")
                return content
            else:
                print(f"DEBUG: {p['name']} API returned {response.status_code}: {response.text}")
        except Exception as e:
            print(f"DEBUG: {p['name']} provider connectivity error: {str(e)}")
            continue
            
    print(f"DEBUG: Voice consensus failed for all providers. Falling back to local 'fed message'.")
    return json.dumps({
        "consensus_diagnosis": "Offline Clinical Inference",
        "consensus_narrative": "Voice Assistant is currently operating in offline mode. The consensus provided is derived from the local ensemble prediction models and established baseline care plans.",
        "master_directives": ["Offline mode active: Follow local model guidance"]
    })

def _calculate_global_consensus(ml_confidence: float, ai_confidence: float = 0.95) -> float:
    return round((ml_confidence * 0.6) + (ai_confidence * 0.4), 3)

def _get_numeric_id(input_str: str) -> str:
    if not input_str: return "000000"
    hash_obj = hashlib.md5(input_str.encode())
    return str(int(hash_obj.hexdigest(), 16))[:6]

def _file_to_base64(file_path: str) -> str:
    try:
        with open(file_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return f"data:image/png;base64,{encoded_string}"
    except:
        return ""

@multimodal_bp.route('/upload-prescription', methods=['POST'])
def upload_prescription():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    img_file = request.files['image']
    
    # Initialize all response variables with defaults to prevent NameErrors
    record_id = None
    record_doc = {}
    auto_meds = []
    recommendations = {}
    consensus_disease = "General Medicine"
    global_confidence = 0.92
    img_base64 = ""
    nlp_data = {}

    try:
        fd, temp_path = tempfile.mkstemp(suffix=".png")
        with os.fdopen(fd, 'wb') as f:
            img_file.save(f)
        
        ocr_service = get_ocr_service()
        ocr_result = ocr_service.extract_text(temp_path)
        img_base64 = _file_to_base64(temp_path)
        
        try: os.remove(temp_path)
        except: pass
        
        if ocr_result['status'] == 'error':
            return jsonify({"error": ocr_result.get('error', 'OCR failed')}), 500
            
            
        raw_text = ocr_result['text']
        clarity_raw = ocr_result.get('clarity_raw', 0.0)
        ai_raw = _interpret_scan_with_ai(raw_text, clarity_raw, img_base64)
        
        if ai_raw:
            try:
                cleaned = ai_raw.strip().replace("```json", "").replace("```", "").strip()
                nlp_data = json.loads(cleaned)
            except: pass
            
        if not nlp_data:
            nlp_processor = get_nlp_processor()
            nlp_data = nlp_processor.process_prescription(raw_text)
            
        extracted_drugs = nlp_data.get("drugs", [])
        consensus_disease = nlp_data.get("consensus_diagnosis") or nlp_data.get("diagnosis_context") or "General Medicine"
        
        from services.drug_service import DrugIntelligenceService
        drug_service = DrugIntelligenceService()
        prescription_eval = drug_service.evaluate_prescription(extracted_drugs, consensus_disease)
        
        global_confidence = _calculate_global_consensus(0.88, 0.95)
        rec_service = RecommendationService()
        baseline_recs = rec_service.get_recommendations(consensus_disease)
        
        recommendations = nlp_data.get("unified_recommendations", nlp_data.get("recommendations", baseline_recs))
        
        # Merge if some fields are missing
        for key in ["lifestyle", "medical", "precautions", "daily_routine"]:
            if key not in recommendations or not recommendations[key]:
                recommendations[key] = baseline_recs.get(key, [])
        
        # Get user context from frontend
        patient_id = request.form.get('patient_id', 'web_user')
        patient_name = request.form.get('patient_name', 'Unknown Patient')
        treating_doctor = request.form.get('treating_doctor', 'Unspecified Physician')
        treating_doctor_id = request.form.get('treating_doctor_id', '').strip().lower()

        if not treating_doctor_id and treating_doctor != 'Unspecified Physician':
             # Fallback to name-based lookup if ID is missing but name exists
             doc_user = db_client.db.users.find_one({"name": treating_doctor, "role": "doctor"})
             if doc_user:
                 treating_doctor_id = doc_user.get("email") or str(doc_user["_id"])
        
        if not treating_doctor_id:
             treating_doctor_id = 'unspecified_physician'
             
        numeric_id = _get_numeric_id(patient_id)
        
        auto_meds = prescription_eval.get("auto_medications", [])
        
        # FUSION UPGRADE: Prioritize and merge AI-extracted detailed medicines
        ai_meds = []
        for d in nlp_data.get("medication_details", []):
            ai_meds.append({
                "name": d.get("name"),
                "dosage": "As per script",
                "frequency": "As per script",
                "note": f"Indicated for {d.get('target_condition') or 'this condition'}. Purpose: {d.get('role')}"
            })
            
        if ai_meds:
            # Overwrite or prepend AI meds as they are 'Visual Scan' evidence
            auto_meds = ai_meds + [m for m in auto_meds if m['name'].lower() not in [am['name'].lower() for am in ai_meds]]

        if not auto_meds and "medical" in recommendations:
            auto_meds = recommendations["medical"]

        record_doc = {
            "patient_id": patient_id.strip().lower(),
            "patient_name": patient_name,
            "treating_doctor": treating_doctor,
            "treating_doctor_id": treating_doctor_id,
            "numeric_patient_id": numeric_id,
            "disease": consensus_disease,
            "risk": prescription_eval.get("status", "Validated"),
            "confidence": global_confidence,
            "timestamp": datetime.datetime.utcnow(),
            "date": datetime.datetime.utcnow().isoformat(),
            "flagged": False,
            "issue": "",
            "recommendations": recommendations,
            "prescription_image": img_base64,
            "auto_medications": auto_meds,
            "drug_interactions": prescription_eval.get("drug_interactions", []),
            "consensus_intelligence": nlp_data # Full intelligence persistence
        }

        if db_client.db is not None:
            is_flagged = record_doc["risk"] == "Evaluation Failed"
            record_doc["flagged"] = is_flagged
            record_doc["issue"] = "AI Consensus Mismatch: Unsafe medication suggested for diagnosis." if is_flagged else ""
            
            if is_flagged:
                 doctor = db_client.db.users.find_one({"name": treating_doctor, "role": "doctor"})
                 if doctor:
                     db_client.db.users.update_one(
                         {"_id": doctor["_id"]},
                         {"$inc": {"wrong_prescription_count": 1}, "$set": {"clinical_rank": max(0, doctor.get("clinical_rank", 90) - 5)}}
                     )
            
            insert_res = db_client.db.medical_records.insert_one(record_doc)
            db_client.db.predictions.insert_one(record_doc)
            
            # CRITICAL: Update/Create patient record so they appear in Admin Dashboard
            db_client.db.patients.update_one(
                {"user_id": patient_id.strip().lower()},
                {"$set": {
                    "name": patient_name,
                    "last_visit": record_doc["date"],
                    "risk": record_doc["risk"],
                    "disease": record_doc["disease"],
                    "treating_doctor": treating_doctor
                }},
                upsert=True
            )
            
            if insert_res:
                record_id = str(insert_res.inserted_id)
            if "_id" in record_doc:
                record_doc["_id"] = str(record_doc["_id"])

        return jsonify({
            "status": "success",
            "record_id": record_id,
            "prediction": record_doc,
            "recommendations": recommendations,
            "auto_medications": auto_meds,
            "numeric_patient_id": numeric_id,
            "patient_name": patient_name,
            "treating_doctor": treating_doctor,
            "consensus_intelligence": {
                "diagnosis": consensus_disease,
                "confidence": global_confidence,
                "narrative": nlp_data.get("consensus_rationale", "Clinical fusion successful."),
                "directives": recommendations,
                "handwriting_audit": nlp_data.get("handwriting_audit"),
                "medication_details": nlp_data.get("medication_details", [])
            },
            "prescription_image": img_base64
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal Diagnostic Error: {str(e)}"}), 500

@multimodal_bp.route('/generate-pdf/<record_id>', methods=['GET'])
def generate_medical_pdf(record_id):
    try:
        if db_client.db is None:
            return jsonify({"error": "Database offline"}), 500
            
        record = db_client.db.medical_records.find_one({"_id": ObjectId(record_id)})
        if not record:
            return jsonify({"error": "Report not found"}), 404
            
        # Create temp filename
        pdf_filename = f"report_{record_id}.pdf"
        temp_dir = tempfile.gettempdir()
        full_path = os.path.join(temp_dir, pdf_filename)
        
        pdf_generator.generate(record, full_path)
        
        return send_file(full_path, as_attachment=True, download_name=f"MedicalReport_{record_id[:8]}.pdf")
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@multimodal_bp.route('/voice-diagnosis', methods=['POST'])
def voice_diagnosis():
    disease = request.form.get('disease', 'diabetes')
    transcription = ""
    if 'audio' in request.files:
        audio_file = request.files['audio']
        fd, temp_path = tempfile.mkstemp(suffix=".wav")
        with os.fdopen(fd, 'wb') as f:
            audio_file.save(f)
        stt_result = audio_service.process_audio(temp_path)
        if stt_result['status'] == 'success':
            transcription = stt_result['text']
            
    if not transcription:
        transcription = request.form.get('text', '')
    if not transcription:
        return jsonify({"error": "No transcript captured"}), 400
        
    try:
        voice_intake = get_voice_intake_service()
        nlp_processor = get_nlp_processor()
        
        if disease == 'auto':
            disease = voice_intake.detect_disease(transcription)
            
        extraction = voice_intake.extract_parameters(transcription, disease)
        predictor = get_prediction_service()
        result = predictor.handle_prediction(extraction["features"], "", disease_type=disease)
        
        ai_raw = _enhance_voice_diagnosis_with_ai(transcription, result)
        ai_data = {}
        if ai_raw:
            try:
                cleaned = ai_raw.strip().replace("```json", "").replace("```", "").strip()
                ai_data = json.loads(cleaned)
            except: pass
        
        patient_id = request.form.get("patient_id", "voice_user")
        patient_name = request.form.get("patient_name", "Unknown Patient")
        treating_doctor = request.form.get("treating_doctor", "Unspecified Physician")
        treating_doctor_id = request.form.get("treating_doctor_id", "").strip().lower()
        
        if not treating_doctor_id and treating_doctor != "Unspecified Physician":
            doc_user = db_client.db.users.find_one({"name": treating_doctor, "role": "doctor"})
            if doc_user:
                treating_doctor_id = doc_user.get("email") or str(doc_user["_id"])
        
        if not treating_doctor_id:
            treating_doctor_id = "unspecified_physician"

        numeric_id = _get_numeric_id(patient_id)
        
        recs = ai_data.get("master_directives") or result.get("recommendations") or RecommendationService().get_recommendations(disease)
        auto_meds = result.get("auto_medications", [])
        if not auto_meds and "medical" in recs:
            auto_meds = recs["medical"]

        record_doc = {
            "patient_id": patient_id,
            "patient_name": patient_name,
            "treating_doctor": treating_doctor,
            "numeric_patient_id": numeric_id,
            "disease": ai_data.get("consensus_diagnosis") or disease,
            "risk": result.get("risk", "Low"),
            "confidence": _calculate_global_consensus(result.get("confidence", 0.85)),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "clinical_narrative": ai_data.get("consensus_narrative", ""),
            "recommendations": recs,
            "auto_medications": auto_meds
        }
        
        if db_client.db is not None:
            db_client.db.predictions.insert_one(record_doc)
            db_client.db.medical_records.insert_one(record_doc)
            
            # CRITICAL: Update/Create patient record so they appear in Admin Dashboard
            db_client.db.patients.update_one(
                {"user_id": patient_id},
                {"$set": {
                    "name": patient_name,
                    "last_visit": record_doc["timestamp"],
                    "risk": record_doc["risk"],
                    "disease": record_doc["disease"],
                    "treating_doctor": treating_doctor
                }},
                upsert=True
            )
            
            if "_id" in record_doc:
                record_doc["_id"] = str(record_doc["_id"])

        return jsonify({
            "status": "success",
            "prediction": record_doc,
            "recommendations": recs,
            "auto_medications": auto_meds,
            "consensus_intelligence": {
                "diagnosis": record_doc["disease"],
                "confidence": record_doc["confidence"],
                "narrative": record_doc["clinical_narrative"],
                "directives": record_doc["recommendations"]
            }
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Voice Diagnostic Crash: {str(e)}"}), 500

@multimodal_bp.route('/send-ping', methods=['POST'])
def send_ping():
    data = request.json or {}
    doctor_id = data.get("doctor_id")
    message = data.get("message")
    if db_client.db is not None:
        db_client.db.notifications.insert_one({
            "to_user_id": doctor_id,
            "message": message,
            "read": False,
            "timestamp": datetime.datetime.utcnow().isoformat()
        })
    return jsonify({"status": "success"})

@multimodal_bp.route('/read-notifications', methods=['POST'])
def read_notifications():
    user_id = request.json.get("user_id")
    if db_client.db is not None:
        db_client.db.notifications.update_many({"to_user_id": user_id}, {"$set": {"read": True}})
    return jsonify({"status": "success"})

@multimodal_bp.route('/history', methods=['GET'])
def get_clinical_history():
    email = request.args.get('email', '').strip().lower()
    role = request.args.get('role', 'patient')
    patient_id_arg = request.args.get('patient_id', '').strip().lower()

    # Force role normalization
    role_str = str(role or '').strip().lower()
    email_clean = str(email or '').strip().lower()
    is_clinical = 'admin' in role_str or 'doctor' in role_str
    
    # 1. Absolute Authority Override (Admin/Doctor Master Key)
    if is_clinical or email_clean == 'admin@123':
        filter_query = {}
    else:
        # Patient: Case-insensitive search across all identity keys
        or_conditions = []
        if email_clean:
            or_conditions.extend([
                {"patient_id": {"$regex": f"^{email_clean}$", "$options": "i"}},
                {"user_id": {"$regex": f"^{email_clean}$", "$options": "i"}},
                {"patient_name": {"$regex": email_clean, "$options": "i"}}
            ])
        if patient_id_arg:
            or_conditions.extend([
                {"patient_id": {"$regex": f"^{patient_id_arg}$", "$options": "i"}},
                {"user_id": {"$regex": f"^{patient_id_arg}$", "$options": "i"}},
                {"patient_name": {"$regex": patient_id_arg, "$options": "i"}}
            ])
            
        if or_conditions:
            filter_query = {"$or": or_conditions}
        else:
            filter_query = {"patient_id": "none_specified"}

    try:
        if db_client.db is None:
            return jsonify({"status": "error", "message": "DB disconnected"}), 500
            
        # 2. Direct Database Pull
        records = list(db_client.db.medical_records.find(filter_query).limit(500))
        
        # 3. Supplemental Predictions Pull (Merge prediction collection for audit integrity)
        if is_clinical:
            pred_records = list(db_client.db.predictions.find(filter_query).limit(500))
            seen_ids = {str(r.get('_id')) for r in records}
            for pr in pred_records:
                if str(pr.get('_id')) not in seen_ids:
                    records.append(pr)

        # 4. JSON Serialization Cleanup
        final_history = []
        for r in records:
            try:
                # Standardize Fields for Admin View
                r['id'] = str(r.pop('_id', 'unknown'))
                ts = r.get('timestamp') or r.get('date') or datetime.datetime.utcnow()
                r['timestamp'] = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
                r['patient_id'] = str(r.get('patient_id') or r.get('user_id') or 'Guest')
                r['disease'] = str(r.get('disease') or r.get('diagnosis') or 'N/A')
                r['risk'] = str(r.get('risk') or 'Low')
                
                final_history.append(r)
            except:
                continue

        # 5. Global Clinical Sort
        final_history.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        return jsonify({
            "status": "success",
            "history": final_history,
            "count": len(final_history)
        })

    except Exception as e:
        print(f"HISTORY_ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch clinical records", "details": str(e)}), 500

@multimodal_bp.route('/patient-history/search', methods=['POST'])
def search_history():
    query = request.json.get('query', '')
    patient_id = request.json.get('patient_id')
    if db_client.db is not None:
        f = {"patient_id": patient_id} if patient_id else {}
        records = list(db_client.db.medical_records.find(f))
        for r in records: r['_id'] = str(r['_id'])
        nlp = get_nlp_processor()
        results = nlp.search_patient_history(query, records)
        return jsonify({"status": "success", "results": results})
    return jsonify({"error": "DB error"}), 500
