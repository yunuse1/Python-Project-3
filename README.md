# CryptoAnalyst - Cryptocurrency Analysis Platform

A comprehensive cryptocurrency analysis platform with React.js frontend, Flask backend, MongoDB database, and advanced data science features including anomaly detection, technical analysis, investor portfolio analysis, and scientific reporting.

## 🚀 Features

### Visualization (React.js)
- **Interactive Charts**: Interactive charts with Recharts library
- **Dual Y-Axis Comparison**: Compare two different coins with real prices (indexed base=100)
- **Technical Analysis Dashboard**: RSI, MACD, Bollinger Bands charts
- **Scientific Report Page**: Comprehensive statistical analysis with interactive visualizations
- **Investor Analysis Center**: Portfolio performance analysis and user comparison
- **Seaborn Charts Gallery**: 16+ pre-generated statistical visualizations
- **Responsive Design**: Modern, responsive design with Tailwind CSS

### Visualization (Seaborn)
- **Statistical Plots**: Histogram, KDE, Box Plot, Violin Plot
- **Correlation Heatmap**: Correlation heatmap between 10 cryptocurrencies
- **Pair Plot**: Multivariate analysis with scatter matrix
- **Anomaly Visualization**: Anomaly visualization with Z-Score
- **Time Series Analysis**: Price trends, rolling statistics, daily returns
- **Volatility Comparison**: Risk-Return profile analysis

### Data Science & Analysis 
- **Anomaly Detection**: Z-Score, IQR, Rolling Window methods
- **Technical Indicators**: RSI, MACD, Bollinger Bands, SMA/EMA
- **Risk Metrics**: VaR, CVaR, Sharpe Ratio, Maximum Drawdown, Beta
- **Statistical Analysis**: Descriptive stats, Skewness, Kurtosis
- **Price Forecasting**: Linear Regression based 7-day prediction
- **Portfolio Analysis**: User performance tracking with PnL calculations

---

## 📥 Scraped Messy Web Data 

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

### Data Science & Analysis 

#### Anomaly Detection Methods
1. **Z-Score Method**: Standard deviation based anomaly detection (threshold: 3σ)
2. **IQR Method**: Interquartile Range outlier detection (multiplier: 1.5)
3. **Rolling Window**: Time-dependent trend-aware anomaly detection (window: 20, threshold: 2.5σ)
4. **Price Spike Detection**: Sudden price change detection (threshold: 10%)

#### Technical Indicators
- **RSI (Relative Strength Index)**: Momentum indicator (14-day), overbought/oversold signals
- **MACD**: Moving Average Convergence Divergence with signal line and histogram
- **Bollinger Bands**: Volatility bands (20-day SMA, 2σ)
- **SMA/EMA**: Simple and Exponential Moving Averages (7, 14, 30-day)
- **Trend Detection**: Bullish/Bearish/Neutral classification
- **Support/Resistance Levels**: Pivot points calculation

#### Risk Metrics
- **Volatility**: 7 and 30-day rolling volatility
- **Sharpe Ratio**: Risk-adjusted return (annualized)
- **Maximum Drawdown**: Peak to trough decline measurement
- **VaR (Value at Risk)**: Parametric and Historic (95% confidence)
- **CVaR (Expected Shortfall)**: Conditional VaR / Tail risk
- **Beta**: Market sensitivity coefficient

#### Statistical Analysis
- **Descriptive Statistics**: Mean, Std, Min, Max, Range, Variance, Quartiles
- **Skewness & Kurtosis**: Distribution shape analysis
- **Coefficient of Variation**: Relative variability measure
- **Returns Analysis**: Daily, cumulative, annualized returns, win rate
- **Correlation Matrix**: Multi-coin correlation analysis

#### Investor Portfolio Analysis
- **User Performance Tracking**: PnL (Profit/Loss) calculations per trade
- **Portfolio Breakdown**: Individual coin performance within portfolio
- **Exchange Overview**: Platform-wide statistics
- **User Comparison**: Side-by-side investor performance comparison
- **Exchange King**: Top performer identification

#### Price Forecasting
- **Linear Regression**: 7-day ahead price prediction
- **Trend Extrapolation**: Based on historical price patterns

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

Docker setup includes:
- **Backend** (Flask API): Auto-starts on port 5000
- **Frontend** (React + Vite): Auto-starts on port 5173
- **MongoDB**: Data persistence with volume
- **Init Container**: Automatically populates data and generates Seaborn charts

