from quart import Blueprint

from .auth import auth_bp
from .pets import pets_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/v1")
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(pets_bp)

__all__ = [
    "v1_bp",
]