# Tüm coinlerin detaylı verisini çekip kaydet
def fetch_and_store_all_coin_details():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["all_coins_details"]
    coins = fetch_all_coins()
    print(f"Detayları çekilecek coin sayısı: {len(coins)}")
    for idx, coin in enumerate(coins):
        coin_id = coin["id"]
        detail = fetch_coin_detail(coin_id)
        if detail:
            coin_data = {
                "id": detail.get("id"),
                "symbol": detail.get("symbol"),
                "name": detail.get("name"),
                "image": detail.get("image", {}).get("large"),
                "current_price": detail.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": detail.get("market_data", {}).get("market_cap", {}).get("usd"),
                "price_change_percentage_24h": detail.get("market_data", {}).get("price_change_percentage_24h"),
                "last_updated": datetime.now()
            }
            collection.update_one({"id": coin_id}, {"$set": coin_data}, upsert=True)
            print(f"[{idx+1}/{len(coins)}] {coin_id} kaydedildi.")
        else:
            print(f"[{idx+1}/{len(coins)}] {coin_id} verisi alınamadı.")
        time.sleep(1)  # Rate limit için bekle
import requests
import time
import pymongo
from datetime import datetime

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "crypto_project_db"
COLLECTION_NAME = "all_coins"

def fetch_all_coins():
    url = "https://api.coingecko.com/api/v3/coins/list"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("CoinGecko'dan coin listesi alınamadı.")
        return []

def fetch_coin_detail(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def upsert_coins_to_db(coins):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    for coin in coins:
        coin["last_updated"] = datetime.now()
        collection.update_one({"id": coin["id"]}, {"$set": coin}, upsert=True)
    print(f"{len(coins)} coin güncellendi/eklendi.")

# Popüler coinlerin detaylı verisi için ayrı koleksiyon
POPULAR_COINS = ["bitcoin", "ethereum", "solana", "avalanche-2"]
POPULAR_COLLECTION = "popular_coins"

def fetch_and_store_popular_coins():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[POPULAR_COLLECTION]
    for coin_id in POPULAR_COINS:
        detail = fetch_coin_detail(coin_id)
        if detail:
            # Sadece temel alanları kaydet
            coin_data = {
                "id": detail.get("id"),
                "symbol": detail.get("symbol"),
                "name": detail.get("name"),
                "image": detail.get("image", {}).get("large"),
                "current_price": detail.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": detail.get("market_data", {}).get("market_cap", {}).get("usd"),
                "price_change_percentage_24h": detail.get("market_data", {}).get("price_change_percentage_24h"),
                "last_updated": datetime.now()
            }
            collection.update_one({"id": coin_id}, {"$set": coin_data}, upsert=True)
            print(f"{coin_id} güncellendi.")
        else:
            print(f"{coin_id} verisi alınamadı.")


def update_all_coins():
    print(f"[ {datetime.now()} ] Coin listesi çekiliyor...")
    coins = fetch_all_coins()
    if coins:
        upsert_coins_to_db(coins)
    else:
        print("Coin listesi alınamadı.")
    print(f"[ {datetime.now()} ] Popüler coinler güncelleniyor...")
    fetch_and_store_popular_coins()
    print(f"[ {datetime.now()} ] Tüm coinlerin detayları güncelleniyor...")
    fetch_and_store_all_coin_details()

def main():
    while True:
        update_all_coins()
        print("1 dakika bekleniyor...")
        time.sleep(60)

if __name__ == "__main__":
    main()
