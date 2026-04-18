import os

class Config:
    DEBUG = True
    
    # AssemblyAI API Configuration
    ASSEMBLYAI_API_KEY = "0fcfb5654ebe46f682ecd84c362fcc04"
    
    # Fallback to SpeechRecognition if AssemblyAI API key is not set
    USE_FALLBACK_STT = not bool(ASSEMBLYAI_API_KEY)