from flask import Blueprint, request, jsonify
import os
import tempfile
import traceback
from werkzeug.utils import secure_filename
from services.audio_service import AudioService
from services.ocr_service import OCRService
from services.voice_intake_service import VoiceIntakeService
from nlp.processor_enhanced import NLPProcessorEnhanced
from utils.db import db_client

multimodal_bp = Blueprint('multimodal', __name__)

audio_service = AudioService()
ocr_service = OCRService()
nlp_processor = NLPProcessorEnhanced()
voice_intake = VoiceIntakeService()

# --- AUDIO ENDPOINT ---
@multimodal_bp.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save to temp file
        ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else 'webm'
        fd, temp_path = tempfile.mkstemp(suffix=f".{ext}")
        with os.fdopen(fd, 'wb') as f:
            audio_file.save(f)

        file_size = os.path.getsize(temp_path)
        print(f"[AUDIO] Received audio file: {audio_file.filename} ({file_size} bytes, ext={ext})")
        
        if file_size < 100:
            return jsonify({"error": "Audio file is empty or too small. Please record for longer."}), 400

        # Process audio to text (AudioService handles cleanup)
        result = audio_service.process_audio(temp_path)

        if result['status'] == 'error':
            return jsonify({"error": result.get('error', 'Audio processing failed')}), 500

        text = result['text']
        
        # Analyze using NLP
        nlp_data = nlp_processor.process_prescription(text)
        
        return jsonify({
            "status": "success",
            "transcription": text,
            "extracted_data": nlp_data
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- OCR ENDPOINT ---
@multimodal_bp.route('/upload-prescription', methods=['POST'])
def upload_prescription():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    img_file = request.files['image']
    if img_file.filename == '':
        return jsonify({"error": "Empty filename"}), 400

    try:
        # Save to temp
        fd, temp_path = tempfile.mkstemp(suffix=".png")
        with os.fdopen(fd, 'wb') as f:
            img_file.save(f)

        # Process OCR
        ocr_result = ocr_service.extract_text(temp_path)
        
        # Cleanup
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass

        if ocr_result['status'] == 'error':
            return jsonify({"error": ocr_result.get('error', 'OCR failed')}), 500
            
        raw_text = ocr_result['text']
        
        # Analyze using NLP
        nlp_data = nlp_processor.process_prescription(raw_text)

        # Fuzzy match extracted drugs and get details using DrugIntelligenceService
        extracted_drugs = nlp_data.get("drugs", [])
        # Use context if available, else default to 'general'
        disease_context = nlp_data.get("context", "general")
        from services.drug_service import DrugIntelligenceService
        drug_service = DrugIntelligenceService()
        prescription_eval = drug_service.evaluate_prescription(extracted_drugs, disease_context)

        return jsonify({
            "status": "success",
            "raw_text": raw_text,
            "extracted_data": nlp_data,
            "prescription_evaluation": prescription_eval
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- HISTORY SEARCH ENDPOINT ---
@multimodal_bp.route('/patient-history/search', methods=['POST'])
def search_history():
    data = request.json
    if not data or 'query' not in data:
        return jsonify({"error": "Missing 'query' parameter"}), 400
        
    query = data['query']
    patient_id = data.get('patient_id') # Optional filter
    
    try:
        if db_client.db is None:
            return jsonify({"error": "Database not connected"}), 500
            
        # Fetch records
        search_filter = {}
        if patient_id:
            search_filter['patient_id'] = patient_id
            
        records_cursor = db_client.db.medical_records.find(search_filter)
        records = list(records_cursor)
        
        # Serialize ObjectIds for safety
        for r in records:
            r['_id'] = str(r['_id'])
            
        # Semantic search
        results = nlp_processor.search_patient_history(query, records)
        
        return jsonify({
            "status": "success",
            "results": results
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ═══ VOICE DIAGNOSIS ENDPOINT ═══
# Full pipeline: Audio -> Wav2Vec2 STT -> NLP parameter extraction -> ML prediction -> Auto-medication
@multimodal_bp.route('/voice-diagnosis', methods=['POST'])
def voice_diagnosis():
    """
    Unified voice-to-diagnosis pipeline:
    1. Accept audio file + disease type
    2. Transcribe via Wav2Vec2 deep learning STT
    3. Extract medical parameters via NLP regex/keyword matching
    4. Impute missing values with medical defaults
    5. Run ensemble ML prediction
    6. Auto-suggest medications if no prescription detected
    """
    disease = request.form.get('disease', 'diabetes')
    
    # Accept either audio upload or raw text
    transcription = ""
    stt_model = "text_input"
    
    if 'audio' in request.files:
        audio_file = request.files['audio']
        if audio_file.filename != '':
            try:
                ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else 'wav'
                fd, temp_path = tempfile.mkstemp(suffix=f".{ext}")
                with os.fdopen(fd, 'wb') as f:
                    audio_file.save(f)
                
                stt_result = audio_service.process_audio(temp_path)
                if stt_result['status'] == 'success':
                    transcription = stt_result['text']
                    stt_model = stt_result.get('model', 'wav2vec2')
                else:
                    return jsonify({"error": "Speech recognition failed: " + stt_result.get('error', 'Unknown')}), 500
            except Exception as e:
                traceback.print_exc()
                return jsonify({"error": f"Audio processing failed: {str(e)}"}), 500
    
    # Also accept text directly (for testing or text-mode voice)
    if not transcription:
        transcription = request.form.get('text', '')
    
    if not transcription.strip():
        return jsonify({"error": "No audio or text input provided."}), 400
    
    try:
        # Step 1: Extract parameters from transcription
        extraction = voice_intake.extract_parameters(transcription, disease)
        features = extraction["features"]
        extracted = extraction["extracted"]
        defaults_used = extraction["defaults_used"]
        
        # Step 2: Check for prescription content in the transcription
        nlp_data = nlp_processor.process_prescription(transcription)
        has_prescription = len(nlp_data.get("drugs", [])) > 0
        prescription_text = transcription if has_prescription else ""
        
        # Step 3: Run ML prediction
        from services.prediction_service import PredictionService
        from services.clinical_intelligence import ClinicalIntelligenceService
        
        # Use the global predictor from diagnosis_routes
        from api.routes.diagnosis_routes import predictor
        
        result = predictor.handle_prediction(features, prescription_text, disease_type=disease)
        
        # Step 4: Auto-suggest medications if no prescription detected
        auto_medications = []
        if not has_prescription:
            risk = result.get("risk", "Moderate")
            auto_medications = voice_intake.get_auto_medications(disease, risk)
        
        # Step 5: Build response
        response = {
            "status": "success",
            "stt_model": stt_model,
            "transcription": transcription,
            
            # Extraction details
            "extraction": {
                "parameters": extracted,
                "defaults_used": defaults_used,
                "extraction_confidence": extraction["extraction_confidence"],
                "features_array": features,
            },
            
            # Prediction results
            "prediction": {
                "risk": result["risk"],
                "confidence": result["confidence"],
                "disease": result["disease"],
                "explanation": result["explanation"],
            },
            
            # Clinical data
            "abnormalities": result.get("abnormalities", []),
            "recommendations": result.get("recommendations", {}),
            
            # Drug/Prescription data
            "prescription_detected": has_prescription,
            "auto_medications": auto_medications,
            "nlp_entities": {
                "drugs": nlp_data.get("drugs", []),
                "symptoms": nlp_data.get("symptoms", []),
            },
            
            # Original NLP data if prescription was given
            "matched_drugs": result.get("matched_drugs", []),
            "drug_interactions": result.get("drug_interactions", []),
            "suggestions": result.get("suggestions", []),
        }
        
        # Log to DB
        try:
            import datetime
            if db_client.db is not None:
                db_client.db.predictions.insert_one({
                    "patient_id": request.form.get("patient_id", "voice_user"),
                    "disease": disease,
                    "risk": result["risk"],
                    "confidence": result["confidence"],
                    "input_method": "voice",
                    "stt_model": stt_model,
                    "timestamp": datetime.datetime.utcnow()
                })
        except Exception:
            pass
        
        return jsonify(response)
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Diagnosis pipeline failed: {str(e)}"}), 500
