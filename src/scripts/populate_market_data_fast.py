import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_binance_ohlc, BINANCE_TO_ID
import concurrent.futures

if __name__ == '__main__':
    symbols = list(BINANCE_TO_ID.keys())
    logger.info(f'Fetching OHLC data for all {len(symbols)} popular coins (parallel)...')
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                logger.info(f'[{idx+1}/{len(symbols)}] Completed')
            except Exception as e:
                logger.error(f'Error: {e}')
    
    logger.info('All market_data records successfully added!')
