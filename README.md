# CryptoAnalyst - Cryptocurrency Analysis Platform

A comprehensive cryptocurrency analysis platform with React.js frontend, Flask backend, MongoDB database, and advanced data science features including anomaly detection and technical analysis.

## 🚀 Features

### Visualization (+15 pts - React.js)
- **Interactive Charts**: Interactive charts with Recharts library
- **Dual Y-Axis Comparison**: Compare two different coins with real prices
- **Technical Analysis Dashboard**: RSI, MACD, Bollinger Bands charts
- **Responsive Design**: Modern, responsive design with Tailwind CSS

### Visualization (+5 pts - Seaborn)
- **Statistical Plots**: Histogram, KDE, Box Plot, Violin Plot
- **Correlation Heatmap**: Correlation heatmap between coins
- **Pair Plot**: Multivariate analysis with scatter matrix
- **Anomaly Visualization**: Anomaly visualization with Z-Score

---

## 📥 Scraped Messy Web Data (+10 pts)

### Data Source: Binance API

The data used in this project is fetched from **Binance Cryptocurrency Exchange** API. This is a REST API that returns raw (messy) JSON data.

#### API Endpoint
```
https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=1d&limit=90
```

#### Raw Data Format (Messy Data)
Raw data from Binance API comes in **nested array** format, with each element containing different data types:

```json
[
  [
    1704067200000,      // [0] Open time (Unix timestamp in milliseconds)
    "42150.00000000",   // [1] Open price (STRING - not float!)
    "43250.50000000",   // [2] High price (STRING)
    "41800.00000000",   // [3] Low price (STRING)
    "42890.25000000",   // [4] Close price (STRING)
    "1234.56789000",    // [5] Volume (STRING)
    1704153599999,      // [6] Close time (Unix timestamp)
    "52345678.90",      // [7] Quote asset volume (STRING)
    12345,              // [8] Number of trades (INTEGER)
    "678.90123456",     // [9] Taker buy base volume (STRING)
    "28765432.10",      // [10] Taker buy quote volume (STRING)
    "0"                 // [11] Ignore (STRING)
  ],
  // ... more candles
]
```

### Reasons Why Data is "Messy"

| Problem | Description | Solution |
|---------|-------------|----------|
| **String Numbers** | Prices come as strings (`"42150.00"`) | Convert with `float()` |
| **Millisecond Timestamps** | Timestamp in ms (13 digits) | Divide by `/1000` to seconds |
| **Nested Arrays** | Data in nested lists | Access by index `kline[4]` |
| **No Column Names** | No column names, only indexes | Manual mapping |
| **Mixed Types** | int, string, float mixed in same row | Type conversions |
| **Symbol Mismatch** | API: `BTCUSDT`, DB: `bitcoin` | Mapping table |

### Data Cleaning Pipeline

#### Step 1: Fetch Raw Data
```python
# src/scripts/populate_market_data_fast.py
import requests

def fetch_binance_klines(symbol, interval='1d', limit=90):
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(url, params=params)
    return response.json()  # Raw messy data

# Example output: [[1704067200000, "42150.00", ...], ...]
```

#### Step 2: Array → Dictionary Conversion
```python
def parse_kline(kline, coin_id):
    """Convert raw array to meaningful dictionary"""
    return {
        'coin_id': coin_id,
        'timestamp': datetime.utcfromtimestamp(kline[0] / 1000),  # ms → datetime
        'open': float(kline[1]),      # String → Float
        'high': float(kline[2]),      # String → Float
        'low': float(kline[3]),       # String → Float
        'close': float(kline[4]),     # String → Float (main price)
        'volume': float(kline[5]),    # String → Float
    }
```

