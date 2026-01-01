import pymongo
import pandas as pd
from datetime import datetime
import os
import random
from faker import Faker
from datetime import timedelta

# Docker ortamında 'mongo', lokalde 'localhost' kullanılır
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
    print(f"Index creation warning: {e}")

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

        # Fiyatı 0 veya None olan satırları filtrele
        if not df.empty and "price" in df.columns:
            df = df[(df["price"].notnull()) & (df["price"] != 0)]
        # Eğer timestamp varsa DateTime'ye çevirip sıralayalım
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

        return df
    except Exception:
        return pd.DataFrame()

fake = Faker()

def seed_users_into_code(count=25):
    """
    Analiz motorunun çalışması için gereken dinamik kullanıcı verisini 
    MongoDB'ye entegre eder.
    """
    if users_collection.count_documents({}) == 0:
        print(f"📊 Analiz için {count} adet sahte yatırımcı oluşturuluyor...")
        
        coins = ["bitcoin", "ethereum", "solana", "ripple", "cardano"]
        fake_users = []
        
        for _ in range(count):
            user = {
                "username": fake.user_name(),
                "wallet_balance": round(random.uniform(1000, 50000), 2),
                "trades": [
                    {
                        "coin": random.choice(coins),
                        "buy_price": round(random.uniform(10, 65000), 2), # Analiz için kritik
                        "amount": round(random.uniform(0.01, 1.5), 4),
                        "date": datetime.now() - timedelta(days=random.randint(1, 60))
                    } for _ in range(random.randint(1, 3))
                ],
                "last_active": datetime.now() - timedelta(hours=random.randint(1, 720))
            }
            fake_users.append(user)
        
        users_collection.insert_many(fake_users)
        print("✅ Dinamik kullanıcı verileri analize hazır!")

def initialize_database():
    """Veritabanını kontrol eder ve dinamik verileri basar."""
    # users_collection.delete_many({}) # Her seferinde sıfırlamak istersen burayı aç
    seed_users_into_code(25) 
    print("🚀 Database check completed and seeders integrated.")

if __name__ == "__main__":
    try:
        client.server_info()
        print("Connected to MongoDB successfully.")
        initialize_database()
    except Exception as e:
        print(f"Connection failed: {e}")