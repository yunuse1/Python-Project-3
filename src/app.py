
from flask import Flask, jsonify
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import pandas as pd
from flask_cors import CORS
from db import database_manager as db

app = Flask(__name__)
# Enable CORS (Cross-Origin Resource Sharing)
CORS(app)

# Tüm coinlerin detaylı verisini dönen endpoint
@app.route('/api/all-coins', methods=['GET'])
def get_all_coins():
    """
    Tüm coinlerin detaylı verisini MongoDB'den döner.
    """
    try:
        client = db.client
        collection = client["crypto_project_db"]["all_coins_details"]
        coins = list(collection.find({}, {"_id": 0}))
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Initialize the Flask application

@app.route('/api/popular-coins', methods=['GET'])
def get_popular_coins():
    """
    Popüler coinlerin özet verisini MongoDB'den döner.
    """
    try:
        client = db.client
        collection = client["crypto_project_db"]["popular_coins"]
        coins = list(collection.find({}, {"_id": 0}))
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    """
    Health check route to verify the API is running.
    """
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
    Returns list of coin detail docs that have market_data entries.
    This is used to power the frontend market page so coins without market data are hidden.
    """
    try:
        client = db.client
        market_coll = client["crypto_project_db"]["market_data"]
        details_coll = client["crypto_project_db"]["all_coins_details"]

        # Distinct coin_ids present in market_data (could be 'BTCUSDT' or 'bitcoin')
        market_ids = set(market_coll.distinct('coin_id'))

        # Fetch all coin details and filter in Python for flexible matching
        all_details = list(details_coll.find({}, {"_id": 0}))
        result = []
        for d in all_details:
            coin_id = d.get('id')
            symbol = (d.get('symbol') or '').upper()

            # direct id match or symbol-based matches
            candidates = {str(coin_id), symbol, symbol + 'USDT', symbol + 'BUSD', symbol + 'USDC'}
            if market_ids.intersection(candidates):
                result.append(d)

        return result
    except Exception:
        return []


@app.route('/api/market-coins', methods=['GET'])
def get_market_coins():
    """Endpoint that returns only coins which have market data available."""
    try:
        coins = fetch_market_coins_list()
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the application on port 5000 in debug mode
    app.run(debug=True, port=5000)