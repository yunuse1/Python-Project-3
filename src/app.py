from flask import Flask, jsonify, request
import traceback
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import pandas as pd
import numpy as np
from flask_cors import CORS
from db import database_manager as db
from analysis_engine import CryptoAnalysisEngine

app = Flask(__name__)
CORS(app)

# Analysis engine instance
analysis_engine = CryptoAnalysisEngine()


@app.route('/api/all-coins', methods=['GET'])
def get_all_coins():
    """Tüm coinlerin detaylı verisini MongoDB'den döner."""
    try:
        client = db.client
        collection = client["crypto_project_db"]["all_coins_details"]
        coins = list(collection.find({}, {"_id": 0}))
        return jsonify(coins)
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e), "traceback": tb}), 500


@app.route('/api/popular-coins', methods=['GET'])
def get_popular_coins():
    """Popüler coinlerin özet verisini MongoDB'den döner."""
    try:
        client = db.client
        collection = client["crypto_project_db"]["popular_coins"]
        coins = list(collection.find({}, {"_id": 0}))
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def home():
    """Health check route."""
    return "Crypto Analysis API is running! 🚀"

@app.route('/api/market/<coin_id>', methods=['GET'])
def get_coin_data(coin_id):
    """
    Fetches historical market data for a specific coin from MongoDB.
    Args:
        coin_id (str): The ID of the cryptocurrency (e.g., 'bitcoin').
    Returns:
        JSON: List of price data records.
    """
    try:
        # Fetch data using the function from database_manager
        df = db.get_market_data(coin_id)
        
        # Check if data exists
        if df.empty:
            return jsonify({"error": "Data not found", "data": []}), 404
            
        # Convert Pandas DataFrame to a list of dictionaries (JSON compatible)
        result = df.to_dict(orient="records")

        # Sanitize values: convert NaN/NaT to None (JSON null) and
        # normalize timestamps to ISO 8601 (UTC, ending with Z).
        sanitized = []
        for rec in result:
            out = {}
            for k, v in rec.items():
                # pandas/numpy NA handling
                try:
                    if pd.isna(v):
                        out[k] = None
                        continue
                except Exception:
                    pass

                # Normalize timestamp formats (datetime or RFC-2822 strings)
                if k == 'timestamp':
                    if isinstance(v, datetime):
                        dt = v
                        if dt.tzinfo is None:
                            out[k] = dt.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
                        else:
                            out[k] = dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
                        continue
                    if isinstance(v, str):
                        try:
                            dt = parsedate_to_datetime(v)
                            if dt.tzinfo is None:
                                out[k] = dt.replace(tzinfo=timezone.utc).isoformat().replace('+00:00', 'Z')
                            else:
                                out[k] = dt.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
                            continue
                        except Exception:
                            # keep original string if parsing fails
                            out[k] = v
                            continue

                out[k] = v

            sanitized.append(out)

        return jsonify(sanitized)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """
    Fetches all user data and their trade history from MongoDB.
    Returns:
        JSON: List of users and their portfolios.
    """
    try:
        # Fetch all documents from the users collection
        # {"_id": 0} excludes the MongoDB internal ID field to prevent JSON errors
        users = list(db.users_collection.find({}, {"_id": 0}))
        
        return jsonify(users)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def fetch_market_coins_list():
    """
    Returns list of coins that have market_data entries.
    This is used to power the frontend market page.
    """
    try:
        client = db.client
        market_coll = client["crypto_project_db"]["market_data"]
        
        # Get distinct coin_ids from market_data
        market_ids = market_coll.distinct('coin_id')
        
        # Filter out exchange symbols (like BTCUSDT) and keep only readable ids (like bitcoin)
        result = []
        seen = set()
        for coin_id in market_ids:
            # Skip if it looks like a trading pair (ends with USDT, BUSD, etc.)
            if coin_id and not coin_id.endswith(('USDT', 'BUSD', 'USDC', 'BTC', 'ETH')):
                if coin_id not in seen:
                    seen.add(coin_id)
                    # Get the latest price for this coin
                    latest = market_coll.find_one(
                        {'coin_id': coin_id},
                        sort=[('timestamp', -1)],
                        projection={'_id': 0, 'close': 1, 'c': 1, 'price': 1}
                    )
                    current_price = None
                    if latest:
                        current_price = latest.get('close') or latest.get('c') or latest.get('price')
                    
                    result.append({
                        'id': coin_id,
                        'name': coin_id.replace('-', ' ').title(),
                        'symbol': coin_id[:3].upper() if len(coin_id) >= 3 else coin_id.upper(),
                        'current_price': current_price
                    })
        
        # Sort by name
        result.sort(key=lambda x: x['name'])
        return result
    except Exception as e:
        print(f"fetch_market_coins_list error: {e}")
        return []


