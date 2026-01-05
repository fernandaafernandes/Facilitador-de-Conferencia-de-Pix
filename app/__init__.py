from flask import Flask
from dotenv import load_dotenv
import os

from app.extensions import db

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    # 🔽 REGISTRO DAS ROTAS
    from app.routes.test import test_bp
    app.register_blueprint(test_bp)

    return app
