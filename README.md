# CryptoAnalyst - Cryptocurrency Analysis Platform

A comprehensive cryptocurrency analysis platform with React.js frontend, Flask backend, MongoDB database, and advanced data science features including anomaly detection and technical analysis.

## 🚀 Features

### Visualization (+15 pts - React.js)
- **Interactive Charts**: Recharts library ile interaktif grafikler
- **Dual Y-Axis Comparison**: İki farklı coin'i gerçek fiyatlarla karşılaştırma
- **Technical Analysis Dashboard**: RSI, MACD, Bollinger Bands grafikleri
- **Responsive Design**: Tailwind CSS ile modern, responsive tasarım

### Visualization (+5 pts - Seaborn)
- **Statistical Plots**: Histogram, KDE, Box Plot, Violin Plot
- **Correlation Heatmap**: Coinler arası korelasyon ısı haritası
- **Pair Plot**: Scatter matrix ile çoklu değişken analizi
- **Anomaly Visualization**: Z-Score ile anomali görselleştirme

---

## 📥 Scraped Messy Web Data (+10 pts)

### Veri Kaynağı: Binance API

Projede kullanılan veriler **Binance Cryptocurrency Exchange** API'sinden çekilmiştir. Bu bir REST API olup, ham (messy) formatta JSON verisi döndürür.

#### API Endpoint
```
https://api.binance.com/api/v3/klines?symbol={SYMBOL}&interval=1d&limit=90
```

#### Ham Veri Formatı (Messy Data)
Binance API'den gelen ham veri, **nested array** formatındadır ve her bir eleman farklı veri tiplerini içerir:

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

### Verinin "Messy" Olma Sebepleri

| Problem | Açıklama | Çözüm |
|---------|----------|-------|
| **String Numbers** | Fiyatlar string olarak geliyor (`"42150.00"`) | `float()` ile dönüştürme |
| **Millisecond Timestamps** | Zaman damgası ms cinsinden (13 haneli) | `/1000` ile saniyeye çevirme |
| **Nested Arrays** | Veri iç içe listeler halinde | Index ile erişim `kline[4]` |
| **No Column Names** | Sütun isimleri yok, sadece indexler | Manuel mapping |
| **Mixed Types** | Aynı satırda int, string, float karışık | Tip dönüşümleri |
| **Symbol Mismatch** | API'de `BTCUSDT`, DB'de `bitcoin` | Mapping tablosu |

### Data Cleaning Pipeline (Veri Temizleme Süreci)

#### Adım 1: Ham Veri Çekme
```python
# src/scripts/populate_market_data_fast.py
import requests

def fetch_binance_klines(symbol, interval='1d', limit=90):
    url = f"https://api.binance.com/api/v3/klines"
    params = {'symbol': symbol, 'interval': interval, 'limit': limit}
    response = requests.get(url, params=params)
    return response.json()  # Raw messy data

# Örnek çıktı: [[1704067200000, "42150.00", ...], ...]
```

#### Adım 2: Array → Dictionary Dönüşümü
```python
def parse_kline(kline, coin_id):
    """Ham array'i anlamlı dictionary'e çevir"""
    return {
        'coin_id': coin_id,
        'timestamp': datetime.utcfromtimestamp(kline[0] / 1000),  # ms → datetime
        'open': float(kline[1]),      # String → Float
        'high': float(kline[2]),      # String → Float
        'low': float(kline[3]),       # String → Float
        'close': float(kline[4]),     # String → Float (ana fiyat)
        'volume': float(kline[5]),    # String → Float
    }
```

#### Adım 3: Symbol Mapping (ID Eşleştirme)
```python
# CoinGecko ID → Binance Symbol eşleştirme
def get_binance_symbol(coin_id, coin_symbol):
    """bitcoin → BTCUSDT dönüşümü"""
    symbol_upper = coin_symbol.upper()
    
    # Önce doğrudan dene
    candidates = [
        f"{symbol_upper}USDT",   # BTCUSDT
        f"{symbol_upper}BUSD",   # BTCBUSD  
        f"{symbol_upper}USDC",   # BTCUSDC
    ]
    
    for candidate in candidates:
        if check_symbol_exists(candidate):
            return candidate
    
    return None  # Eşleşme bulunamadı
```

#### Adım 4: Timestamp Standardization
```python
# src/app.py - API response hazırlama
from datetime import datetime, timezone

def normalize_timestamp(ts):
    """Farklı formatlardaki timestamp'leri UTC ISO 8601'e çevir"""
    
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
    
    # UTC timezone ekle ve ISO format döndür
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    return dt.isoformat().replace('+00:00', 'Z')
    # Çıktı: "2024-01-01T00:00:00Z"
```

