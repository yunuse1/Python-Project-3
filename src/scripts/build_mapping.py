import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymongo
from util import get_coins

# Veritabanındaki tüm coinleri al
client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['crypto_project_db']
all_coins = list(db['all_coins'].find({}, {'symbol': 1, '_id': 0}))

print(f'Toplam {len(all_coins)} coin bulundu.')

# Eksik mapping'leri belirle ve ekle
new_mappings = {}
for coin in all_coins:
    symbol = coin.get('symbol', '').upper() + 'USDT'  # BTCUSDT formatı
    if symbol not in get_coins.BINANCE_TO_ID:
        # Dinamik id oluştur: symbol -> lowercase
        base_id = coin.get('symbol', '').lower()
        new_mappings[symbol] = base_id
        get_coins.BINANCE_TO_ID[symbol] = base_id

print(f'Yeni {len(new_mappings)} mapping eklendi.')
print(f'Toplam {len(get_coins.BINANCE_TO_ID)} mapping şimdi hazır.')

# Tüm coinler için market_data çek (paralel)
import concurrent.futures

symbols = list(get_coins.BINANCE_TO_ID.keys())
print(f'{len(symbols)} sembol için OHLC veri çekiliyor...')

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    futures = [executor.submit(get_coins.fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
    for idx, future in enumerate(concurrent.futures.as_completed(futures)):
        try:
            future.result()
            print(f'[{idx+1}/{len(symbols)}] Tamamlandı')
        except Exception as e:
            print(f'Hata: {e}')

print('Tüm market_data verileri başarıyla eklenmiştir!')
