import sys
import os
import traceback
from dotenv import load_dotenv

# Load environment variables early with absolute path
env_path = r"c:\Users\ashis\Downloads\prediction (2)\prediction\prediction\.env"
load_dotenv(env_path)
print(f"[BOOT] Loaded .env from folder structure")
print(f"[BOOT] Groq Key Loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")
print(f"[BOOT] OpenRouter Key Loaded: {'Yes' if os.getenv('OPENROUTER_API_KEY') else 'No'}")

from flask import Flask
from flask_cors import CORS
from api.routes.auth_routes import auth_bp
from api.routes.diagnosis_routes import diagnosis_bp
from api.routes.image_routes import image_bp
from api.routes.info_routes import info_bp
from api.routes.multimodal_routes import multimodal_bp
from api.routes.dashboard_routes import dashboard_bp
from api.routes.predict_routes import predict_bp
from api.routes.assistant_routes import assistant_bp
from api.routes.assignment_routes import assignment_bp
from api.routes.doctor_review_routes import doctor_review_bp
from api.routes.ocr_routes import ocr_bp
from api.routes.ai_enhancement_routes import ai_enhancement_bp
from utils.db import db_client 
from utils.preloader import warmup_all
from utils.auth_store import ensure_default_admin

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(diagnosis_bp, url_prefix='/api')
app.register_blueprint(image_bp, url_prefix='/api')
app.register_blueprint(info_bp, url_prefix='/api')
app.register_blueprint(multimodal_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')
app.register_blueprint(predict_bp, url_prefix='/api')
app.register_blueprint(assistant_bp, url_prefix='/api')
app.register_blueprint(assignment_bp, url_prefix='/api')
app.register_blueprint(doctor_review_bp, url_prefix='/api')
app.register_blueprint(ocr_bp, url_prefix='/api')
app.register_blueprint(ai_enhancement_bp, url_prefix='/api')

@app.route('/warmup', methods=['GET'])
def warmup():
    """Manual warmup trigger."""
    warmup_all()
    return {"status": "All services preloaded - analysis now fast!"}

if __name__ == "__main__":
    print("STARTING BACKEND IN STABILIZATION MODE (debug=False)...")
    ensure_default_admin() 
    warmup_all()  
    app.run(host='0.0.0.0', debug=False, port=5000)