#### Adım 5: Missing Value Handling
```python
# src/app.py - NaN/None temizleme
import pandas as pd
import numpy as np

def clean_dataframe(df):
    """Eksik ve hatalı değerleri temizle"""
    
    # Price sütununu sayıya çevir (hatalı değerler NaN olur)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    
    # NaN satırları sil
    df = df.dropna(subset=['price'])
    
    # Sıfır ve negatif fiyatları sil
    df = df[df['price'] > 0]
    
    # Timestamp'e göre sırala
    df = df.sort_values('timestamp')
    
    # Duplicate'ları sil
    df = df.drop_duplicates(subset=['timestamp'])
    
    return df
```

#### Adım 6: JSON Serialization (API Response)
```python
# NaN/Infinity → null dönüşümü (JSON uyumluluğu)
def sanitize_for_json(value):
    """Python değerlerini JSON-safe hale getir"""
    if isinstance(value, float):
        if np.isnan(value) or np.isinf(value):
            return None  # JSON'da null olacak
    if isinstance(value, (np.int64, np.int32)):
        return int(value)  # numpy int → python int
    if isinstance(value, (np.float64, np.float32)):
        return float(value)  # numpy float → python float
    return value
```

### Veri Akış Şeması

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
│  • String → Float dönüşümü                                          │
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
│  • NaN değerleri sil                                                │
│  • Sıfır/negatif fiyatları sil                                      │
│  • Duplicate timestamp'leri sil                                     │
│  • Timestamp'e göre sırala                                          │
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

### Temizlenen Veri İstatistikleri

| Metrik | Değer |
|--------|-------|
| Toplam Coin Sayısı | 625+ |
| Her Coin İçin Veri Noktası | 90 gün |
| Toplam Kayıt | ~56,000+ |
| Veri Kaynağı | Binance REST API |
| Veri Formatı | OHLCV (Open, High, Low, Close, Volume) |
| Zaman Aralığı | Son 90 gün |
| Güncelleme Sıklığı | Günlük |

---

### Data Science & Analysis (+15 pts)

#### Anomaly Detection Methods
1. **Z-Score Method**: Standart sapma tabanlı anomali tespiti
2. **IQR Method**: Interquartile Range ile outlier detection
3. **Rolling Window**: Zamana bağlı trend-aware anomali tespiti
4. **Price Spike Detection**: Ani fiyat değişimlerini tespit etme

#### Technical Indicators
- **RSI (Relative Strength Index)**: Momentum göstergesi (14 günlük)
- **MACD**: Trend takip göstergesi
- **Bollinger Bands**: Volatilite bantları
- **SMA/EMA**: Hareketli ortalamalar (7, 14, 30 günlük)

#### Risk Metrics
- **Volatility**: 7 ve 30 günlük volatilite
- **Sharpe Ratio**: Risk ayarlı getiri
- **Maximum Drawdown**: En yüksek noktadan düşüş
- **VaR (Value at Risk)**: Parametrik ve historik
- **CVaR (Expected Shortfall)**: Tail risk ölçümü
- **Beta**: Piyasa hassasiyeti

#### Statistical Analysis
- **Descriptive Statistics**: Mean, Std, Min, Max, Quartiles
- **Skewness & Kurtosis**: Dağılım şekli analizi
- **Correlation Matrix**: Coinler arası korelasyon
- **Returns Analysis**: Günlük, kümülatif, yıllık getiri

---

## 📦 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB 6.0+
- Docker & Docker Compose (önerilen)

### Docker ile Çalıştırma (Önerilen)
```bash
docker-compose up -d
```
- Frontend: http://localhost:5173
- Backend: http://localhost:5000
- MongoDB: localhost:27017

### Manuel Kurulum

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
| `GET /api/market-coins` | Market verisi olan coinlerin listesi |
| `GET /api/market/<coin_id>` | Coin için OHLC verileri |
| `GET /api/market/indexed` | İndeksli fiyat serisi (karşılaştırma için) |

### Technical Analysis
| Endpoint | Description |
|----------|-------------|
| `GET /api/analysis/<coin_id>` | RSI, MACD, Bollinger, trend analizi |
| `GET /api/correlation?coins=btc,eth` | Korelasyon matrisi |

### Data Science
| Endpoint | Description |
|----------|-------------|
| `GET /api/anomalies/<coin_id>` | Anomali tespiti (Z-Score, IQR, Rolling) |
| `GET /api/report/<coin_id>` | Kapsamlı bilimsel rapor |

---

## 📊 Frontend Pages

1. **Home (/)**: Tüm coinlerin listesi ve arama
2. **Coin Detail (/coin/:id)**: Tek coin detayı ve grafiği
3. **Compare (/compare)**: İki coin karşılaştırma (dual Y-axis)
4. **Technical Analysis (/analysis)**: RSI, MACD, Bollinger grafikleri

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

