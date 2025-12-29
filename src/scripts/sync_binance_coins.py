import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import pymongo

if __name__ == '__main__':
    # Binance'den tüm USDT paritelerini çek
    print('Binance API\'dan tüm USDT paritelerini çekiliyor...')
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f'API hatası: {response.status_code}')
        exit(1)
    
    all_pairs = response.json()
    usdt_pairs = [p for p in all_pairs if p['symbol'].endswith('USDT')]
    print(f'Toplam {len(usdt_pairs)} USDT paritesi bulundu.')
    
    # Symbol'ü çıkar (BTCUSDT -> BTC)
    symbols = set([p['symbol'][:-4] for p in usdt_pairs])
    print(f'Unique {len(symbols)} coin symbol.')
    
    # MongoDB'de all_coins'i güncelle (sadece Binance'de var olanları tut)
    client = pymongo.MongoClient('mongodb://localhost:27017/')
    db = client['crypto_project_db']
    
    # Tüm Binance coinlerini kaydet
    db['all_coins'].delete_many({})
    
    records = []
    for pair in usdt_pairs:
        symbol = pair['symbol'][:-4]
        records.append({
            'id': pair['symbol'],
            'symbol': symbol,
            'name': symbol,
            'current_price': float(pair['price']),
            'market_cap': None,
            'image': None,
            'price_change_percentage_24h': None
        })
    
    if records:
        db['all_coins'].insert_many(records)
        print(f'{len(records)} coin kaydedildi.')
    
    # market_data'da olan ama all_coins'de olmayan coinleri sil
    market_symbols = db['market_data'].distinct('coin_id')
    for sym in market_symbols:
        if sym.lower() not in symbols:
            db['market_data'].delete_many({'coin_id': sym})
    
    print('Tamamlandı: all_coins ve market_data senkronize edildi.')
