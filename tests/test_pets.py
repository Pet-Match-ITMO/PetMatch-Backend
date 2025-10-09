import pytest_asyncio
from app.src.api.v1.pets import pets_bp
import pytest

@pytest_asyncio.fixture
async def app(template_app):
    template_app.register_blueprint(pets_bp)
    return template_app
 
@pytest.mark.asyncio
async def test_get_pets(app):
    client = app.test_client()
    
    response = await client.get('/pets/get_pets')

    assert response.status_code == 200
    data = await response.get_json()
    assert data


@pytest.mark.asyncio
async def test_get_next_pet(app):
    client = app.test_client()

    user_data = {
        'user_id': 0,
        'next_token': 0       
    }

    response = await client.post(
        '/pets/get_next_pet',
        json=user_data,
        headers={'Content-Type': 'application/json', 'accept': 'application/json'}
        )
    
    assert response.status_code == 200
    await response.get_json()
    
    
