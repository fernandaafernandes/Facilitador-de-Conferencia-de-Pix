import os
from flask import Flask
from dotenv import load_dotenv

from app.extensions import db, migrate

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "segredo")

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        db_url = "sqlite:///:memory:"  # fallback 

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    
    from app import models  # noqa: F401

    
    from app.routes.casaamor import casaamor_bp
    app.register_blueprint(casaamor_bp)

    return app