@app.route('/api/market-coins', methods=['GET'])
def get_market_coins():
    """Endpoint that returns only coins which have market data available."""
    try:
        coins = fetch_market_coins_list()
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/market/indexed', methods=['GET'])
def get_indexed_series():
    """
    Returns indexed series (base = 100 at base_date) and percent-change summaries for given coins.
    Query params:
      - coins: comma-separated list of coin ids (e.g. bitcoin,ethereum)
      - base_date: optional ISO or RFC date string; if omitted defaults to 30 days before latest available point per coin
    """
    try:
        coins_param = request.args.get('coins', '')
        if not coins_param:
            return jsonify({"error": "Missing 'coins' query parameter"}), 400

        coins = [c.strip() for c in coins_param.split(',') if c.strip()]
        base_date_raw = request.args.get('base_date')

        results = {}
        ranking = []

        for coin in coins:
            df = db.get_market_data(coin)

                # Defensive: accept alternative price column names and coerce types
            if df.empty:
                results[coin] = {"series": [], "summary": None, "debug": {"raw_count": 0, "valid_count": 0}}
                continue

            df = df.copy()

            # normalize timestamp column (make tz-aware UTC)
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce', utc=True)
            else:
                df['timestamp'] = pd.NaT

            # normalize price column: accept 'price', 'close', 'c'
            if 'price' not in df.columns:
                if 'close' in df.columns:
                    df['price'] = df['close']
                elif 'c' in df.columns:
                    df['price'] = df['c']

            # coerce price to numeric
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce')

            df = df.sort_values('timestamp')

            # determine base_date for this coin
            if base_date_raw:
                try:
                    bd = parsedate_to_datetime(base_date_raw)
                    bd = bd.astimezone(timezone.utc) if bd.tzinfo else bd.replace(tzinfo=timezone.utc)
                except Exception:
                    # fallback: try pandas parser
                    bd = pd.to_datetime(base_date_raw, utc=True)
            else:
                # default base = 30 days before latest available
                latest = df['timestamp'].max()
                bd = latest - pd.Timedelta(days=30)

            # find the first price at or after base_date; fallback to earliest
            df_valid = df.dropna(subset=['price'])
            raw_count = len(df)
            valid_count = len(df_valid)
            if df_valid.empty:
                results[coin] = {"series": [], "summary": None, "debug": {"raw_count": raw_count, "valid_count": valid_count}}
                continue

            base_row = df_valid[df_valid['timestamp'] >= bd]
            if not base_row.empty:
                base_price = float(base_row.iloc[0]['price'])
                base_ts = pd.to_datetime(base_row.iloc[0]['timestamp'], utc=True)
            else:
                base_price = float(df_valid.iloc[0]['price'])
                base_ts = pd.to_datetime(df_valid.iloc[0]['timestamp'], utc=True)

            # compute indexed series
            series = []
            for _, row in df_valid.iterrows():
                try:
                    price = float(row['price'])
                except Exception:
                    continue
                indexed = price / base_price * 100.0
                ts = row['timestamp']
                ts_iso = pd.to_datetime(ts, utc=True).isoformat().replace('+00:00', 'Z')
                series.append({"timestamp": ts_iso, "indexed": indexed, "price": price})

            latest_price = float(df_valid.iloc[-1]['price'])
            pct_change = (latest_price / base_price - 1.0) * 100.0

            summary = {
                "base_date": pd.to_datetime(base_ts, utc=True).isoformat().replace('+00:00', 'Z'),
                "base_price": base_price,
                "latest_price": latest_price,
                "percent_change": pct_change
            }

            results[coin] = {"series": series, "summary": summary, "debug": {"raw_count": raw_count, "valid_count": valid_count}}
            ranking.append({"coin": coin, "percent_change": pct_change})

        # sort ranking descending
        ranking = sorted(ranking, key=lambda x: x['percent_change'], reverse=True)

        return jsonify({"coins": results, "ranking": ranking})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/analysis/<coin_id>', methods=['GET'])
