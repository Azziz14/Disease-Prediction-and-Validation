import requests
import os
import json
from dotenv import load_dotenv

# Path to the .env file - ABSOLUTE PATH to be safe
env_path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\.env"
load_dotenv(env_path)

def test_api():
    # Use EXACT models as in the app
    providers = [
        {"name": "Groq", "env_key": "GROQ_API_KEY", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.3-70b-versatile"},
        {"name": "OpenRouter", "env_key": "OPENROUTER_API_KEY", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openai/gpt-4o-mini"},
        {"name": "OpenAI", "env_key": "OPENAI_API_KEY", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"}
    ]

    print("--- STARTING UPDATED AI DIAGNOSTIC ---")
    print(f"Env Path used: {env_path}")
    print(f"Env Path Found? {os.path.exists(env_path)}")
    
    for p in providers:
        key = os.getenv(p["env_key"], "").strip()
        print(f"\n[Testing {p['name']}]")
        if not key:
            print(f"  FAILED: {p['env_key']} NOT FOUND.")
            continue
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "Healthcare-Diagnostic/1.0"
        }
        if p['name'] == 'OpenRouter':
            headers["HTTP-Referer"] = "http://localhost:3000"
            headers["X-Title"] = "Diagnostic Test"

        payload = {
            "model": p["model"],
            "messages": [{"role": "user", "content": "Ping"}],
            "max_tokens": 5
        }
        
        try:
            response = requests.post(p["url"], headers=headers, json=payload, timeout=15)
            print(f"  Status Code: {response.status_code}")
            if response.status_code == 200:
                print(f"  SUCCESS: {response.json()['choices'][0]['message']['content']}")
            else:
                print(f"  API ERROR: {response.text}")
        except Exception as e:
            print(f"  NETWORK ERROR: {str(e)}")

if __name__ == "__main__":
    test_api()
