import os
import dotenv
from quart import Blueprint
from quart_schema import validate_request, validate_response, validate_querystring
from .scheme import PetsRequest, PetsResponse, PetsQuery
from src.utils import redis_cache
import httpx

dotenv.load_dotenv()
ML_API_URL = os.environ['ML_API_URL']
pets_bp = Blueprint("pets", __name__, url_prefix="/pets")


@pets_bp.get("/get_pets", endpoint='get_pets')
@validate_response(list[PetsResponse], 200)
@validate_querystring(PetsQuery)
@redis_cache()
async def get_pets(query_args: PetsQuery):
    response = httpx.get(ML_API_URL+f'pets?limit={query_args.limit}')
    if response.status_code != 200:
        print('Error getting pets')
        return []
    return [PetsResponse(**i) for i in response.json()]
    

@pets_bp.post("/get_next_pet", endpoint='get_next_pet')
@validate_request(PetsRequest)
@validate_response(PetsResponse, 200)
@redis_cache()
async def get_next_pet(data: PetsRequest):
    response = httpx.post(
        ML_API_URL+'get_next_pet',
        headers={'Content-Type': 'application/json', 'accept':'application/json'},
        json = data.model_dump(exclude_unset=True, exclude_none=True)
        )
    if response.status_code != 200:
        print('Error getting next pet')
        return []
    return PetsResponse(**response.json())