def get_coin_analysis(coin_id):
    """
    Bir coin için detaylı teknik analiz ve risk metrikleri döner.
    RSI, MACD, Bollinger Bands, Volatilite, Sharpe Ratio, Trend analizi
    """
    try:
        df = db.get_market_data(coin_id)
        
        if df.empty:
            return jsonify({"error": "Data not found"}), 404
        
        # Normalize price column
        if 'price' not in df.columns:
            if 'close' in df.columns:
                df['price'] = df['close']
            elif 'c' in df.columns:
                df['price'] = df['c']
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        if len(df) < 30:
            return jsonify({"error": "Insufficient data for analysis", "data_points": len(df)}), 400
        
        # Full analysis
        analysis = analysis_engine.get_full_analysis(df, column='price')
        
        # DataFrame'i çıkar (JSON'a çevrilemez)
        analysis_df = analysis.pop('dataframe')
        
        # NaN değerleri None'a çevir
        def clean_value(v):
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                return None
            return v
        
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            else:
                return clean_value(d)
        
        analysis = clean_dict(analysis)
        
        # Son 30 günlük veri serisi (grafik için)
        recent_df = analysis_df.tail(30).copy()
        series_data = []
        for _, row in recent_df.iterrows():
            ts = row.get('timestamp')
            if pd.notna(ts):
                if isinstance(ts, datetime):
                    ts_str = ts.isoformat()
                else:
                    ts_str = str(ts)
            else:
                continue
            
            series_data.append({
                'timestamp': ts_str,
                'price': clean_value(row.get('price')),
                'sma_7': clean_value(row.get('sma_7')),
                'sma_30': clean_value(row.get('sma_30')),
                'rsi': clean_value(row.get('rsi')),
                'bb_upper': clean_value(row.get('bb_upper')),
                'bb_middle': clean_value(row.get('bb_middle')),
                'bb_lower': clean_value(row.get('bb_lower')),
                'macd': clean_value(row.get('macd')),
                'macd_signal': clean_value(row.get('macd_signal')),
                'macd_histogram': clean_value(row.get('macd_histogram'))
            })
        
        analysis['series'] = series_data
        analysis['coin_id'] = coin_id
        
        return jsonify(analysis)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e), "traceback": tb}), 500


