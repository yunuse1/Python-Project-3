import sys
import os
import pytest
import pandas as pd
import numpy as np

# 1. src klasörünü Python'a tanıtıyoruz (Import hatasını önler)
current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

# 2. Analiz motorunu import ediyoruz
from analysis_engine import CryptoAnalysisEngine

@pytest.fixture
def engine():
    return CryptoAnalysisEngine()

@pytest.fixture
def mock_data():
    """Analiz motorunun beklediği TÜM sütunları içeren sahte veri seti"""
    dates = pd.date_range(start='2023-01-01', periods=60, freq='D')
    prices = np.random.uniform(20000, 30000, size=60)
    
    data = {
        'timestamp': dates,
        'price': prices,        # Hata veren 'price' sütunu eklendi
        'close': prices,        # Bazı hesaplamalar 'close' bekleyebilir
        'high': prices + 500,
        'low': prices - 500,
        'volume': np.random.uniform(100, 1000, size=60)
    }
    df = pd.DataFrame(data)
    # Pandas'ın datetime formatında olduğundan emin olalım
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

def test_rsi_range(engine, mock_data):
    """RSI hesaplamasının 0-100 arasında olduğunu doğrular"""
    # get_full_analysis artık 'price' sütununu bulabilecek
    analysis = engine.get_full_analysis(mock_data)
    df = analysis['dataframe']
    
    # RSI hesaplanmış mı ve mantıklı aralıkta mı?
    if 'rsi' in df.columns:
        rsi_values = df['rsi'].dropna()
        assert all(0 <= x <= 100 for x in rsi_values)
    else:
        pytest.fail("RSI sütunu hesaplanamadı!")

def test_engine_output_structure(engine, mock_data):
    """Analiz motorunun gerçek çıktı yapısını doğrular"""
    result = engine.get_full_analysis(mock_data)

    # 1. Çıktı bir sözlük mü?
    assert isinstance(result, dict), "Sonuç bir sözlük olmalı!"
    
    # 2. Senin kodunun döndürdüğü GERÇEK anahtarlar var mı?
    assert 'dataframe' in result, "Çıktıda 'dataframe' yok!"
    assert 'indicators' in result, "Çıktıda 'indicators' yok!"
    assert 'levels' in result, "Çıktıda 'levels' yok!"
    assert 'current_price' in result, "Çıktıda 'current_price' yok!"

    # 3. Veriler boş mu?
    assert not result['dataframe'].empty, "Dataframe boş döndü!"
    assert isinstance(result['indicators'], dict), "Indicators bir sözlük olmalı!"

def test_sma_calculation(engine, mock_data):
    """SMA (Basit Hareketli Ortalama) sütunlarının oluştuğunu kontrol eder"""
    result = engine.get_full_analysis(mock_data)
    df = result['dataframe']
    
    # app.py içindeki 7 ve 30 günlük SMA'ları kontrol et
    assert 'sma_7' in df.columns or 'sma_30' in df.columns, "SMA sütunları eksik!"