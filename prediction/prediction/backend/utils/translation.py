"""
High-Fidelity AI Localization Utility
Replaces basic machine translation with LLM-based Transcreation (Hinglish/Native Hindi).
"""
import os
import requests
import json
import logging

try:
    from langdetect import detect as _detect
except ImportError:
    _detect = None

logger = logging.getLogger(__name__)

class AITranslator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY") or os.getenv("OPENROUTER_API_KEY")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions" if os.getenv("GROQ_API_KEY") else "https://openrouter.ai/api/v1/chat/completions"
        self.model = "llama-3.1-8b-instant" if "groq" in self.api_url else "google/gemini-flash-1.5"

    def translate(self, text, src_lang, tgt_lang="en"):
        if not text or src_lang == tgt_lang:
            return text
            
        if not self.api_key:
            return text

        # Use LLM for High-Fidelity Localization (Transcreation)
        prompt = (
            f"You are a professional medical translator. Translate the following text from {src_lang} to {tgt_lang}.\n"
            f"RULE 1: If translating to Hindi, use high-quality 'Hinglish' (Hindi grammar with English clinical terms like 'Blood Pressure', 'Diabetes', 'Scan').\n"
            f"RULE 2: Maintain a professional, empathetic clinical tone. Use 'Aap' (honorific).\n"
            f"RULE 3: Return ONLY the translated text. No explanations.\n\n"
            f"TEXT: {text}"
        )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f"[TranslationAI] LLM Translation failed: {e}")
            
        return text

# Global singleton
_ai_translator = AITranslator()

def detect_language_fast(text):
    if not text or _detect is None:
        return 'en'
    try:
        # Simple local detection is fast and 99% accurate for hi/en
        return _detect(text)
    except Exception:
        return 'en'

def translate_fast(text, src_lang, tgt_lang="en"):
    """
    Upgraded: Uses AI-driven transcreation for interactive, clinical-grade Hindi/Hinglish.
    """
    return _ai_translator.translate(text, src_lang, tgt_lang)
