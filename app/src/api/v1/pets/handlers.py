import os
import dotenv
from quart import Blueprint, jsonify, current_app, abort
from quart_schema import validate_request, validate_response
from .scheme import PetsRequest, PetsResponse
from src.utils import redis_cache

dotenv.load_dotenv()

pets_bp = Blueprint("pets", __name__, url_prefix="/auth")

@pets_bp.get("/pets")
@validate_request(PetsRequest)
@validate_response(PetsResponse, 200)
@redis_cache
async def get_pet(data: PetsRequest):
    db_helper = current_app.config['db_helper']
    async with db_helper.make_session() as session:
        pass