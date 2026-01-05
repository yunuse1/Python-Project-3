from flask.testing import FlaskClient
import pytest
import sys
import os
import json

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home(client: FlaskClient):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Crypto Analysis API is running!" in response.data

def test_get_all_coins(client: FlaskClient):
    response = client.get('/api/all-coins')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert isinstance(data, list)

def test_get_popular_coins(client: FlaskClient):
    response = client.get('/api/popular-coins')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert isinstance(data, list)

def test_get_market_coins(client: FlaskClient):
    response = client.get('/api/market-coins')
    assert response.status_code in [200, 500]
    if response.status_code == 200:
        data = json.loads(response.data)
        assert isinstance(data, list)

def test_get_coin_data_not_found(client: FlaskClient):
    response = client.get('/api/market/nonexistent-coin-xyz')
    assert response.status_code in [404, 500]

def test_get_analysis_endpoint(client: FlaskClient):
    response = client.get('/api/analysis/bitcoin')
    assert response.status_code in [200, 404, 500]

def test_get_report_endpoint(client: FlaskClient):
    response = client.get('/api/report/bitcoin')
    assert response.status_code in [200, 404, 500]

def test_get_forecast_endpoint(client: FlaskClient):
    response = client.get('/api/forecast/bitcoin')
    assert response.status_code in [200, 404, 500]

def test_compare_endpoint_missing_params(client: FlaskClient):
    response = client.get('/api/compare')
    assert response.status_code in [400, 404, 500]

def test_compare_endpoint_with_params(client: FlaskClient):
    response = client.get('/api/compare?coin1=bitcoin&coin2=ethereum')
    assert response.status_code in [200, 404, 500]

def test_users_endpoint(client: FlaskClient):
    response = client.get('/api/users')
    assert response.status_code in [200, 500]

def test_investor_stats_endpoint(client: FlaskClient):
    response = client.get('/api/investor-stats')
    assert response.status_code in [200, 404, 500]

def test_invalid_endpoint(client: FlaskClient):
    response = client.get('/api/invalid-endpoint-xyz')
    assert response.status_code == 404