import requests
import os
import json
from dotenv import load_dotenv

# Path to the .env file
env_path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\.env"
load_dotenv(env_path)

def test_api():
    providers = [
        {"name": "Groq", "env_key": "GROQ_API_KEY", "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama-3.1-70b-versatile"},
        {"name": "OpenRouter", "env_key": "OPENROUTER_API_KEY", "url": "https://openrouter.ai/api/v1/chat/completions", "model": "openai/gpt-4o-mini"},
        {"name": "OpenAI", "env_key": "OPENAI_API_KEY", "url": "https://api.openai.com/v1/chat/completions", "model": "gpt-4o-mini"}
    ]

    print("--- STARTING AI DIAGNOSTIC ---")
    print(f"Working Directory: {os.getcwd()}")
    
    for p in providers:
        key = os.getenv(p["env_key"], "").strip()
        print(f"\n[Testing {p['name']}]")
        if not key:
            print(f"  FAILED: {p['env_key']} is not set in environment or .env file.")
            continue
        
        print(f"  Key found (Starts with: {key[:8]}...)")
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
            "User-Agent": "Healthcare-AI-Diagnostic/1.0"
        }
        
        payload = {
            "model": p["model"],
            "messages": [{"role": "user", "content": "Hello. Response in 1 word."}],
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
            print(f"  NETWORK/REQUEST ERROR: {str(e)}")

if __name__ == "__main__":
    test_api()
