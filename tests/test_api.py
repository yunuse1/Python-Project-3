import pytest
from app import app 

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client):
    """API'nin çalışıp çalışmadığını kontrol eder"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Crypto Analysis API is running!" in response.data