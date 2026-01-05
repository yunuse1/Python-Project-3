import pytest
import mongomock
import pandas as pd
import sys
import os

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
scripts_path = os.path.abspath(os.path.join(current_dir, '..', 'src', 'scripts'))
if src_path not in sys.path:
    sys.path.append(src_path)
if scripts_path not in sys.path:
    sys.path.append(scripts_path)

from load_data_for_analysis import load_popular_coins  # type: ignore
from fill_missing_market_data import logger as script_logger  # type: ignore

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    return client

def test_load_data_script(mock_db):
    db = mock_db['crypto_project_db']
    db['popular_coins'].insert_one({'symbol': 'BTC', 'name': 'Bitcoin'})
    
    df = load_popular_coins(mock_db)
    assert not df.empty
    assert df.iloc[0]['symbol'] == 'BTC'

def test_load_data_empty_collection(mock_db):
    df = load_popular_coins(mock_db)
    assert df.empty

def test_load_data_multiple_coins(mock_db):
    db = mock_db['crypto_project_db']
    db['popular_coins'].insert_many([
        {'symbol': 'BTC', 'name': 'Bitcoin'},
        {'symbol': 'ETH', 'name': 'Ethereum'},
        {'symbol': 'SOL', 'name': 'Solana'}
    ])
    
    df = load_popular_coins(mock_db)
    assert len(df) == 3

def test_fill_missing_logic_check():
    all_coins = [{'symbol': 'BTC'}, {'symbol': 'ETH'}]
    market_data = ['btc']
    missing = [c for c in all_coins if c['symbol'].lower() not in market_data]
    assert len(missing) == 1
    assert missing[0]['symbol'] == 'ETH'

def test_fill_missing_all_present():
    all_coins = [{'symbol': 'BTC'}, {'symbol': 'ETH'}]
    market_data = ['btc', 'eth']
    missing = [c for c in all_coins if c['symbol'].lower() not in market_data]
    assert len(missing) == 0

def test_fill_missing_all_missing():
    all_coins = [{'symbol': 'BTC'}, {'symbol': 'ETH'}, {'symbol': 'SOL'}]
    market_data = []
    missing = [c for c in all_coins if c['symbol'].lower() not in market_data]
    assert len(missing) == 3

def test_sync_logic(mock_db):
    db = mock_db['crypto_project_db']
    details_col = db['all_coins_details']
    all_coins_col = db['all_coins']

    details_col.insert_one({
        'id': 'solana',
        'symbol': 'sol',
        'name': 'Solana',
        'current_price': 100
    })

    for doc in details_col.find({}):
        coin_id = doc.get('id')
        record = {'id': coin_id, 'symbol': doc.get('symbol')}
        all_coins_col.update_one({'id': coin_id}, {'$setOnInsert': record}, upsert=True)

    result = all_coins_col.find_one({'id': 'solana'})
    assert result is not None
    assert result['symbol'] == 'sol'

def test_sync_multiple_coins(mock_db):
    db = mock_db['crypto_project_db']
    details_col = db['all_coins_details']
    all_coins_col = db['all_coins']

    details_col.insert_many([
        {'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'},
        {'id': 'ethereum', 'symbol': 'eth', 'name': 'Ethereum'}
    ])

    for doc in details_col.find({}):
        coin_id = doc.get('id')
        record = {'id': coin_id, 'symbol': doc.get('symbol')}
        all_coins_col.update_one({'id': coin_id}, {'$setOnInsert': record}, upsert=True)

    assert all_coins_col.count_documents({}) == 2

def test_sync_no_duplicate_inserts(mock_db):
    db = mock_db['crypto_project_db']
    details_col = db['all_coins_details']
    all_coins_col = db['all_coins']

    details_col.insert_one({'id': 'bitcoin', 'symbol': 'btc', 'name': 'Bitcoin'})

    for _ in range(3):
        for doc in details_col.find({}):
            coin_id = doc.get('id')
            record = {'id': coin_id, 'symbol': doc.get('symbol')}
            all_coins_col.update_one({'id': coin_id}, {'$setOnInsert': record}, upsert=True)

    assert all_coins_col.count_documents({}) == 1    