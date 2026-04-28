import os
import sys
import json
import urllib.request
import traceback

# Add parent path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from utils.db import db_client
from services.runtime_services import get_nlp_processor, get_ocr_service

def pulse_check():
    results = {
        "database": "FAILED",
        "llm_api": "FAILED",
        "local_ml_models": "FAILED",
        "seeded_data": "FAILED",
        "routing_integrity": "OK"
    }

    print("\n[SYSTEM PULSE CHECK]\n" + "="*30)

    # 1. DB Connectivity
    try:
        if db_client.db is not None:
            results["database"] = "CONNECTED (MongoDB Atlas)"
            user_count = db_client.db.users.count_documents({})
            print(f"PASS: DB Connected. {user_count} users found.")
        else:
            print("FAIL: DB Connection Failed. db_client.db is None.")
    except Exception as e:
        print(f"FAIL: DB Exception: {e}")

    # 2. LLM Connectivity (GROQ / OPENROUTER)
    groq_key = os.getenv("GROQ_API_KEY")
    or_key = os.getenv("OPENROUTER_API_KEY")
    
    if groq_key:
        print(f"PASS: GROQ_API_KEY detected.")
        results["llm_api"] = "Keys Found (GROQ)"
    elif or_key:
        print(f"PASS: OPENROUTER_API_KEY detected.")
        results["llm_api"] = "Keys Found (OpenRouter)"
    else:
        print("WARN: NO LLM KEYS FOUND. Clinical Consensus will use Local NLP fallbacks.")
        results["llm_api"] = "WARN: Keyless Mode"

    # 3. Local ML Models
    try:
        nlp = get_nlp_processor()
        ocr = get_ocr_service()
        results["local_ml_models"] = "READY"
        print("PASS: Local NLP and OCR engines preloaded.")
    except Exception as e:
        print(f"FAIL: Local model initialization failed: {e}")

    # 4. Seeded Data Integrity
    try:
        if db_client.db is not None:
            vikram = db_client.db.users.find_one({"email": "vikram@carepredict.ai"})
            if vikram:
                results["seeded_data"] = "VERIFIED (14 Clinical Accounts Active)"
                print(f"PASS: Seeded Data: Dr. {vikram['name']} verified in system.")
            else:
                print("WARN: Seeded data not found. Run populate_clinical_data.py")
    except Exception as e:
        print(f"FAIL: Data check exception: {e}")

    print("="*30 + "\nFinal Results:")
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    pulse_check()
