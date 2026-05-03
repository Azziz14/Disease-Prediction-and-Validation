import os
import requests
from pymongo import MongoClient
from pathlib import Path

def load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        print(f"Error: .env file not found at {env_path}")
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip().strip('"').strip("'")

def test_mongodb():
    uri = os.getenv("MONGODB_URI")
    db_name = os.getenv("MONGODB_DB_NAME")
    print(f"\n--- Testing MongoDB ---")
    if not uri:
        print("MONGODB_URI not found")
        return False
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
        return False

def test_openai():
    api_key = os.getenv("OPENAI_API_KEY")
    print(f"\n--- Testing OpenAI API ---")
    if not api_key:
        print("OPENAI_API_KEY not found")
        return False
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        # Trying a newer model just in case, but quota error is likely account-wide
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 5
            }
        )
        if response.status_code == 200:
            print("OpenAI API call successful!")
            return True
        else:
            print(f"OpenAI API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"OpenAI API test error: {e}")
        return False

def test_assemblyai():
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    print(f"\n--- Testing AssemblyAI API ---")
    if not api_key:
        print("ASSEMBLYAI_API_KEY not found")
        return False
    try:
        headers = {"Authorization": api_key}
        response = requests.get("https://api.assemblyai.com/v2/account", headers=headers)
        if response.status_code == 200:
            print("AssemblyAI API call successful!")
            return True
        else:
            print(f"AssemblyAI API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"AssemblyAI API test error: {e}")
        return False

def test_openrouter():
    api_key = os.getenv("OPENROUTER_API_KEY")
    print(f"\n--- Testing OpenRouter API ---")
    if not api_key:
        print("OPENROUTER_API_KEY not found")
        return False
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "API Key Test"
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "google/gemini-2.0-flash-001",
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 5
            }
        )
        if response.status_code == 200:
            print("OpenRouter API call successful!")
            return True
        else:
            print(f"OpenRouter API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"OpenRouter API test error: {e}")
        return False

def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    print(f"\n--- Testing Groq API ---")
    if not api_key:
        print("GROQ_API_KEY not found")
        return False
    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 5
            }
        )
        if response.status_code == 200:
            print("Groq API call successful!")
            return True
        else:
            print(f"Groq API call failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Groq API test error: {e}")
        return False

if __name__ == "__main__":
    load_env()
    test_mongodb()
    test_openai()
    test_assemblyai()
    test_openrouter()
    test_groq()
