import pymongo
import pandas as pd
from datetime import datetime
import os
import random
import logging
from faker import Faker
from datetime import timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Use 'mongo' for Docker environment, 'localhost' for local development
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")
db = client["crypto_project_db"]
users_collection = db["users"]
market_collection = db["market_data"]

# Create indexes for faster queries (idempotent - safe to run multiple times)
try:
    market_collection.create_index([("coin_id", 1), ("timestamp", -1)])
    market_collection.create_index("coin_id")
except Exception as e:
    logger.warning(f"Index creation warning: {e}")

def save_market_data(coin_id, df):
    market_collection.delete_many({"coin_id": coin_id})
    
    df["coin_id"] = coin_id
    data_records = df.to_dict("records")
    
    if data_records:
        market_collection.insert_many(data_records)
        logger.info(f"Data for {coin_id} saved successfully.")
    else:
        logger.warning(f"No data found for {coin_id}.")

def get_market_data(coin_id):
    try:
        # Direct match (e.g., 'bitcoin' or 'BTCUSDT')
        cursor = market_collection.find({"coin_id": coin_id}, {"_id": 0})
        df = pd.DataFrame(list(cursor))

        # If no direct record, try fallback searches using coin's symbol
        if df.empty:
            details_col = db["all_coins_details"]
            doc = details_col.find_one({"id": coin_id}, {"symbol": 1, "_id": 0})
            candidates = []
            if doc and doc.get("symbol"):
                sym = doc.get("symbol").upper()
                # Try common quote pairs
                candidates = [sym + 'USDT', sym + 'BUSD', sym + 'USDC', sym]

            # First try exact matches
            if candidates:
                cursor2 = market_collection.find({"coin_id": {"$in": candidates}}, {"_id": 0})
                df2 = pd.DataFrame(list(cursor2))
                if not df2.empty:
                    df = df2

            # Still empty, check with regex for symbol prefix
            if df.empty and doc and doc.get("symbol"):
                regex_pattern = f"^{doc.get('symbol').upper()}"
                cursor3 = market_collection.find({"coin_id": {"$regex": regex_pattern}}, {"_id": 0})
                df3 = pd.DataFrame(list(cursor3))
                if not df3.empty:
                    df = df3

            # Last resort: case-insensitive search with coin_id
            if df.empty:
                cursor4 = market_collection.find({"coin_id": {"$regex": coin_id, "$options": "i"}}, {"_id": 0})
                df4 = pd.DataFrame(list(cursor4))
                if not df4.empty:
                    df = df4

        # Filter out rows with price 0 or None
        if not df.empty and "price" in df.columns:
            df = df[(df["price"].notnull()) & (df["price"] != 0)]
        # Convert timestamp to DateTime and sort if exists
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

        return df
    except Exception:
        return pd.DataFrame()

fake = Faker()

def seed_users_into_code(count=25):
    """
    Inserts dynamic user data into MongoDB for analysis engine testing.
    """
    if users_collection.count_documents({}) == 0:
        logger.info(f"Creating {count} fake investors for analysis...")
        
        coins = ["bitcoin", "ethereum", "solana", "ripple", "cardano"]
        fake_users = []
        
        for _ in range(count):
            user = {
                "username": fake.user_name(),
                "wallet_balance": round(random.uniform(1000, 50000), 2),
                "trades": [
                    {
                        "coin": random.choice(coins),
                        "buy_price": round(random.uniform(10, 65000), 2),  # Critical for analysis
                        "amount": round(random.uniform(0.01, 1.5), 4),
                        "date": datetime.now() - timedelta(days=random.randint(1, 60))
                    } for _ in range(random.randint(1, 3))
                ],
                "last_active": datetime.now() - timedelta(hours=random.randint(1, 720))
            }
            fake_users.append(user)
        
        users_collection.insert_many(fake_users)
        logger.info("Dynamic user data ready for analysis!")

def initialize_database():
    """Checks database and seeds dynamic data."""
    seed_users_into_code(25) 
    logger.info("Database check completed and seeders integrated.")

if __name__ == "__main__":
    try:
        client.server_info()
        logger.info("Connected to MongoDB successfully.")
        initialize_database()
    except Exception as e:
        logger.error(f"Connection failed: {e}")