Access Points:
- Frontend: http://localhost:5173
- Backend API: http://localhost:5000
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

#### Data Population (Manual)
```bash
# Populate market data from Binance API
python src/scripts/populate_market_data_fast.py

# Generate Seaborn visualizations
python analysis/seaborn_analysis.py
```

---

## 🔌 API Endpoints

### Coin Data
| Endpoint | Description |
|----------|-------------|
| `GET /api/all-coins` | Complete coin list with details |
| `GET /api/popular-coins` | Summary data for popular coins |
| `GET /api/market-coins` | List of coins with market data (cached) |
| `GET /api/market/<coin_id>` | OHLCV data for a specific coin |
| `GET /api/market/indexed` | Indexed price series (base=100) for comparison |

### Technical Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/analysis/<coin_id>` | RSI, MACD, Bollinger, trend analysis with 30-day series |
| `GET /api/correlation?coins=btc,eth` | Correlation matrix between coins |
| `GET /api/anomalies/<coin_id>` | Anomaly detection (Z-Score, IQR, Rolling) |
| `GET /api/report/<coin_id>` | Comprehensive scientific report |
| `GET /api/forecast/<coin_id>` | 7-day price prediction |

### Investor Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/users` | All users with trade history |
| `GET /api/user-analysis/<username>` | Individual user portfolio performance |
| `GET /api/exchange-overview` | Platform-wide statistics (king, liquidity, popularity) |

---

## 📊 Frontend Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | **Home** | Searchable list of all coins with prices and 24h change |
| `/coin/:id` | **Coin Detail** | Single coin price chart with OHLC data |
| `/compare` | **Compare** | Dual Y-axis comparison (indexed base=100) with ranking |
| `/analysis` | **Technical Analysis** | Interactive RSI, MACD, Bollinger Bands charts |
| `/report` | **Scientific Report** | Comprehensive statistical analysis with visualizations |
| `/charts` | **Seaborn Gallery** | 16 pre-generated statistical charts (filterable by category) |
| `/investors` | **Investor Analysis** | Portfolio performance, user comparison, exchange overview |

---

## 🗂️ Project Structure

```
├── src/
│   ├── app.py                      # Flask API server (20+ endpoints)
│   ├── analysis_engine.py          # Technical analysis, anomaly detection, portfolio analysis
│   ├── db/
│   │   └── database_manager.py     # MongoDB operations, data fetching, user seeding
│   ├── scripts/
│   │   ├── populate_market_data_fast.py  # Binance API data fetcher
│   │   ├── populate_all_coins.py         # CoinGecko coin list fetcher
│   │   ├── fill_missing_market_data.py   # Gap filling utility
│   │   └── load_timeseries_from_db.py    # Time series export
│   └── util/
│       └── get_coins.py            # Coin symbol mapping utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx                 # Router configuration
│   │   ├── config.js               # API base URL config
│   │   ├── pages/
│   │   │   ├── Home.jsx            # Coin listing with search
│   │   │   ├── CoinDetail.jsx      # Single coin chart
│   │   │   ├── Compare.jsx         # Dual coin comparison
│   │   │   ├── Analysis.jsx        # Technical indicators
│   │   │   ├── Report.jsx          # Scientific analysis report
│   │   │   ├── Charts.jsx          # Seaborn gallery
│   │   │   └── InvestorAnalysis.jsx # Portfolio analysis
│   │   └── components/
│   │       └── Navbar.jsx          # Navigation component
│   └── package.json
├── analysis/
│   ├── seaborn_analysis.py         # Statistical visualization generator
│   ├── plots/                      # Generated chart images (16+)
│   └── *.csv                       # Analysis data exports
├── scripts/
│   ├── docker_init.sh              # Container initialization script
│   └── check_market_db.py          # Database validation
├── docker-compose.yml              # Multi-container orchestration
├── Dockerfile                      # Python backend container
└── requirements.txt                # Python dependencies
```

---

## 📈 Example API Responses

### Scientific Report (`/api/report/bitcoin`)
```json
{
  "coin": "Bitcoin",
  "analysis_period": {
    "start": "2025-10-07T00:00:00",
    "end": "2026-01-05T00:00:00",
    "total_days": 90
  },
  "descriptive_statistics": {
    "mean": 87500.50,
    "std": 3200.25,
    "skewness": -0.15,
    "kurtosis": 2.8,
    "coefficient_of_variation": 3.66
  },
  "returns_analysis": {
    "cumulative_return": 15.5,
    "annualized_return": 72.3,
    "win_rate": 54.2
  },
  "risk_analysis": {
    "var_historic_95": -4.5,
    "cvar_95": -5.8,
    "max_drawdown": -12.0,
    "sharpe_ratio": 1.2
  },
  "anomaly_detection": {
    "total_anomalies": 5,
    "anomaly_percentage": 5.5
  }
}
```

