from threading import Lock

_prediction_service = None
_report_service = None
_prediction_lock = Lock()
_report_lock = Lock()


def get_prediction_service():
    global _prediction_service
    if _prediction_service is None:
        with _prediction_lock:
            if _prediction_service is None:
                from services.prediction_service import PredictionService

                _prediction_service = PredictionService()
    return _prediction_service


def get_report_service():
    global _report_service
    if _report_service is None:
        with _report_lock:
            if _report_service is None:
                from services.report_service import ReportService

                _report_service = ReportService()
    return _report_service
