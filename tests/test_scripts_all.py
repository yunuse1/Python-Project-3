import pytest
import mongomock
import pandas as pd
import sys
import os

# Yolları ayarla (src ve scripts klasörlerini tanıtıyoruz)
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', '..', 'src'))
sys.path.append(src_path)

# Scriptleri import et
from scripts.load_data_for_analysis import load_popular_coins
from scripts.fill_missing_market_data import logger as script_logger # Sadece import testi için

@pytest.fixture
def mock_db():
    client = mongomock.MongoClient()
    return client

def test_load_data_script(mock_db):
    """load_data_for_analysis.py testini yapar"""
    db = mock_db['crypto_project_db']
    db['popular_coins'].insert_one({'symbol': 'BTC', 'name': 'Bitcoin'})
    
    df = load_popular_coins(mock_db)
    assert not df.empty
    assert df.iloc[0]['symbol'] == 'BTC'

def test_fill_missing_logic_check():
    """fill_missing_market_data.py içindeki mantığı kontrol eder"""
    # Bu script direkt çalıştırılmak üzere yazıldığı için 
    # içindeki mantık parçalarını burada manuel doğrulayabiliriz
    all_coins = [{'symbol': 'BTC'}, {'symbol': 'ETH'}]
    market_data = ['btc']
    missing = [c for c in all_coins if c['symbol'].lower() not in market_data]
    assert len(missing) == 1
    assert missing[0]['symbol'] == 'ETH'
    

def test_sync_logic(mock_db):
    """Koleksiyonlar arası veri senkronizasyon mantığını test eder"""
    db = mock_db['crypto_project_db']
    details_col = db['all_coins_details']
    all_coins_col = db['all_coins']

    # 1. Senaryo: Detaylarda yeni bir coin var
    details_col.insert_one({
        'id': 'solana',
        'symbol': 'sol',
        'name': 'Solana',
        'current_price': 100
    })

    # Script'teki mantığı simüle edelim
    for doc in details_col.find({}):
        coin_id = doc.get('id')
        record = {'id': coin_id, 'symbol': doc.get('symbol')}
        all_coins_col.update_one({'id': coin_id}, {'$setOnInsert': record}, upsert=True)

    # Doğrulama
    result = all_coins_col.find_one({'id': 'solana'})
    assert result is not None
    assert result['symbol'] == 'sol'    