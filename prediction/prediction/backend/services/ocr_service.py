import os
import logging

logger = logging.getLogger(__name__)

class OCRService:
    def __init__(self):
        # We init easyocr lazily so it doesn't block startup or throw torch warnings if unused
        self.reader = None

    def _init_reader(self):
        if self.reader is None:
            try:
                import easyocr
                # Initialize EasyOCR for English
                logger.info("Initializing EasyOCR Model...")
                self.reader = easyocr.Reader(['en'], gpu=True) # Will fallback to CPU if no GPU
            except ImportError:
                logger.error("EasyOCR library not found. Please install easyocr.")
                return False
        return True

    def extract_text(self, image_path):
        """
        Extract text from an image file using EasyOCR.
        Returns a single concatenated string.
        """
        if not self._init_reader():
            return {"text": "", "error": "OCR engine not available."}

        try:
            results = self.reader.readtext(image_path)
            extracted_text = " ".join([res[1] for res in results])
            
            # Calculate average confidence
            avg_conf = 0.0
            if results:
                avg_conf = sum([res[2] for res in results]) / len(results)
                
            return {
                "text": extracted_text, 
                "status": "success",
                "clarity_raw": round(avg_conf * 100, 2)
            }
        except Exception as e:
            logger.error(f"Error during OCR extraction: {e}")
            return {"text": "", "status": "error", "error": str(e)}
