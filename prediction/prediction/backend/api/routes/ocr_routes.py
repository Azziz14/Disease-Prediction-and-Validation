import os
import json
import base64
import urllib.error
import urllib.request
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import traceback

ocr_bp = Blueprint('ocr', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_api_credentials():
    return {
        "groq": os.getenv("GROQ_API_KEY", "").strip(),
        "openrouter": os.getenv("OPENROUTER_API_KEY", "").strip(),
        "openai": os.getenv("OPENAI_API_KEY", "").strip()
    }

@ocr_bp.route('/upload-prescription', methods=['POST'])
def upload_prescription():
    """Upload and analyze prescription image using Multimodal Vision (Groq -> OpenRouter -> OpenAI)."""
    import requests
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "File type not allowed."}), 400
        
        creds = get_api_credentials()
        image_bytes = file.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = """
        Analyze this prescription image. Extract the patient name, doctor name, and date.
        Most importantly, list all medications, dosages, frequencies, and instructions.
        Crucially: Correct any misspelled medicine names to their proper pharmaceutical spelling.
        
        Return ONLY valid JSON exactly in this format, and no other text or formatting blocks:
        {
            "patient_name": "String",
            "doctor_name": "String",
            "date": "String",
            "drugs": ["Medication 1", "Medication 2"],
            "medications": ["Medication 1", "Medication 2"],
            "dosage": ["Dosage 1", "Dosage 2"],
            "frequency": ["Frequency 1", "Frequency 2"],
            "instructions": ["Instruction 1", "Instruction 2"]
        }
        """

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]

        providers = [
            {"name": "groq", "key": creds["groq"], "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.2-11b-vision-preview"},
            {"name": "openrouter", "key": creds["openrouter"], "url": "https://openrouter.ai/api/v1/chat/completions", "model": "google/gemini-2.0-flash-001"},
            {"name": "openai", "key": creds["openai"], "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"}
        ]

        for p in providers:
            if not p["key"]: continue
            try:
                print(f"[OCR] Attempting vision analysis via {p['name']}...")
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {p['key']}"
                }
                if p["name"] == "openrouter":
                    headers["HTTP-Referer"] = "http://localhost:3000"
                    headers["X-Title"] = "Healthcare AI Platform"

                payload = {
                    "model": p["model"],
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.2
                }
                
                response = requests.post(p["url"], headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"].strip()
                    if content.startswith("```json"):
                        content = content.replace("```json", "").replace("```", "").strip()
                    
                    extracted_data = json.loads(content)
                    extracted_data["filename"] = secure_filename(file.filename)
                    extracted_data["processed_at"] = datetime.utcnow().isoformat()
                    extracted_data["provider"] = p["name"]
                    
                    print(f"[OCR] SUCCESS via {p['name']}")
                    return jsonify({
                        "status": "success",
                        "data": extracted_data,
                        "extracted_data": extracted_data
                    })
                else:
                    print(f"[OCR] {p['name']} API Error: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[OCR] {p['name']} call failed: {e}")

        return jsonify({"error": "All Vision AI providers failed or were not configured."}), 503
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Vision processing failed: {str(e)}"}), 500
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Vision processing failed: {str(e)}"}), 500

@ocr_bp.route('/validate-medications', methods=['POST'])
def validate_medications():
    """Dynamically correct typos and validate medications using OpenAI."""
    try:
        data = request.get_json()
        medications = data.get('medications', [])
        
        if not medications:
            return jsonify({"error": "No medications provided"}), 400
            
        api_key = get_openai_client()
        if not api_key:
            return jsonify({"error": "OpenAI API key not configured"}), 503

        prompt = f"""
        You are a pharmaceutical validator. I will give you a list of medications that may contain typos.
        Correct their spellings to the official pharmacological name. Ensure they are actual drugs.
        If it's correctly spelled, leave it as is.

        Original List: {', '.join(medications)}

        Respond ONLY in valid JSON matching this format:
        [
            {{
                "name": "Original Name",
                "is_valid": true_if_real_drug,
                "suggestions": ["Corrected Name"],
                "category": "common"
            }}
        ]
        """

        req_body = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
            "temperature": 0.1
        }
        
        api_url = "https://api.openai.com/v1/chat/completions"
        if api_key.startswith("sk-or-v1"):
            api_url = "https://openrouter.ai/api/v1/chat/completions"

        req = urllib.request.Request(
            api_url,
            data=json.dumps(req_body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            method="POST",
        )
        
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            
        content = body.get("choices", [])[0].get("message", {}).get("content", "").strip()
        if content.startswith("```json"):
            content = content[7:-3]
            
        validated_medications = json.loads(content)
        
        return jsonify({
            "status": "success",
            "data": {
                "validated_medications": validated_medications,
                "total_medications": len(medications),
                "valid_count": len([m for m in validated_medications if m.get("is_valid")])
            }
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Medication validation failed: {str(e)}"}), 500