#### Step 3: Symbol Mapping (ID Matching)
```python
# CoinGecko ID → Binance Symbol mapping
def get_binance_symbol(coin_id, coin_symbol):
    """bitcoin → BTCUSDT conversion"""
    symbol_upper = coin_symbol.upper()
    
    # Try direct match first
    candidates = [
        f"{symbol_upper}USDT",   # BTCUSDT
        f"{symbol_upper}BUSD",   # BTCBUSD  
        f"{symbol_upper}USDC",   # BTCUSDC
    ]
    
    for candidate in candidates:
        if check_symbol_exists(candidate):
            return candidate
    
    return None  # No match found
```

#### Step 4: Timestamp Standardization
```python
# src/app.py - Preparing API response
from datetime import datetime, timezone

def normalize_timestamp(ts):
    """Convert different timestamp formats to UTC ISO 8601"""
    
    # Unix milliseconds
    if isinstance(ts, (int, float)) and ts > 1e12:
        dt = datetime.utcfromtimestamp(ts / 1000)
    
    # Unix seconds
    elif isinstance(ts, (int, float)):
        dt = datetime.utcfromtimestamp(ts)
    
    # String parse
    elif isinstance(ts, str):
        dt = pd.to_datetime(ts, utc=True)
    
    # Datetime object
    elif isinstance(ts, datetime):
        dt = ts
    
    # Add UTC timezone and return ISO format
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat().replace('+00:00', 'Z')
    # Output: "2024-01-01T00:00:00Z"
```

#### Step 5: Missing Value Handling
```python
# src/app.py - NaN/None cleanup
import pandas as pd
import numpy as np

def clean_dataframe(df):
    """Clean missing and invalid values"""
    
    # Convert price column to number (invalid values become NaN)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Drop NaN rows
    df = df.dropna(subset=['price'])
    
    # Remove zero and negative prices
    df = df[df['price'] > 0]
    
    # Sort by timestamp
    df = df.sort_values('timestamp')
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['timestamp'])
    
    return df
```

