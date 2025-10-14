import pytest
from unittest.mock import patch
from app.main import create_app



@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_get_path_success(client):
    """
    Test that the GET /paths/calculate endpoint is working correctly
    with the appropriate parameters.
    """
    # We use 'patch' to intercept the call to the AI model and simulate its response.
    # This isolates our test from the AI logic.
    with patch('app.api.paths.call_ai_model') as mock_call_ai:
        
        mock_response = {
            "routes": [
                {
                    "coordinates": [
                        [-64.349323, -33.123203],
                        [-64.349316, -33.123246],
                        [-64.349561, -33.124013],
                        [-64.349619, -33.124079],
                        [-64.349687, -33.124143]
                    ],
                    "duration": 127.5,
                    "distance": 1057.8
                }
            ],
            "waypoints": []

        }

        mock_call_ai.return_value = mock_response

        # We make the call to the endpoint through the test client
        response = client.get('/paths/calculate?start_node=A&end_node=B')

        assert response.status_code == 200

        assert response.json== mock_response

        mock_call_ai.assert_called_once_with('A','B')

def test_get_path_missing_params(client):
    """
    Test that the endpoint returns a 400 error if parameters are missing.
    """
    # Falta el end_node
    response = client.get('/paths/calculate?start_node=A')


    assert response.status_code == 400

    json_data = response.get_json()
    assert "error" in json_data
    assert "The 'start_node' and 'end_node' parameters are required" in json_data["error"]
    