### Investor Analysis (`/api/user-analysis/john_doe`)
```json
{
  "username": "john_doe",
  "wallet_balance": 10000,
  "total_pnl": 2450.50,
  "overall_status": "Profit",
  "portfolio_details": [
    {
      "coin": "bitcoin",
      "amount": 0.5,
      "buy_price": 45000,
      "current_price": 50000,
      "pnl": 2500,
      "pnl_percent": 11.11
    }
  ]
}
```

### Exchange Overview (`/api/exchange-overview`)
```json
{
  "king": {"username": "whale_trader", "pnl_percent": 45.2},
  "total_liquidity": 1500000,
  "most_popular_coin": "BTC",
  "total_investors": 25
}
```

---

## 📊 Seaborn Visualizations

The `Charts` page displays 16 pre-generated statistical charts:

| Category | Charts |
|----------|--------|
| **Bitcoin** | Price Distribution, Returns Analysis, Time Series, Anomaly Detection |
| **Ethereum** | Price Distribution, Returns Analysis, Time Series, Anomaly Detection |
| **Solana** | Price Distribution, Returns Analysis, Time Series, Anomaly Detection |
| **Comparison** | Correlation Heatmap, Volatility Comparison, Returns Pairplot, Summary Dashboard |

Charts are generated by `analysis/seaborn_analysis.py` and served from `/plots/` folder.

---

## 🛠️ Technologies

### Backend
- **Python 3.10**: Core programming language
- **Flask**: REST API framework
- **Flask-CORS**: Cross-origin resource sharing
- **PyMongo**: MongoDB driver
- **Pandas & NumPy**: Data manipulation and analysis
- **scikit-learn**: Linear regression for forecasting
- **SciPy**: Statistical functions (Q-Q plots, distributions)
- **Faker**: Synthetic user data generation

### Frontend
- **React 18**: UI library
- **Vite 7**: Build tool and dev server
- **React Router 6**: Client-side routing
- **Recharts 2**: Interactive charting library
- **Tailwind CSS 3**: Utility-first styling
- **Axios**: HTTP client

### Data Visualization
- **Seaborn**: Statistical visualization
- **Matplotlib**: Chart rendering

### Infrastructure
- **MongoDB 6.0**: NoSQL database
- **Docker & Docker Compose**: Containerization
- **Shared Volumes**: Plot synchronization between containers

---

## 📋 Requirements

### Python Dependencies (`requirements.txt`)
```
flask
Flask-Cors
requests
pandas
numpy
scikit-learn
matplotlib
seaborn
scipy
pymongo
faker
```

### Node.js Dependencies (frontend)
```
react, react-dom, react-router-dom
recharts, axios
tailwindcss, vite
```

---

## 🔄 Data Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Binance API   │────▶│   Flask Backend │────▶│    React App    │
│  (Raw OHLCV)    │     │  (Data Science) │     │  (Visualization)│
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    MongoDB      │
                        │ (Persistence)   │
                        └─────────────────┘
```

---

## 👨‍💻 Author

Cryptocurrency Analysis Platform - Data Science Project

---

## 🧪 Testing

### Test Structure
```
tests/
├── test_api.py          # API endpoint integration tests (13 tests)
├── test_db.py           # Database unit tests (9 tests)
├── test_engine.py       # Analysis engine unit tests (14 tests)
├── test_scripts_all.py  # Script logic unit tests (9 tests)
└── __init__.py
```

### Running Tests

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_api.py -v
pytest tests/test_engine.py -v
```

**Run with coverage report:**
```bash
pytest tests/ -v --cov=src --cov-report=html
```

**Run only failed tests:**
```bash
pytest tests/ --lf
```

### Test Categories

| Category | File | Description |
|----------|------|-------------|
| Integration | `test_api.py` | Flask API endpoints, HTTP responses |
| Unit | `test_db.py` | MongoDB CRUD operations with mongomock |
| Unit | `test_engine.py` | Technical indicators (RSI, MACD, Bollinger) |
| Unit | `test_scripts_all.py` | Data sync and script logic |

### Requirements for Testing
```bash
pip install pytest mongomock pytest-cov
```

