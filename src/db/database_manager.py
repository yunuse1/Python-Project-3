import pymongo
import pandas as pd
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["crypto_project_db"]
users_collection = db["users"]
market_collection = db["market_data"]

def save_market_data(coin_id, df):
    market_collection.delete_many({"coin_id": coin_id})
    
    df["coin_id"] = coin_id
    data_records = df.to_dict("records")
    
    if data_records:
        market_collection.insert_many(data_records)
        print(f"Data for {coin_id} saved successfully.")
    else:
        print(f"No data found for {coin_id}.")

def get_market_data(coin_id):
    cursor = market_collection.find({"coin_id": coin_id}, {"_id": 0})
    return pd.DataFrame(list(cursor))

def initialize_database():
    users_collection.delete_many({})
    
    dummy_users = [
        {
            "username": "Alice_Smith",
            "wallet_balance": 15000,
            "trades": [
                {"coin": "bitcoin", "buy_price": 42000, "amount": 0.05, "date": datetime(2023, 12, 1)},
                {"coin": "solana", "buy_price": 60, "amount": 10.0, "date": datetime(2024, 1, 15)}
            ]
        },
        {
            "username": "Bob_Jones",
            "wallet_balance": 2000,
            "trades": [
                {"coin": "ethereum", "buy_price": 2800, "amount": 1.0, "date": datetime(2024, 2, 20)}
            ]
        }
    ]
    
    users_collection.insert_many(dummy_users)
    print("Database initialized and dummy users created successfully.")

if __name__ == "__main__":
    try:
        client.server_info()
        print("Connected to MongoDB successfully.")
        initialize_database()
    except Exception as e:
        print(f"Connection failed: {e}")