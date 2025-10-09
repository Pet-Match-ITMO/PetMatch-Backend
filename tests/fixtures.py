import pytest_asyncio
from quart import Quart
from quart_schema import QuartSchema
from decouple import config
from app.src.api.v1.auth.handlers import auth_bp
from app.src.db.models.base import Base
from app.src.db.utils.helper import DBHelper
from app.src.scheme import ErrorResponse
from werkzeug.exceptions import HTTPException


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
async def template_app(test_db):
    app = Quart(__name__)

    QuartSchema(app)

    app.config['TESTING'] = True
    app.config['QUART_SCHEMA_CONVERT_CASING'] = False
    app.config['QUART_SCHEMA_CONVERSION_PREFERENCE'] = None
    
    app.config['JWT_SECRET'] = 'test-secret-key'
    
    # Use the test_db fixture directly
    app.config['db_helper'] = test_db

    @app.errorhandler(HTTPException)
    async def handle_http_exception(e: HTTPException):
        # serialize HTTPException to JSON using a Pydantic model
        return ErrorResponse(error=e.name, detail=e.description).model_dump(), e.code
    
    return app