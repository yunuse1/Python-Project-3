import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_binance_ohlc
import pymongo

import concurrent.futures

if __name__ == '__main__':
    # Docker ortamında 'mongo', lokalde 'localhost' kullanılır
    MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
    client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:27017/')
    db = client['crypto_project_db']
    
    # all_coins'deki tüm coinleri al
    all_coins = list(db['all_coins'].find({}, {'symbol': 1, '_id': 0}))
    
    # market_data'da veri olmayan coinleri bul
    market_symbols = set(db['market_data'].distinct('coin_id'))
    missing_coins = [c for c in all_coins if c['symbol'].lower() not in market_symbols]
    
    print(f'Toplam {len(missing_coins)} coin için market_data veri çekiliyor...')
    
    # Eksik coinlerin Binance sembolünü oluştur ve çek (paralel)
    symbols = [c['symbol'].upper() + 'USDT' for c in missing_coins]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                print(f'[{idx+1}/{len(symbols)}] Tamamlandı')
            except Exception as e:
                print(f'Hata: {e}')
    
    print('Tüm eksik market_data verileri eklendi!')
