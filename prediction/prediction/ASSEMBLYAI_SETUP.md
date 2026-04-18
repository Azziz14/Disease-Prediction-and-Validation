# AssemblyAI Setup Guide

Your voice input system has been upgraded from **Wav2Vec2** (slow local model loading) to **AssemblyAI** (fast cloud-based transcription).

## Benefits

✅ **No model loading delays** - API-based, instant availability
✅ **Better accuracy** - Specialized for medical terminology
✅ **Cloud-powered** - Scales automatically
✅ **Fallback support** - Automatically uses Google STT if API key is missing

## Setup Instructions

### 1. Get AssemblyAI API Key

1. Go to [AssemblyAI Dashboard](https://www.assemblyai.com/)
2. Sign up for a free account (or use existing)
3. Copy your **API Key** from the dashboard

### 2. Set Environment Variable

#### **Option A: Windows PowerShell** (Recommended)
```powershell
# Set for current session only
$env:ASSEMBLYAI_API_KEY = "your_api_key_here"

# To make it permanent, use:
[Environment]::SetEnvironmentVariable("ASSEMBLYAI_API_KEY", "your_api_key_here", "User")
```

#### **Option B: Create `.env` file**
Create a `.env` file in the backend folder:
```
ASSEMBLYAI_API_KEY=your_api_key_here
```

Then load it in your Flask app:
```python
from dotenv import load_dotenv
load_dotenv()
```

#### **Option C: Windows Environment Variables GUI**
1. Press `Win + X` → Environment Variables
2. Click "Edit the system environment variables"
3. Click "Environment Variables..."
4. Add new User/System variable: `ASSEMBLYAI_API_KEY = your_api_key_here`
5. Restart your terminal/app

### 3. Install Dependencies

```powershell
pip install assemblyai requests
# Or update all requirements:
pip install -r requirements.txt
```

### 4. Test the Setup

```python
from config import Config
from services.audio_service import AudioService

# Check if API key is loaded
print(f"API Key configured: {bool(Config.ASSEMBLYAI_API_KEY)}")

# Initialize service
audio_service = AudioService()
print(f"Using fallback STT: {audio_service.use_fallback}")
```

## API Pricing

AssemblyAI offers:
- **Free tier**: $0/month with limited requests
- **Pay-as-you-go**: $0.01 per minute of audio (after free credits)
- Medical transcription model available in all tiers

## Troubleshooting

### "No API key found, using fallback STT"
- Ensure environment variable `ASSEMBLYAI_API_KEY` is set correctly
- Restart your terminal/Python process after setting the variable
- Check that the value is pasted exactly without extra spaces

### "Transcription timeout"
- AssemblyAI can take 20-30% of audio duration to process
- The system automatically retries with progressive backoff
- Check your internet connection

### "Upload failed"
- Verify your API key is valid
- Ensure you have AssemblyAI credits remaining
- Check that the audio file is not corrupted

### Fallback to Google STT
- System automatically uses Google's free STT if AssemblyAI fails or key is missing
- No additional setup needed
- Google STT is less accurate but always available

## How It Works

```
User records audio
       ↓
Audio converted to 16kHz WAV
       ↓
Upload to AssemblyAI
       ↓
System polls for transcription (with exponential backoff)
       ↓
Return transcribed text
       ↓
Voice Intake Service extracts medical parameters
       ↓
ML prediction + auto-medication suggestions
```

## API Response Example

```json
{
  "status": "success",
  "stt_model": "assemblyai",
  "transcription": "My glucose is 150 and blood pressure is 140 over 90",
  "extraction": {
    "parameters": {"glucose": 150, "bloodPressure": 140, ...},
    "extraction_confidence": 0.85
  },
  "prediction": {
    "risk": "High",
    "disease": "diabetes"
  },
  "auto_medications": [...]
}
```

## Migration Notes

- **Old system**: Wav2Vec2 (local, required 2GB+ download, slow startup)
- **New system**: AssemblyAI (cloud, instant, more accurate)
- **No code changes needed** - Works with existing endpoints:
  - `/upload-audio`
  - `/voice-diagnosis`

---

For more info: [AssemblyAI Docs](https://www.assemblyai.com/docs)
