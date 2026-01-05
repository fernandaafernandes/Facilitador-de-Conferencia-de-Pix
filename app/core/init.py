import os
from flask import Flask
from dotenv import load_dotenv

from app.extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    # Configurações 
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "segredo")

    # Diretório de uploads
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    app.config["UPLOAD_DIR"] = upload_dir

    # Banco de dados 
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        
        db_url = "sqlite:///:memory:"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # extensões
    db.init_app(app)

  

    # Blueprints
    from app.routes.casaamor import casaamor_bp
    from app.routes.test import test_bp

    app.register_blueprint(casaamor_bp)
    app.register_blueprint(test_bp)

    return app
