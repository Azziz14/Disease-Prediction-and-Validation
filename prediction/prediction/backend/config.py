import os
from pathlib import Path


def _load_env_file() -> None:
    """Load key=value pairs from the project-level .env if present."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ[key] = value


_load_env_file()


class Config:
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"

    MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
    MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "DiseasePredictionValidation")

    # AssemblyAI API Configuration
    ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY", "").strip()
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

    # Fallback to SpeechRecognition if AssemblyAI API key is not set
    USE_FALLBACK_STT = not bool(ASSEMBLYAI_API_KEY)
