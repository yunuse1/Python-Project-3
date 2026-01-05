import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from util.get_coins import fetch_and_store_binance_ohlc
import pymongo

import concurrent.futures

if __name__ == '__main__':
    MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
    client = pymongo.MongoClient(f'mongodb://{MONGO_HOST}:27017/')
    db = client['crypto_project_db']
    
    all_coins = list(db['all_coins'].find({}, {'symbol': 1, '_id': 0}))
    
    market_symbols = set(db['market_data'].distinct('coin_id'))
    missing_coins = [c for c in all_coins if c['symbol'].lower() not in market_symbols]
    
    logger.info(f'Fetching market_data for {len(missing_coins)} coins...')
    
    symbols = [c['symbol'].upper() + 'USDT' for c in missing_coins]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_and_store_binance_ohlc, symbol, '1d', 90) for symbol in symbols]
        for idx, future in enumerate(concurrent.futures.as_completed(futures)):
            try:
                future.result()
                logger.info(f'[{idx+1}/{len(symbols)}] Completed')
            except Exception as e:
                logger.error(f'Error: {e}')
    
    logger.info('All missing market_data records added!')
