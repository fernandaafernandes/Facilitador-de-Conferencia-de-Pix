import os
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL não definida")

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

    app.config["UPLOAD_DIR"] = "/tmp/uploads"
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    db.init_app(app)

    from app.routes.casaamor import casaamor_bp
    app.register_blueprint(casaamor_bp)

    return app
