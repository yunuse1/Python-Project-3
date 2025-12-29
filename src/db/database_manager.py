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
    try:
        # Direkt eşleşme (örn. 'bitcoin' veya 'BTCUSDT' gibi)
        cursor = market_collection.find({"coin_id": coin_id}, {"_id": 0})
        df = pd.DataFrame(list(cursor))

        # Eğer direkt kayıt yoksa, coin'in sembolünü kullanarak fallback aramaları yap
        if df.empty:
            details_col = db["all_coins_details"]
            doc = details_col.find_one({"id": coin_id}, {"symbol": 1, "_id": 0})
            candidates = []
            if doc and doc.get("symbol"):
                sym = doc.get("symbol").upper()
                # Yaygın quote'ları deneyelim
                candidates = [sym + 'USDT', sym + 'BUSD', sym + 'USDC', sym]

            # İlk olarak tam eşleşmelerle ara
            if candidates:
                cursor2 = market_collection.find({"coin_id": {"$in": candidates}}, {"_id": 0})
                df2 = pd.DataFrame(list(cursor2))
                if not df2.empty:
                    df = df2

            # Hâlâ yoksa, sembolle başlayan tüm market kayıtlarını regex ile kontrol et
            if df.empty and doc and doc.get("symbol"):
                regex_pattern = f"^{doc.get('symbol').upper()}"
                cursor3 = market_collection.find({"coin_id": {"$regex": regex_pattern}}, {"_id": 0})
                df3 = pd.DataFrame(list(cursor3))
                if not df3.empty:
                    df = df3

            # Son çare: coin_id'yi küçük/büyük harf duyarsız arama ile dene
            if df.empty:
                cursor4 = market_collection.find({"coin_id": {"$regex": coin_id, "$options": "i"}}, {"_id": 0})
                df4 = pd.DataFrame(list(cursor4))
                if not df4.empty:
                    df = df4

        # Eğer timestamp varsa DateTime'ye çevirip sıralayalım
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

        return df
    except Exception:
        return pd.DataFrame()

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