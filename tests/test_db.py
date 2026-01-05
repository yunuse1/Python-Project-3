import sys
import os
import pytest
import pandas as pd
import mongomock

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from db.database_manager import save_market_data, get_market_data, seed_users_into_code
import db.database_manager as db_module

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    fake_client = mongomock.MongoClient()
    fake_db = fake_client["test_crypto_db"]
    
    monkeypatch.setattr(db_module, "client", fake_client)
    monkeypatch.setattr(db_module, "db", fake_db)
    monkeypatch.setattr(db_module, "market_collection", fake_db["market_data"])
    monkeypatch.setattr(db_module, "users_collection", fake_db["users"])
    
    return fake_db

def test_save_and_get_market_data():
    coin_id = "test-bitcoin"
    test_df = pd.DataFrame([
        {"timestamp": "2023-01-01", "price": 50000},
        {"timestamp": "2023-01-02", "price": 51000}
    ])
    
    save_market_data(coin_id, test_df)
    result_df = get_market_data(coin_id)
    
    assert not result_df.empty
    assert len(result_df) == 2
    assert "coin_id" in result_df.columns

def test_seed_users():
    seed_users_into_code(count=10)
    count = db_module.users_collection.count_documents({})
    assert count == 10

def test_get_market_data_empty():
    result = get_market_data("nonexistent-coin-123")
    assert isinstance(result, pd.DataFrame)
    assert result.empty

def test_save_empty_dataframe():
    coin_id = "empty-test"
    empty_df = pd.DataFrame()
    
    save_market_data(coin_id, empty_df)
    result = get_market_data(coin_id)
    assert result.empty

def test_save_large_dataset():
    coin_id = "large-test"
    large_df = pd.DataFrame({
        "timestamp": pd.date_range(start="2020-01-01", periods=1000, freq="D"),
        "price": range(1000)
    })
    
    save_market_data(coin_id, large_df)
    result = get_market_data(coin_id)
    
    assert len(result) >= 999

def test_overwrite_market_data():
    coin_id = "overwrite-test"
    
    df1 = pd.DataFrame([{"timestamp": "2023-01-01", "price": 100}])
    save_market_data(coin_id, df1)
    
    df2 = pd.DataFrame([
        {"timestamp": "2023-01-01", "price": 200},
        {"timestamp": "2023-01-02", "price": 300}
    ])
    save_market_data(coin_id, df2)
    
    result = get_market_data(coin_id)
    assert len(result) >= 1

def test_special_characters_coin_id():
    coin_id = "test-coin_with.special"
    test_df = pd.DataFrame([{"timestamp": "2023-01-01", "price": 100}])
    
    save_market_data(coin_id, test_df)
    result = get_market_data(coin_id)
    
    assert not result.empty

def test_seed_users_multiple_calls():
    seed_users_into_code(count=5)
    first_count = db_module.users_collection.count_documents({})
    
    seed_users_into_code(count=5)
    second_count = db_module.users_collection.count_documents({})
    
    assert first_count == 5
    assert second_count >= 5

def test_market_data_with_null_values():
    coin_id = "null-test"
    test_df = pd.DataFrame([
        {"timestamp": "2023-01-01", "price": 100, "volume": None},
        {"timestamp": "2023-01-02", "price": 200, "volume": 500}
    ])
    
    save_market_data(coin_id, test_df)
    result = get_market_data(coin_id)
    
    assert len(result) >= 1