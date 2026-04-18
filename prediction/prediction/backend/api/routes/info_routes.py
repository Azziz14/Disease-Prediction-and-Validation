from flask import Blueprint, request, jsonify
from services.model_info_service import ModelInfoService

info_bp = Blueprint('info', __name__)

model_info = ModelInfoService()


@info_bp.route('/model-info', methods=['GET'])
def get_model_info():
    try:
        disease = request.args.get('disease', 'diabetes')
        result = model_info.get_model_info(disease)
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to retrieve model information."}), 500
