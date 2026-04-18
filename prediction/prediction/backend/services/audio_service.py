"""
AssemblyAI Speech-to-Text Service
Uses AssemblyAI API for fast, accurate audio transcription.
Specialized for medical terminology and professional use.
Cloud-based - no local model loading required.
"""

import os
import logging
import tempfile
import requests
from config import Config

logger = logging.getLogger(__name__)

ASSEMBLYAI_API_URL = "https://api.assemblyai.com/v2"


def _convert_to_wav(file_path: str) -> str:
    """
    Convert any audio format (webm, ogg, mp3, etc.) to WAV format.
    Returns the path (may be same if already compatible).
    """
    try:
        from pydub import AudioSegment

        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else 'webm'
        
        audio = None
        formats_to_try = [ext]
        if ext not in ['webm', 'ogg', 'mp4', 'wav', 'mp3']:
            formats_to_try.extend(['webm', 'ogg', 'mp4'])
        elif ext == 'wav':
            formats_to_try.extend(['webm', 'ogg'])
        
        for fmt in formats_to_try:
            try:
                audio = AudioSegment.from_file(file_path, format=fmt)
                logger.info(f"Successfully loaded audio as {fmt}")
                break
            except Exception as e:
                logger.debug(f"Failed to load as {fmt}: {e}")
                continue
        
        if audio is None:
            try:
                audio = AudioSegment.from_file(file_path)
                logger.info("Loaded audio with auto-detection")
            except Exception as e:
                logger.error(f"All audio format attempts failed: {e}")
                return file_path
        
        # Convert to 16kHz mono WAV
        audio = audio.set_frame_rate(16000).set_channels(1)
        
        wav_path = file_path.rsplit('.', 1)[0] + '_converted.wav'
        audio.export(wav_path, format="wav")
        logger.info(f"Converted to WAV: {wav_path} (duration: {len(audio)/1000:.1f}s)")
        
        return wav_path
        
    except ImportError:
        logger.warning("pydub not installed, skipping conversion")
        return file_path
    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        return file_path


class AudioService:
    """
    Cloud-based Speech-to-Text using AssemblyAI.
    Fast, accurate transcription with medical terminology support.
    """

    def __init__(self):
        self.api_key = Config.ASSEMBLYAI_API_KEY
        self.use_fallback = Config.USE_FALLBACK_STT
        
        if not self.use_fallback:
            logger.info("AssemblyAI service initialized")
        else:
            logger.warning("No AssemblyAI API key found. Will use fallback STT.")

    def process_audio(self, file_path: str) -> dict:
        """
        Transcribe audio using AssemblyAI API.
        
        Pipeline:
        1. Convert audio to compatible WAV format
        2. Upload to AssemblyAI
        3. Poll for transcription (typically 20-30% of audio duration)
        4. Return transcribed text
        
        Args:
            file_path: Path to audio file (.wav, .mp3, .webm, etc.)
            
        Returns:
            dict with keys: text, status, model, duration_seconds
        """
        wav_path = None
        
        try:
            # Convert any format to WAV
            wav_path = _convert_to_wav(file_path)
            
            if self.use_fallback:
                return self._fallback_process(wav_path)
            
            # Upload file to AssemblyAI
            with open(wav_path, 'rb') as f:
                upload_response = requests.post(
                    f"{ASSEMBLYAI_API_URL}/upload",
                    headers={"Authorization": self.api_key},
                    files={"file": f}
                )
            
            if upload_response.status_code != 200:
                logger.error(f"Upload failed: {upload_response.text}")
                return self._fallback_process(wav_path)
            
            audio_url = upload_response.json()['upload_url']
            logger.info(f"Audio uploaded successfully: {audio_url}")
            
            # Submit for transcription
            transcription_request = {
                "audio_url": audio_url,
                "language_code": "en",
                "speech_model": "best"  # Most accurate model
            }
            
            submit_response = requests.post(
                f"{ASSEMBLYAI_API_URL}/transcript",
                json=transcription_request,
                headers={"Authorization": self.api_key}
            )
            
            if submit_response.status_code != 200:
                logger.error(f"Transcription submit failed: {submit_response.text}")
                return self._fallback_process(wav_path)
            
            transcript_id = submit_response.json()['id']
            logger.info(f"Transcription job submitted: {transcript_id}")
            
            # Poll for completion
            transcription = self._poll_transcription(transcript_id)
            
            if transcription is None:
                return self._fallback_process(wav_path)
            
            # Get audio duration
            duration_seconds = submit_response.json().get('audio_duration', 0)
            
            logger.info(f"AssemblyAI transcription: {transcription[:100]}...")
            print(f"[STT] Transcription: {transcription[:200]}")
            
            return {
                "text": transcription,
                "status": "success",
                "model": "assemblyai",
                "duration_seconds": duration_seconds
            }
        
        except Exception as e:
            logger.error(f"Error processing audio: {e}")
            try:
                fallback = self._fallback_process(wav_path or file_path)
                if fallback.get("status") == "success":
                    return fallback
            except Exception:
                pass
            return {"text": "", "status": "error", "error": f"Speech recognition failed: {str(e)}"}
        
        finally:
            # Clean up temp files
            for path in [file_path, wav_path]:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

    def _poll_transcription(self, transcript_id: str, max_attempts: int = 120) -> str:
        """
        Poll AssemblyAI for transcription completion.
        """
        import time
        
        for attempt in range(max_attempts):
            response = requests.get(
                f"{ASSEMBLYAI_API_URL}/transcript/{transcript_id}",
                headers={"Authorization": self.api_key}
            )
            
            if response.status_code != 200:
                logger.error(f"Poll failed: {response.text}")
                return None
            
            result = response.json()
            status = result['status']
            
            if status == 'completed':
                text = result['text']
                logger.info(f"Transcription completed in {attempt + 1} attempts")
                return text if text else "Could not transcribe audio clearly."
            
            elif status == 'error':
                error_msg = result.get('error', 'Unknown error')
                logger.error(f"Transcription error: {error_msg}")
                return None
            
            # Still processing, wait and retry
            wait_time = min(2 + attempt // 10, 10)  # Progressive backoff
            logger.debug(f"Attempt {attempt + 1}/{max_attempts}: Status={status}, waiting {wait_time}s...")
            time.sleep(wait_time)
        
        logger.error(f"Transcription timeout after {max_attempts} attempts")
        return None

    def _fallback_process(self, file_path: str) -> dict:
        """
        Fallback to local SpeechRecognition if AssemblyAI is unavailable.
        Uses Google's free Speech Recognition API.
        """
        try:
            import speech_recognition as sr
            from pydub import AudioSegment

            if not file_path.endswith('.wav'):
                audio = AudioSegment.from_file(file_path)
                wav_path = file_path.rsplit('.', 1)[0] + '_fallback.wav'
                audio = audio.set_frame_rate(16000).set_channels(1)
                audio.export(wav_path, format="wav")
            else:
                wav_path = file_path

            recognizer = sr.Recognizer()
            with sr.AudioFile(wav_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.record(source)
                text = recognizer.recognize_google(audio_data)
                
                logger.info(f"Fallback STT transcription: {text[:100]}")
                print(f"[STT FALLBACK] Transcription: {text[:200]}")
                
                return {"text": text, "status": "success", "model": "google_stt_fallback"}

        except Exception as e:
            logger.error(f"Fallback STT failed: {e}")
            return {
                "text": "",
                "status": "error",
                "error": f"All STT methods failed: {str(e)}"
            }

