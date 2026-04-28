"""
/predict API Route — Low-Latency, Async, Modular
Handles text/audio input (Hindi/English), fast STT, translation, language detection, and ML prediction.
"""

from flask import Blueprint, request, jsonify
from concurrent.futures import ThreadPoolExecutor
import asyncio
import functools
from services.audio_service import AudioService
from services.prediction_runtime import get_prediction_service
from utils.translation import (
    detect_language_fast as detect_language_fast_sync,
    translate_fast as translate_fast_sync,
)
from utils.cache import lru_cache_async

predict_bp = Blueprint('predict', __name__)

AUDIO_SERVICE = AudioService()

# Thread pool for blocking I/O (speech-to-text, translation)
EXECUTOR = ThreadPoolExecutor(max_workers=4)

# Async wrapper for sync functions
def run_in_executor(func, *args, **kwargs):
    loop = asyncio.get_running_loop()
    return loop.run_in_executor(EXECUTOR, functools.partial(func, *args, **kwargs))

# --- Modular Fast Functions ---
async def speech_to_text_fast(audio_path):
    # Limit audio length before processing (10-15s)
    # Use lightweight/streaming model if available
    return await run_in_executor(AUDIO_SERVICE.process_audio, audio_path)

@lru_cache_async(maxsize=128)
async def translate_text_fast(text, src_lang, tgt_lang="en"):
    # Use local/optimized model or fast API
    return await run_in_executor(translate_fast_sync, text, src_lang, tgt_lang)

@lru_cache_async(maxsize=128)
async def detect_text_language_fast(text):
    return await run_in_executor(detect_language_fast_sync, text)

async def preprocess_fast(text):
    # Lightweight tokenizer/keyword match, fallback to BERT if needed
    prediction_service = get_prediction_service()
    return await run_in_executor(prediction_service.nlp.process, text)

async def predict_fast(features, prescription, disease_type="diabetes", user_id=None, patient_id=None, patient_name=None, treating_doctor_id=None):
    # Enforce priority for explicitly passed identities
    resolved_user_id = user_id or treating_doctor_id
    prediction_service = get_prediction_service()
    return await run_in_executor(prediction_service.handle_prediction, features, prescription, disease_type, resolved_user_id, patient_id, patient_name, treating_doctor_id)

# --- /predict Endpoint ---
@predict_bp.route('/predict', methods=['POST'])
def predict():
    # Use asyncio event loop for async processing
    data = request.form or request.json or {}
    audio_file = request.files.get('audio')
    text_input = data.get('text', "")
    
    # Identify context early
    user_id = request.headers.get('X-User-Id') or data.get('user_id')
    patient_id = data.get('patient_id')
    patient_name = data.get('patient_name')
    treating_doctor_id = data.get('treating_doctor_id')
    
    response = {}

    async def process(current_text_input):
        temp_text = current_text_input
        # 1. Handle audio input (if present)
        if audio_file:
            # Save audio to temp file
            import tempfile, os
            ext = audio_file.filename.rsplit('.', 1)[-1].lower() if '.' in audio_file.filename else 'wav'
            fd, temp_path = tempfile.mkstemp(suffix=f".{ext}")
            with os.fdopen(fd, 'wb') as f:
                audio_file.save(f)
            stt_result = await speech_to_text_fast(temp_path)
            os.remove(temp_path)
            if stt_result.get('status') != 'success':
                return {"error": "Speech-to-text failed", **stt_result}
            temp_text = stt_result['text']
            response['transcription'] = temp_text

        # 2. Language detection
        lang = await detect_text_language_fast(temp_text)
        response['detected_language'] = lang

        # 3. Translation (Hindi → English)
        if lang != 'en':
            translated = await translate_text_fast(temp_text, lang, 'en')
            response['translated'] = translated
            temp_text = translated

        # 4. Preprocess (tokenizer/keyword/BERT fallback)
        preprocessed = await preprocess_fast(temp_text)
        response['preprocessed'] = preprocessed

        # 5. Model prediction (no retraining, no disk I/O)
        features = preprocessed.get('features', [])
        prescription = preprocessed.get('prescription', {})
        prediction = await predict_fast(
            features, 
            prescription, 
            data.get('disease', 'diabetes'), 
            user_id, 
            patient_id, 
            patient_name, 
            treating_doctor_id
        )
        response['prediction'] = prediction
        return response

    # Run async process in event loop
    # Run async process in event loop
    result = asyncio.run(process(text_input))
    return jsonify(result)
