from flask import Blueprint, request, jsonify
from services.runtime_services import get_model_info_service

info_bp = Blueprint('info', __name__)


@info_bp.route('/model-info', methods=['GET'])
def get_model_info():
    try:
        disease = request.args.get('disease', 'diabetes')
        model_info = get_model_info_service()
        result = model_info.get_model_info(disease)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to retrieve model information."}), 500
