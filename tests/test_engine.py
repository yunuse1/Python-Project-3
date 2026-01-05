import sys
import os
import pytest
import pandas as pd
import numpy as np

current_dir = os.path.dirname(__file__)
src_path = os.path.abspath(os.path.join(current_dir, '..', 'src'))
if src_path not in sys.path:
    sys.path.append(src_path)

from analysis_engine import CryptoAnalysisEngine

@pytest.fixture
def engine():
    return CryptoAnalysisEngine()

@pytest.fixture
def mock_data():
    dates = pd.date_range(start='2023-01-01', periods=60, freq='D')
    prices = np.random.uniform(20000, 30000, size=60)
    
    data = {
        'timestamp': dates,
        'price': prices,
        'close': prices,
        'high': prices + 500,
        'low': prices - 500,
        'volume': np.random.uniform(100, 1000, size=60)
    }
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

@pytest.fixture
def small_data():
    dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
    prices = [100, 102, 101, 105, 103]
    return pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'close': prices,
        'high': [p + 2 for p in prices],
        'low': [p - 2 for p in prices],
        'volume': [1000, 1100, 900, 1200, 1050]
    })

def test_rsi_range(engine, mock_data):
    analysis = engine.get_full_analysis(mock_data)
    df = analysis['dataframe']
    
    if 'rsi' in df.columns:
        rsi_values = df['rsi'].dropna()
        assert all(0 <= x <= 100 for x in rsi_values)
    else:
        pytest.fail("RSI column not found!")

def test_engine_output_structure(engine, mock_data):
    result = engine.get_full_analysis(mock_data)

    assert isinstance(result, dict)
    assert 'dataframe' in result
    assert 'indicators' in result
    assert 'levels' in result
    assert 'current_price' in result
    assert not result['dataframe'].empty
    assert isinstance(result['indicators'], dict)

def test_sma_calculation(engine, mock_data):
    result = engine.get_full_analysis(mock_data)
    df = result['dataframe']
    
    assert 'sma_7' in df.columns or 'sma_30' in df.columns

def test_ema_calculation(engine, mock_data):
    df = engine.calculate_ema(mock_data, column='price', periods=[7, 14])
    
    assert 'ema_7' in df.columns
    assert 'ema_14' in df.columns
    assert not df['ema_7'].isna().all()

def test_macd_calculation(engine, mock_data):
    df = engine.calculate_macd(mock_data, column='price')
    
    assert 'macd' in df.columns
    assert 'macd_signal' in df.columns
    assert 'macd_histogram' in df.columns

def test_bollinger_bands(engine, mock_data):
    df = engine.calculate_bollinger_bands(mock_data, column='price')
    
    assert 'bb_middle' in df.columns
    assert 'bb_upper' in df.columns
    assert 'bb_lower' in df.columns
    assert 'bb_width' in df.columns
    
    valid_rows = df.dropna(subset=['bb_upper', 'bb_lower', 'bb_middle'])
    if len(valid_rows) > 0:
        assert all(valid_rows['bb_upper'] >= valid_rows['bb_middle'])
        assert all(valid_rows['bb_lower'] <= valid_rows['bb_middle'])

def test_volatility_calculation(engine, mock_data):
    df = engine.calculate_volatility(mock_data, column='price', periods=[7, 30])
    
    assert 'daily_return' in df.columns
    assert 'volatility_7d' in df.columns
    assert 'volatility_30d' in df.columns

def test_max_drawdown(engine, mock_data):
    df = engine.calculate_max_drawdown(mock_data, column='price')
    
    assert 'drawdown' in df.columns
    assert 'max_drawdown' in df.columns
    
    valid_dd = df['max_drawdown'].dropna()
    if len(valid_dd) > 0:
        assert all(valid_dd <= 0)

def test_sharpe_ratio(engine, mock_data):
    df = engine.calculate_sharpe_ratio(mock_data, column='price')
    
    assert 'sharpe_ratio' in df.columns

def test_trend_detection(engine, mock_data):
    result = engine.detect_trend(mock_data, column='price')
    
    if isinstance(result, str):
        assert result in ['bullish', 'bearish', 'neutral']
    else:
        assert result is not None

def test_empty_dataframe(engine):
    empty_df = pd.DataFrame()
    
    try:
        result = engine.calculate_sma(empty_df, column='price')
        assert result.empty
    except (KeyError, ValueError):
        pass

def test_single_row_dataframe(engine):
    single_df = pd.DataFrame({
        'timestamp': [pd.Timestamp('2023-01-01')],
        'price': [100.0]
    })
    
    result = engine.calculate_sma(single_df, column='price', periods=[7])
    assert 'sma_7' in result.columns

def test_negative_prices(engine):
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'price': [-100 + i for i in range(30)]
    })
    
    result = engine.calculate_rsi(df, column='price')
    assert 'rsi' in result.columns

def test_constant_prices(engine):
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2023-01-01', periods=30, freq='D'),
        'price': [100.0] * 30
    })
    
    result = engine.calculate_volatility(df, column='price', periods=[7])
    valid_vol = result['volatility_7d'].dropna()
    if len(valid_vol) > 0:
        assert all(v == 0 or np.isclose(v, 0, atol=1e-10) for v in valid_vol)