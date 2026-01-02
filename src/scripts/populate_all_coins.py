import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import update_all_coins, fetch_and_store_binance_ohlc, BINANCE_TO_ID

if __name__ == '__main__':
    # First update coin list (fast)
    update_all_coins()
    
    # Fetch historical price data for popular coins (all symbols in BINANCE_TO_ID)
    popular_symbols = list(BINANCE_TO_ID.keys())
    logger.info(f'Starting: Fetching OHLC data for {len(popular_symbols)} popular coins...')
    for idx, symbol in enumerate(popular_symbols):
        logger.info(f'[{idx+1}/{len(popular_symbols)}] Fetching {symbol}...')
        fetch_and_store_binance_ohlc(symbol, interval='1d', limit=90)
    logger.info('All coins and historical prices updated.')
