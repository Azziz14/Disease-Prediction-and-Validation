from flask import Flask
from flask_cors import CORS
from api.routes.diagnosis_routes import diagnosis_bp
from api.routes.image_routes import image_bp
from api.routes.info_routes import info_bp
from api.routes.multimodal_routes import multimodal_bp
from api.routes.dashboard_routes import dashboard_bp
from utils.db import db_client # Initialize DB connection early

app = Flask(__name__)
CORS(app)

app.register_blueprint(diagnosis_bp, url_prefix='/api')
app.register_blueprint(image_bp, url_prefix='/api')
app.register_blueprint(info_bp, url_prefix='/api')
app.register_blueprint(multimodal_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

if __name__ == "__main__":
    app.run(debug=True)