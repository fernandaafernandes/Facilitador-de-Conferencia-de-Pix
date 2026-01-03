import os
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "segredo"
    app.config["UPLOAD_DIR"] = os.path.join(os.getcwd(), "uploads")
    os.makedirs(app.config["UPLOAD_DIR"], exist_ok=True)

    # registra rotas
    from app.routes.casaamor import casaamor_bp
    app.register_blueprint(casaamor_bp)

    return app
