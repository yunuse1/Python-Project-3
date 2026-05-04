import pymongo
import pandas as pd
from datetime import datetime, timedelta
import os
import random
import logging
from faker import Faker
from werkzeug.security import generate_password_hash
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
client = pymongo.MongoClient(f"mongodb://{MONGO_HOST}:27017/")
db = client["crypto_project_db"]
users_collection = db["users"]
market_collection = db["market_data"]

# --- ENCRYPTION (ŞİFRELEME) ---
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", b'Jb_rM9_7A_lE3Z-VbY-3qU8wP_W8Y_aP4rN-K_8Q3X4=')
cipher_suite = Fernet(ENCRYPTION_KEY)

def encrypt_sensitive_data(plain_text):
    if not plain_text:
        return ""
    return cipher_suite.encrypt(plain_text.encode()).decode()

def decrypt_sensitive_data(cipher_text):
    if not cipher_text:
        return ""
    try:
        return cipher_suite.decrypt(cipher_text.encode()).decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return "Decryption Failed!"

try:
    market_collection.create_index([("coin_id", 1), ("timestamp", -1)])
    market_collection.create_index("coin_id")
    users_collection.create_index("username", unique=True)
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
        cursor = market_collection.find({"coin_id": coin_id}, {"_id": 0})
        df = pd.DataFrame(list(cursor))

        if df.empty:
            details_col = db["all_coins_details"]
            doc = details_col.find_one({"id": coin_id}, {"symbol": 1, "_id": 0})
            candidates = []
            if doc and doc.get("symbol"):
                sym = doc.get("symbol").upper()
                candidates = [sym + 'USDT', sym + 'BUSD', sym + 'USDC', sym]

            if candidates:
                cursor2 = market_collection.find({"coin_id": {"$in": candidates}}, {"_id": 0})
                df2 = pd.DataFrame(list(cursor2))
                if not df2.empty:
                    df = df2

            if df.empty and doc and doc.get("symbol"):
                regex_pattern = f"^{doc.get('symbol').upper()}"
                cursor3 = market_collection.find({"coin_id": {"$regex": regex_pattern}}, {"_id": 0})
                df3 = pd.DataFrame(list(cursor3))
                if not df3.empty:
                    df = df3

            if df.empty:
                cursor4 = market_collection.find({"coin_id": {"$regex": coin_id, "$options": "i"}}, {"_id": 0})
                df4 = pd.DataFrame(list(cursor4))
                if not df4.empty:
                    df = df4

        if not df.empty and "price" in df.columns:
            df = df[(df["price"].notnull()) & (df["price"] != 0)]
        if not df.empty and "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df = df.sort_values("timestamp")

        return df
    except Exception:
        return pd.DataFrame()

fake = Faker()

def seed_users_into_code(count=25):
    """
    Sistemi test edebilmek için normal User hesaplarını veritabanına ekler.
    (Sadece veritabanı tamamen boşsa çalışır)
    """
    if users_collection.count_documents({}) == 0:
        logger.info(f"Creating {count} secure investors for analysis...")
        
        coins = ["bitcoin", "ethereum", "solana", "ripple", "cardano"]
        fake_users = []

        for _ in range(count):
            user_note = f"Private key for {fake.user_name()}"
            user = {
                "username": fake.user_name(),
                "password_hash": generate_password_hash("UserPass123!"),
                "role": "User",
                "wallet_balance": round(random.uniform(1000, 50000), 2),
                "encrypted_wallet_note": encrypt_sensitive_data(user_note),
                "trades": [
                    {
                        "coin": random.choice(coins),
                        "buy_price": round(random.uniform(10, 65000), 2),
                        "amount": round(random.uniform(0.01, 1.5), 4),
                        "date": datetime.now() - timedelta(days=random.randint(1, 60))
                    } for _ in range(random.randint(1, 3))
                ],
                "last_active": datetime.now() - timedelta(hours=random.randint(1, 720))
            }
            fake_users.append(user)
        
        users_collection.insert_many(fake_users)
        logger.info("Secure initial database ready!")

def initialize_database():
    """Veritabanını kontrol eder ve eksikse admin hesabını zorla oluşturur."""
    
    # --- ADMIN ZORUNLU KONTROLÜ EKLENDİ ---
    admin_check = users_collection.find_one({"username": "admin_zeynep"})
    if not admin_check:
        logger.info("Admin account not found in database. Forcing creation of 'admin_zeynep'...")
        admin_user = {
            "username": "admin_zeynep",
            "password_hash": generate_password_hash("Admin123!"),
            "role": "Admin",
            "wallet_balance": 100000.0,
            "encrypted_wallet_note": encrypt_sensitive_data("Master Admin Wallet Key"),
            "trades": [],
            "last_active": datetime.now()
        }
        users_collection.insert_one(admin_user)
        logger.info("Admin 'admin_zeynep' successfully injected into database!")

    seed_users_into_code(25) 
    logger.info("Database check completed and seeders integrated.")

if __name__ == "__main__":
    try:
        client.server_info()
        logger.info("Connected to MongoDB successfully.")
        initialize_database()
    except Exception as e:
        logger.error(f"Connection failed: {e}")