@app.route('/api/correlation', methods=['GET'])
def get_correlation():
    """
    Birden fazla coin için korelasyon matrisi döner.
    Query params: coins=bitcoin,ethereum,solana
    """
    try:
        coins_param = request.args.get('coins', 'bitcoin,ethereum,solana')
        coins = [c.strip() for c in coins_param.split(',') if c.strip()]
        
        if len(coins) < 2:
            return jsonify({"error": "At least 2 coins required"}), 400
        
        coin_dfs = {}
        for coin in coins:
            df = db.get_market_data(coin)
            if not df.empty:
                if 'price' not in df.columns:
                    if 'close' in df.columns:
                        df['price'] = df['close']
                    elif 'c' in df.columns:
                        df['price'] = df['c']
                df['price'] = pd.to_numeric(df['price'], errors='coerce')
                coin_dfs[coin] = df
        
        if len(coin_dfs) < 2:
            return jsonify({"error": "Not enough coins with data"}), 400
        
        correlation = analysis_engine.calculate_correlation_matrix(coin_dfs)
        
        # NaN değerleri temizle
        def clean_corr(d):
            if isinstance(d, dict):
                return {k: clean_corr(v) for k, v in d.items()}
            elif isinstance(d, float) and (np.isnan(d) or np.isinf(d)):
                return None
            return d
        
        return jsonify({
            "coins": list(coin_dfs.keys()),
            "correlation_matrix": clean_corr(correlation)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/anomalies/<coin_id>', methods=['GET'])
def get_coin_anomalies(coin_id):
    """
    Coin için anomali tespiti ve özet istatistikleri döner.
    Z-Score, IQR ve Rolling window metodları kullanılır.
    """
    try:
        df = db.get_market_data(coin_id)
        
        if df.empty:
            return jsonify({"error": "Data not found"}), 404
        
        # Normalize price column
        if 'price' not in df.columns:
            if 'close' in df.columns:
                df['price'] = df['close']
            elif 'c' in df.columns:
                df['price'] = df['c']
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        if len(df) < 10:
            return jsonify({"error": "Insufficient data for anomaly detection"}), 400
        
        # Anomali analizi
        anomaly_result = analysis_engine.get_anomaly_summary(df, column='price')
        
        # DataFrame'i çıkar
        anomaly_df = anomaly_result.pop('dataframe')
        
        # NaN değerleri temizle
        def clean_value(v):
            if isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
                return None
            if isinstance(v, (np.int64, np.int32)):
                return int(v)
            if isinstance(v, (np.float64, np.float32)):
                return float(v)
            return v
        
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            else:
                return clean_value(d)
        
        anomaly_result = clean_dict(anomaly_result)
        
        # Son 30 günlük anomali verisi (grafik için)
        recent_df = anomaly_df.tail(30).copy()
        series_data = []
        for _, row in recent_df.iterrows():
            ts = row.get('timestamp')
            if pd.notna(ts):
                ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
            else:
                continue
            
            series_data.append({
                'timestamp': ts_str,
                'price': clean_value(row.get('price')),
                'zscore': clean_value(row.get('zscore')),
                'rolling_zscore': clean_value(row.get('rolling_zscore')),
                'pct_change': clean_value(row.get('pct_change')),
                'is_anomaly': bool(row.get('is_anomaly_any', False)),
                'is_spike': bool(row.get('is_spike', False))
            })
        
        anomaly_result['series'] = series_data
        anomaly_result['coin_id'] = coin_id
        
        return jsonify(anomaly_result)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e)}), 500


@app.route('/api/report/<coin_id>', methods=['GET'])
def get_scientific_report(coin_id):
    """
    Coin için kapsamlı bilimsel rapor döner.
    Descriptive statistics, returns analysis, risk analysis, anomaly detection
    """
    try:
        df = db.get_market_data(coin_id)
        
        if df.empty:
            return jsonify({"error": "Data not found"}), 404
        
        # Normalize price column
        if 'price' not in df.columns:
            if 'close' in df.columns:
                df['price'] = df['close']
            elif 'c' in df.columns:
                df['price'] = df['c']
        
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df = df.dropna(subset=['price'])
        
        if len(df) < 30:
            return jsonify({"error": "Insufficient data for scientific report"}), 400
        
        # Coin adını al
        client = db.client
        details_coll = client["crypto_project_db"]["all_coins_details"]
        coin_info = details_coll.find_one({"id": coin_id}, {"_id": 0, "name": 1})
        coin_name = coin_info.get('name', coin_id) if coin_info else coin_id
        
        # Bilimsel rapor oluştur
        report = analysis_engine.generate_scientific_report(df, column='price', coin_name=coin_name)
        
        # NaN değerleri temizle
        def clean_value(v):
            if isinstance(v, (float, np.floating)) and (np.isnan(v) or np.isinf(v)):
                return None
            if isinstance(v, (np.int64, np.int32)):
                return int(v)
            if isinstance(v, (np.float64, np.float32)):
                return float(v)
            return v
        
        def clean_dict(d):
            if isinstance(d, dict):
                return {k: clean_dict(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [clean_dict(v) for v in d]
            else:
                return clean_value(d)
        
        report = clean_dict(report)
        report['coin_id'] = coin_id
        
        return jsonify(report)
        
    except Exception as e:
        tb = traceback.format_exc()
        print(tb)
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Run the application on port 5000 in debug mode
    # host='0.0.0.0' is required for Docker to expose the port externally
    app.run(debug=True, host='0.0.0.0', port=5000)