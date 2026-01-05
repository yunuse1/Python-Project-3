from flask.testing import FlaskClient
import pytest
import sys
import os

# Bu 2 satır hayati önem taşıyor: Üst klasördeki app.py'yi bulmasını sağlar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client: FlaskClient):
    """Ana sayfa mesajını kontrol eder"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Crypto Analysis API is running!" in response.data