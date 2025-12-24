from flask import Flask, jsonify
from flask_cors import CORS
from db import database_manager as db

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing)
# This allows our React frontend to communicate with this Python backend
CORS(app)

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
        return jsonify(result)
        
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

if __name__ == '__main__':
    # Run the application on port 5000 in debug mode
    app.run(debug=True, port=5000)