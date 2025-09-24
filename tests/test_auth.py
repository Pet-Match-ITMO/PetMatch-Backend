import os
import dotenv

import pytest
import pytest_asyncio

from quart import Quart
from quart_schema import QuartSchema
from werkzeug.exceptions import HTTPException

from src.api.v1.auth.views import auth_bp
from src.db.base import Base
from src.db.utils.helper import DBHelper
from src.scheme import ErrorResponse

# Set environment variables before any imports
os.environ['QUART_SCHEMA_CONVERT_CASING'] = 'False'
dotenv.load_dotenv("test.env")


@pytest_asyncio.fixture
async def test_db():
    # Use in-memory SQLite for tests
    db_url = os.environ['TEST_DB_URL']
    db_helper = DBHelper(db_url)
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield db_helper
    await db_helper.engine.dispose()


@pytest_asyncio.fixture
async def app(test_db):
    app = Quart(__name__)
    QuartSchema(app)
    app.register_blueprint(auth_bp)
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


@pytest.mark.asyncio
async def test_register_user(app):
    client = app.test_client()
    # app.config['db_helper'] is now set in the app fixture

    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
        "username": "testuser"
    }

    response = await client.post(
        "/auth/register",
        json=user_data,
        headers={'Content-Type': 'application/json', 'accept': 'application/json'}
    )
    assert response.status_code == 200
    data = await response.get_json()
    assert "token" in data
    assert "user_id" in data
    assert data["expires_in"] == 86400


@pytest.mark.asyncio
async def test_register_duplicate_email(app):
    client = app.test_client()

    user_data = {
        "email": "duplicate@example.com",
        "password": "password123",
        "username": "user1"
    }

    # First registration should succeed
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 200

    # Second registration with same email should fail
    response = await client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    data = await response.get_json()
    assert "error" in data
    assert "detail" in data
    assert "User already exists" in data["detail"]

@pytest.mark.asyncio
async def test_login_success(app):
    client = app.test_client()

    user_data = {
        "email": "login@example.com",
        "password": "validpassword",
        "username": "loginuser"
    }

    # Register user first
    await client.post("/auth/register", json=user_data)

    # Login with correct credentials
    login_data = {
        "email": "login@example.com",
        "password": "validpassword"
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    data = await response.get_json()
    assert "token" in data
    assert "user_id" in data

@pytest.mark.asyncio
async def test_login_invalid_password(app):
    client = app.test_client()

    user_data = {
        "email": "invalidpass@example.com",
        "password": "correctpassword",
        "username": "testuser"
    }

    # Register user
    await client.post("/auth/register", json=user_data)

    # Login with wrong password
    login_data = {
        "email": "invalidpass@example.com",
        "password": "wrongpassword"
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = await response.get_json()
    assert "error" in data
    assert "Invalid credentials" in data["error"]

@pytest.mark.asyncio
async def test_login_invalid_email(app):
    client = app.test_client()

    login_data = {
        "email": "nonexistent@example.com",
        "password": "anypassword"
    }
    response = await client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    data = await response.get_json()
    assert "error" in data
    assert "Invalid credentials" in data["error"]