import pytest
import pytest_asyncio
from app.src.api.v1.auth.handlers import auth_bp
from .fixtures import template_app


@pytest_asyncio.fixture
async def app(template_app):
    template_app.register_blueprint(auth_bp)
    return template_app


@pytest.mark.asyncio
async def test_register_user(app):
    client = app.test_client()
    # app.config['db_helper'] is now set in the app fixture

    user_data = {
        "email": "test@example.com",
        "password": "securepassword123",
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