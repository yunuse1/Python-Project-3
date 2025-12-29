import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_all_coins, upsert_coins_to_db
import pymongo

if __name__ == '__main__':
    # 1. all_coins koleksiyonunu temizle
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['crypto_project_db']
    db['all_coins'].delete_many({})
    print('all_coins temizlendi.')
    
    # 2. Tüm coinleri Binance API'dan çek (1000+ coin)
    print('Binance API\'dan tüm coinler çekiliyor...')
    coins = fetch_all_coins()
    print(f'{len(coins)} coin çekildi.')
    
    # 3. Veritabanına kaydet
    if coins:
        upsert_coins_to_db(coins)
        print(f'{len(coins)} coin veritabanına kaydedildi.')
    else:
        print('Coin bulunamadı.')
