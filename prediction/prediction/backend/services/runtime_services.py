from threading import Lock

_image_classifier = None
_nlp_processor = None
_model_info_service = None
_ocr_service = None
_voice_intake_service = None

_image_classifier_lock = Lock()
_nlp_processor_lock = Lock()
_model_info_lock = Lock()
_ocr_lock = Lock()
_voice_intake_lock = Lock()


def get_image_classifier():
    global _image_classifier
    if _image_classifier is None:
        with _image_classifier_lock:
            if _image_classifier is None:
                from models.image_classifier import ImageClassifier

                _image_classifier = ImageClassifier()
    return _image_classifier


def get_nlp_processor():
    global _nlp_processor
    if _nlp_processor is None:
        with _nlp_processor_lock:
            if _nlp_processor is None:
                from nlp.processor_enhanced import NLPProcessorEnhanced

                _nlp_processor = NLPProcessorEnhanced()
    return _nlp_processor


def get_model_info_service():
    global _model_info_service
    if _model_info_service is None:
        with _model_info_lock:
            if _model_info_service is None:
                from services.model_info_service import ModelInfoService

                _model_info_service = ModelInfoService()
    return _model_info_service


def get_ocr_service():
    global _ocr_service
    if _ocr_service is None:
        with _ocr_lock:
            if _ocr_service is None:
                from services.ocr_service import OCRService

                _ocr_service = OCRService()
    return _ocr_service


def get_voice_intake_service():
    global _voice_intake_service
    if _voice_intake_service is None:
        with _voice_intake_lock:
            if _voice_intake_service is None:
                from services.voice_intake_service import VoiceIntakeService

                _voice_intake_service = VoiceIntakeService()
    return _voice_intake_service
