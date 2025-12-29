import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_binance_ohlc, BINANCE_TO_ID
import concurrent.futures

if __name__ == '__main__':
    symbols = list(BINANCE_TO_ID.keys())
    print(f'Tüm {len(symbols)} popüler coin için OHLC veri çekiliyor (paralel)...')
    
    # 5 paralel worker ile çek
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                print(f'[{idx+1}/{len(symbols)}] Tamamlandı')
            except Exception as e:
                print(f'Hata: {e}')
    
    print('Tüm market_data verileri başarıyla eklenmiştir!')
