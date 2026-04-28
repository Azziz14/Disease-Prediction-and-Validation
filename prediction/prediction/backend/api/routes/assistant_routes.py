import json
import os
import requests
import traceback
import logging
from flask import Blueprint, jsonify, request
from dotenv import load_dotenv

# Hard-coded absolute path for reliability on Windows
env_path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\.env"
load_dotenv(env_path)

assistant_bp = Blueprint("assistant", __name__)
logger = logging.getLogger(__name__)

def _sanitize_history(predictions: list) -> list:
    """Strip bulky fields like base64 images from history records before sending to LLM."""
    sanitized = []
    for p in predictions[:5]: # Take only the last 5
        clean_p = {
            "date": p.get("timestamp", ""),
            "disease": p.get("disease", "Unknown"),
            "risk": p.get("risk", "N/A"),
            "confidence": f"{float(p.get('confidence', 0))*100:.1f}%",
            "medications": p.get("auto_medications", p.get("autoMedications", [])),
            "diagnosis": p.get("consensus_diagnosis", p.get("diagnosis", ""))
        }
        sanitized.append(clean_p)
    return sanitized

def _build_prompt(payload: dict) -> str:
    question = (payload.get("question") or "").strip()
    patient_name = payload.get("patientName") or "Patient"
    selected_log = payload.get("selectedLog") or {}
    predictions = payload.get("predictions") or []

    # Aggressively sanitize history and log to remove base64 images
    sanitized_history = _sanitize_history(predictions)
    sanitized_log = _sanitize_history([selected_log])[0] if selected_log else None

    history_str = json.dumps(sanitized_history, ensure_ascii=False)
    log_str = json.dumps(sanitized_log, ensure_ascii=False) if sanitized_log else 'None'

    return (
        "You are an authoritative, clinical medical voice assistant. Your goal is to provide high-impact medical value with social awareness.\n"
        "1. SALUTATIONS: If the user is just greeting you (e.g., 'Hello', 'How are you'), respond with a professional, friendly greeting.\n"
        "2. CLINICAL TONE: For medical questions (e.g., symptoms, medication side effects, diagnostics), use 'CLINICAL DIRECTIVE'. Be punchy and direct.\n"
        "3. LIFESTYLE & DIET: For general questions about food (e.g., 'Can I eat mumus/momos'), diet, or exercise, provide balanced, evidence-based nutrition advice. DO NOT use 'CLINICAL DIRECTIVE' for food unless it is a known allergen or toxic. Be helpful and realistic.\n"
        "4. MEDICATION INTELLIGENCE: Explain exactly WHAT a drug is for and WHY it is used (e.g., 'Metformin: Used for Type 2 Diabetes').\n"
        "5. DATA-DRIVEN: Use history to justify your directives.\n"
        "6. CONCISE: Under 100 words. Zero fluff.\n\n"
        f"Patient: {patient_name}\n"
        f"Context Log: {log_str}\n"
        f"Recent History: {history_str}\n"
        f"User Asked: {question}"
    )

def _call_llm_api(api_key, model_name, messages, mode="openai"):
    api_url = "https://api.openai.com/v1/chat/completions"
    
    if mode == "openrouter":
        api_url = "https://openrouter.ai/api/v1/chat/completions"
        if not model_name.startswith("openai/") and not model_name.startswith("google/"):
            model_name = "openai/gpt-4o-mini"
    elif mode == "groq":
        api_url = "https://api.groq.com/openai/v1/chat/completions"
        model_name = "llama-3.3-70b-versatile" 

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "CarePredict-Assistant/1.1"
    }
    
    if mode == "openrouter":
        headers["HTTP-Referer"] = "http://localhost:3000"
        headers["X-Title"] = "CarePredict Assistant"

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.7
    }

    try:
        print(f"[LLM] Mode: {mode}, Key present: {bool(api_key)}, URL: {api_url}", flush=True)
        response = requests.post(api_url, headers=headers, json=payload, timeout=20)
        
        if response.status_code == 200:
            body = response.json()
            content = body.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            if content:
                return content
        else:
            print(f"[LLM ERROR] {mode} API returned {response.status_code}: {response.text}", flush=True)
    except Exception as e:
        print(f"[LLM CRITICAL] {mode} connectivity error:", flush=True)
        traceback.print_exc()
        
    return ""

@assistant_bp.route("/assistant-chat", methods=["POST"])
def assistant_chat():
    try:
        payload = request.get_json(silent=True) or {}
        question = (payload.get("question") or "").strip()[:2000] # Safe limit
        print(f"[ASSISTANT] Incoming: {question}", flush=True)
        
        # Reloading env inside the request just to BE ABSOLUTELY POSITIVE
        load_dotenv(env_path)
        
        groq_key = os.getenv("GROQ_API_KEY", "").strip()
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        openai_key = os.getenv("OPENAI_API_KEY", "").strip()

        print(f"[ASSISTANT] Keys -> Groq:{bool(groq_key)}, OR:{bool(openrouter_key)}, OpenAI:{bool(openai_key)}", flush=True)

        chat_messages = [
            {
                "role": "system", 
                "content": (
                    "You are a clinical-grade medical assistant. Be direct, authoritative, and professional.\n"
                    "INTERACTIVE MULTILINGUAL RULE: If asked in Hindi or about Hindi context, use high-fidelity 'Hinglish'.\n"
                    "Use 'Aap' (honorific). Maintain Hindi grammar but keep clinical terms (e.g., 'Blood Pressure', 'Sugar', 'Scan') in English for accuracy.\n"
                    "Be warm and empathetic. Encourage follow-up questions to stay interactive."
                )
            },
            {"role": "user", "content": _build_prompt(payload)}
        ]

        text = ""
        # 1. Groq
        if groq_key:
            text = _call_llm_api(groq_key, "llama-3.3-70b-versatile", chat_messages, mode="groq")
        
        # 2. OpenRouter
        if not text and openrouter_key:
            text = _call_llm_api(openrouter_key, "gpt-4o-mini", chat_messages, mode="openrouter")

        # 3. OpenAI
        if not text and openai_key:
            text = _call_llm_api(openai_key, "gpt-4o-mini", chat_messages, mode="openai")

        if not text:
            print("[ASSISTANT] FAILED TO GENERATE TEXT WITH ANY PROVIDER", flush=True)
            return jsonify({
                "text": "CAREPREDICT INTELLIGENCE: I am currently unable to reach my clinical consensus nodes. Please verify your internet connection or check the backend logs for API provider status.",
                "offline": True
            })

        return jsonify({"text": text})

    except Exception as exc:
        print(f"[ASSISTANT CRASH] Internal error:", flush=True)
        traceback.print_exc()
        return jsonify({"error": str(exc)}), 500
