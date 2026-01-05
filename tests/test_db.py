import sys
import os
import pytest
import pandas as pd
import mongomock

# 1. Python'a src klasörünün yerini öğretiyoruz (Import hatasını çözen kısım)
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

# 2. Artık alt klasörden (db) güvenle import edebiliriz
from db.database_manager import save_market_data, get_market_data, seed_users_into_code
import db.database_manager as db_module

@pytest.fixture(autouse=True)
def mock_db(monkeypatch):
    """Gerçek MongoDB yerine sanal (mock) DB kullanır. Gerçek verileri korur."""
    fake_client = mongomock.MongoClient()
    fake_db = fake_client["test_crypto_db"]
    
    # database_manager içindeki gerçek bağlantıları sanallarıyla değiştiriyoruz
    monkeypatch.setattr(db_module, "client", fake_client)
    monkeypatch.setattr(db_module, "db", fake_db)
    monkeypatch.setattr(db_module, "market_collection", fake_db["market_data"])
    monkeypatch.setattr(db_module, "users_collection", fake_db["users"])
    
    return fake_db

def test_save_and_get_market_data():
    """Veritabanına veri yazma ve geri okuma başarılı mı?"""
    coin_id = "test-bitcoin"
    test_df = pd.DataFrame([
        {"timestamp": "2023-01-01", "price": 50000},
        {"timestamp": "2023-01-02", "price": 51000}
    ])
    
    # Veriyi kaydet
    save_market_data(coin_id, test_df)
    
    # Veriyi geri çek
    result_df = get_market_data(coin_id)
    
    assert not result_df.empty, "Veritabanından veri boş döndü!"
    assert len(result_df) == 2, "Kaydedilen veri sayısı eşleşmiyor!"
    assert "coin_id" in result_df.columns, "coin_id kolonu eksik!"

def test_seed_users():
    """Sahte kullanıcı oluşturma (seed) fonksiyonu çalışıyor mu?"""
    # 10 tane sahte kullanıcı oluşturmayı dene
    seed_users_into_code(count=10)
    
    # Veritabanında kaç kullanıcı var bak
    count = db_module.users_collection.count_documents({})
    assert count == 10, f"Beklenen 10 kullanıcıydı ama {count} bulundu!"

def test_get_market_data_empty():
    """Olmayan bir coin arandığında sistem çökmeden boş DataFrame dönüyor mu?"""
    result = get_market_data("olmayan-coin-123")
    assert isinstance(result, pd.DataFrame), "Hata durumunda DataFrame dönmeli!"
    assert result.empty, "Olmayan coin için veri boş olmalı!"