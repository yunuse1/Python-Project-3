import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_binance_ohlc
import pymongo
import concurrent.futures

if __name__ == '__main__':
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['crypto_project_db']
    
    # market_data tamamen temizle
    db['market_data'].delete_many({})
    print('market_data temizlendi.')
    
    # all_coins'deki tüm coinler için Binance'ten veri çek
    all_coins = list(db['all_coins'].find({}, {'symbol': 1, '_id': 0}))
    print(f'Toplam {len(all_coins)} coin için market_data çekiliyor...')
    
    # Symbol -> USDT format (ör: BTC -> BTCUSDT)
    symbols = [c['symbol'].upper() + 'USDT' for c in all_coins]
    
    # Paralel çek
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
        completed = 0
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
                completed += 1
                if completed % 50 == 0:
                    print(f'[{completed}/{len(symbols)}] Tamamlandı')
            except Exception as e:
                print(f'Hata: {e}')
    
    # Sonuç kontrol
    market_count = db['market_data'].count_documents({})
    unique = len(db['market_data'].distinct('coin_id'))
    print(f'Tamamlandı: {market_count} records, {unique} unique coins')
