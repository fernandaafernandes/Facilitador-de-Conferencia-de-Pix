from flask import Blueprint
from app.extensions import db

test_bp = Blueprint("test", __name__)

@test_bp.get("/db-test")
def db_test():
    db.session.execute(db.text("SELECT 1"))
    return {"status": "PostgreSQL conectado"}
