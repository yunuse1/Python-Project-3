import os
import sys
from datetime import datetime

# Ensure src is on path when run from repo root
ROOT_SRC = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_SRC not in sys.path:
    sys.path.insert(0, ROOT_SRC)

import pymongo
import pandas as pd

# Use 'mongo' in Docker environment, 'localhost' locally
MONGO_HOST = os.environ.get('MONGO_HOST', 'localhost')
MONGO_URI = f'mongodb://{MONGO_HOST}:27017/'
DB_NAME = os.environ.get('DB_NAME', 'crypto_project_db')


def get_mongo_client(uri=None):
    return pymongo.MongoClient(uri or MONGO_URI)


def load_popular_coins(client=None):
    client = client or get_mongo_client()
    db = client[DB_NAME]
    coll = db['popular_coins']
    docs = list(coll.find())
    if not docs:
        return pd.DataFrame()
    df = pd.DataFrame(docs)
    # Convert datetime fields if present
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'])
    return df


def load_all_coin_details(client=None, limit=None):
    client = client or get_mongo_client()
    db = client[DB_NAME]
    coll = db['all_coins_details']
    cursor = coll.find()
    if limit:
        cursor = cursor.limit(limit)
    docs = list(cursor)
    if not docs:
        return pd.DataFrame()
    df = pd.DataFrame(docs)
    if 'last_updated' in df.columns:
        df['last_updated'] = pd.to_datetime(df['last_updated'])
    return df


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Load coin data for analysis and optionally save to CSV')
    parser.add_argument('--popular-out', help='CSV path to save popular coins', default='popular_coins.csv')
    parser.add_argument('--details-out', help='CSV path to save all coin details', default='all_coins_details_sample.csv')
    parser.add_argument('--details-limit', type=int, help='Limit number of detail docs to load', default=500)
    args = parser.parse_args()

    client = get_mongo_client()
    pop_df = load_popular_coins(client)
    print(f'Loaded popular coins: {len(pop_df)}')
    if not pop_df.empty:
        pop_df.to_csv(args.popular_out, index=False)
        print(f'Saved popular coins to {args.popular_out}')

    details_df = load_all_coin_details(client, limit=args.details_limit)
    print(f'Loaded all coin details: {len(details_df)}')
    if not details_df.empty:
        details_df.to_csv(args.details_out, index=False)
        print(f'Saved coin details sample to {args.details_out}')
