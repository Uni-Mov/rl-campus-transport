import pytest
from app.main import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_list_users_endpoint(client):
    """Test GET /users returns JSON"""
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json, list)

def test_get_user_endpoint(client):
    """Test GET /users/<id>"""
    # Assuming the DB is empty initially, should return 404
    response = client.get("/users/1")
    assert response.status_code == 404
