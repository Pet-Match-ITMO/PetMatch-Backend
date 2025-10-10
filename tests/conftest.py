import dotenv
import pytest_asyncio
from quart import Quart
from quart_schema import QuartSchema
from decouple import config
from app.src.db.models.base import Base
from app.src.db.utils.helper import DBHelper
from app.src.scheme import ErrorResponse
from werkzeug.exceptions import HTTPException
import redis.asyncio as aioredis
from testcontainers.redis import RedisContainer

dotenv.load_dotenv("test.env")


@pytest_asyncio.fixture
async def test_db():
    # Use in-memory SQLite for tests
    db_url = config('TEST_DB_URL')
    db_helper = DBHelper(db_url)

    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield db_helper
    await db_helper.engine.dispose()


@pytest_asyncio.fixture
async def redis_conn_pool():
    with RedisContainer("redis:7-alpine", password=config("REDIS_PASSWORD")) as redis_container:
        host = redis_container.get_container_host_ip()
        port = redis_container.get_exposed_port(
            config("REDIS_PORT", cast=int)
        )

        yield aioredis.ConnectionPool(
            host=host,
            port=port,
            db=config("REDIS_DB", cast=int),
            password=config("REDIS_PASSWORD"),
        )


@pytest_asyncio.fixture
async def template_app(test_db, redis_conn_pool):
    app = Quart(__name__)

    QuartSchema(app)

    app.config['TESTING'] = True
    app.config['QUART_SCHEMA_CONVERT_CASING'] = False
    app.config['QUART_SCHEMA_CONVERSION_PREFERENCE'] = None
    
    app.config['JWT_SECRET'] = 'test-secret-key'
    
    # Use the test_db fixture directly
    app.config['db_helper'] = test_db

    # redis connection pool
    app.config['redis_conn_pool'] = redis_conn_pool 

    @app.errorhandler(HTTPException)
    async def handle_http_exception(e: HTTPException):
        # serialize HTTPException to JSON using a Pydantic model
        return ErrorResponse(error=e.name, detail=e.description).model_dump(), e.code
    
    return app