#### Step 6: JSON Serialization (API Response)
```python
# NaN/Infinity → null conversion (JSON compatibility)
def sanitize_for_json(value):
    """Convert Python values to JSON-safe format"""
    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return None  # Will be null in JSON
    if isinstance(value, (np.int64, np.int32)):
        return int(value)  # numpy int → python int
    if isinstance(value, (np.float64, np.float32)):
        return float(value)  # numpy float → python float
    return value
```

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    BINANCE API (Raw Messy Data)                     │
│  [[1704067200000, "42150.00", "43250.50", "41800.00", "42890.25"]]  │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STEP 1: Parse & Type Convert                     │
│  • kline[0]/1000 → datetime                                         │
│  • float(kline[1]) → 42150.00                                       │
│  • String → Float conversion                                        │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STEP 2: Symbol Mapping                           │
│  • bitcoin → BTC → BTCUSDT                                          │
│  • ethereum → ETH → ETHUSDT                                         │
│  • CoinGecko ID ↔ Binance Symbol                                    │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STEP 3: Clean & Validate                         │
│  • Remove NaN values                                                │
│  • Remove zero/negative prices                                      │
│  • Remove duplicate timestamps                                      │
│  • Sort by timestamp                                                │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STEP 4: Store in MongoDB                         │
│  {                                                                   │
│    "coin_id": "bitcoin",                                            │
│    "timestamp": ISODate("2024-01-01T00:00:00Z"),                    │
│    "open": 42150.00,                                                │
│    "high": 43250.50,                                                │
│    "low": 41800.00,                                                 │
│    "close": 42890.25,                                               │
│    "volume": 1234.56                                                │
│  }                                                                   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     STEP 5: API Response (Clean JSON)                │
│  {                                                                   │
│    "timestamp": "2024-01-01T00:00:00Z",                             │
│    "price": 42890.25,                                               │
│    "open": 42150.00,                                                │
│    "high": 43250.50,                                                │
│    "low": 41800.00                                                  │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
```

### Cleaned Data Statistics

| Metric | Value |
|--------|-------|
| Total Coin Count | 625+ |
| Data Points Per Coin | 90 days |
| Total Records | ~56,000+ |
| Data Source | Binance REST API |
| Data Format | OHLCV (Open, High, Low, Close, Volume) |
| Time Range | Last 90 days |
| Update Frequency | Daily |

---

### Data Science & Analysis (+15 pts)

#### Anomaly Detection Methods
1. **Z-Score Method**: Standard deviation based anomaly detection
2. **IQR Method**: Interquartile Range outlier detection
3. **Rolling Window**: Time-dependent trend-aware anomaly detection
4. **Price Spike Detection**: Sudden price change detection

#### Technical Indicators
- **RSI (Relative Strength Index)**: Momentum indicator (14-day)
- **MACD**: Trend following indicator
- **Bollinger Bands**: Volatility bands
- **SMA/EMA**: Moving averages (7, 14, 30-day)

#### Risk Metrics
- **Volatility**: 7 and 30-day volatility
- **Sharpe Ratio**: Risk-adjusted return
- **Maximum Drawdown**: Drop from peak
- **VaR (Value at Risk)**: Parametric and historic
- **CVaR (Expected Shortfall)**: Tail risk measurement
- **Beta**: Market sensitivity

#### Statistical Analysis
- **Descriptive Statistics**: Mean, Std, Min, Max, Quartiles
- **Skewness & Kurtosis**: Distribution shape analysis
- **Correlation Matrix**: Correlation between coins
- **Returns Analysis**: Daily, cumulative, annualized returns

---

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 6.0+
- Docker & Docker Compose (recommended)

### Running with Docker (Recommended)
```bash
docker-compose up -d
```
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- MongoDB: localhost:27017

### Manual Setup

#### Backend
```bash
pip install -r requirements.txt
python src/app.py
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Endpoints

### Market Data
| Endpoint | Description |
|----------|-------------|
| `GET /api/market-coins` | List of coins with market data |
| `GET /api/market/<coin_id>` | OHLC data for a coin |
| `GET /api/market/indexed` | Indexed price series (for comparison) |

### Technical Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/analysis/<coin_id>` | RSI, MACD, Bollinger, trend analysis |
| `GET /api/correlation?coins=btc,eth` | Correlation matrix |

### Data Science
| Endpoint | Description |
|----------|-------------|
| `GET /api/anomalies/<coin_id>` | Anomaly detection (Z-Score, IQR, Rolling) |
| `GET /api/report/<coin_id>` | Comprehensive scientific report |

---

## 📊 Frontend Pages

1. **Home (/)**: List of all coins with search
2. **Coin Detail (/coin/:id)**: Single coin details and chart
3. **Compare (/compare)**: Two coin comparison (dual Y-axis)
4. **Technical Analysis (/analysis)**: RSI, MACD, Bollinger charts

---

## 🗂️ Project Structure

```
├── src/
│   ├── app.py                 # Flask API server
│   ├── analysis_engine.py     # Technical analysis & anomaly detection
│   ├── db/
│   │   └── database_manager.py # MongoDB operations
│   └── scripts/               # Data population scripts
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.jsx
│   │   │   ├── CoinDetail.jsx
│   │   │   ├── Compare.jsx
│   │   │   └── Analysis.jsx
│   │   └── components/
│   └── package.json
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## 📈 Example API Responses

### Scientific Report
```json
{
  "coin": "Bitcoin",
  "descriptive_statistics": {
    "mean": 87500.50,
    "std": 3200.25,
    "skewness": -0.15,
    "kurtosis": 2.8
  },
  "risk_analysis": {
    "var_historic_95": -4.5,
    "max_drawdown": -32.0,
    "sharpe_ratio": 1.2
  },
  "anomaly_detection": {
    "total_anomalies": 5,
    "anomaly_percentage": 5.5
  }
}
```

---

## 🛠️ Technologies

- **Backend**: Python 3.10, Flask, Flask-CORS, PyMongo
- **Frontend**: React.js, Vite, Tailwind CSS, Recharts
- **Database**: MongoDB 6.0
- **Data Analysis**: Pandas, NumPy
- **Containerization**: Docker, Docker Compose

