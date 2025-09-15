from quart import Blueprint

from .auth import auth_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
v1_bp.register_blueprint(auth_bp)
