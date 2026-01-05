import os
import sys
from datetime import datetime

ROOT_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_SRC not in sys.path:
    sys.path.insert(0, ROOT_SRC)

import pandas as pd
from db import database_manager as db

DATA_DIR = os.environ.get('ANALYSIS_DATA_DIR', 'analysis')
os.makedirs(DATA_DIR, exist_ok=True)


def load_series_from_db(coin_ids=None, save_csv=False, csv_prefix='ts_db'):
    """Load time-series price data for given coin_ids from MongoDB and return a pivoted DataFrame.

    If coin_ids is None, attempts to load list from `popular_coins` collection.
    Returns: DataFrame indexed by timestamp with columns per coin containing prices.
    """
    client = db.client
    if coin_ids is None:
        coll = client['crypto_project_db']['popular_coins']
        docs = list(coll.find({}, {'_id': 0}))
        coin_ids = [d.get('id') or d.get('coin_id') or d.get('symbol') for d in docs]
        coin_ids = [c for c in coin_ids if c]
    series_dict = {}
    for coin in coin_ids:
        df = db.get_market_data(coin)
        if df.empty:
            print(f'No market data for {coin} in DB')
            continue
        if 'timestamp' not in df.columns:
            print(f'No timestamp column for {coin} — skipping')
            continue
        df = df.copy()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.set_index('timestamp').sort_index()
        price_col = None
        for candidate in ('price','close','price_usd'):
            if candidate in df.columns:
                price_col = candidate
                break
        if price_col is None:
            cand_cols = [c for c in df.columns if c != 'coin_id']
            if cand_cols:
                price_col = cand_cols[0]
            else:
                print(f'No price-like column for {coin} — skipping')
                continue
        series = df[price_col].astype(float)
        series.name = coin
        series_dict[coin] = series
    if not series_dict:
        return pd.DataFrame()
    df_prices = pd.DataFrame(series_dict)
    df_prices = df_prices.sort_index().ffill()
    if save_csv:
        out_path = os.path.join(DATA_DIR, f'{csv_prefix}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df_prices.to_csv(out_path)
        print('Saved merged timeseries to', out_path)
    return df_prices


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Load time-series price data from MongoDB for analysis')
    parser.add_argument('--coins', nargs='*', help='List of coin ids to load (default: popular_coins)')
    parser.add_argument('--out', help='Save merged CSV to this path (optional)')
    args = parser.parse_args()
    coins = args.coins or None
    df = load_series_from_db(coins, save_csv=bool(args.out), csv_prefix='ts_db')
    if df.empty:
        print('No time-series data loaded.')
    else:
        print('Loaded timeseries with shape', df.shape)
        if args.out:
            df.to_csv(args.out)
            print('Wrote', args.out)
