import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import update_all_coins, fetch_and_store_binance_ohlc, BINANCE_TO_ID

if __name__ == '__main__':
    # Önce coin listesini güncelle (hızlı)
    update_all_coins()
    
    # Popüler coinler için geçmiş fiyat verisi çek (BINANCE_TO_ID'deki tüm semboller)
    popular_symbols = list(BINANCE_TO_ID.keys())
    print(f'Başlanıyor: {len(popular_symbols)} popüler coin için OHLC veri çekiliyor...')
    for idx, symbol in enumerate(popular_symbols):
        print(f'[{idx+1}/{len(popular_symbols)}] {symbol} çekiliyor...')
        fetch_and_store_binance_ohlc(symbol, interval='1d', limit=90)
    print('Tüm coinler ve geçmiş fiyatlar güncellendi.')
