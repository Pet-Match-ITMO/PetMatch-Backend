import uvicorn
from decouple import config
import redis.asyncio as aioredis

from quart import Quart
from quart_schema import QuartSchema
from quart_cors import cors
from werkzeug.exceptions import HTTPException

from src.api import api_bp
from src.db import DBHelper
from src.scheme import ErrorResponse


def create_app():
    app = Quart(__name__)
    QuartSchema(app)
    app.register_blueprint(api_bp)
    app = cors(
        app,
        allow_origin="*",
    )

    async def create_lifespan_handler():
        app.config['db_helper'] = DBHelper(config('DB_URL'))

        app.config['redis_conn_pool'] = aioredis.ConnectionPool(
            host=config('REDIS_HOST'),
            port=config('REDIS_PORT', cast=int), 
            db=config('REDIS_DB', cast=int),
            password=config('REDIS_PASSWORD', default=None)
        )

        yield

        await app.config['redis_conn_pool'].disconnect()

    app.while_serving(create_lifespan_handler)
        
    async def create_error_handler(e: HTTPException):
        # serialize HTTPException to JSON using a Pydantic model
        return ErrorResponse(error=e.name, detail=e.description).model_dump(), e.code

    app.errorhandler(HTTPException)(create_error_handler)

    return app


if __name__ == "__main__":
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)
