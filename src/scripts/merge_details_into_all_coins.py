import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pymongo

MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_URI = f"mongodb://{MONGO_HOST}:27017/"
DB_NAME = "crypto_project_db"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
all_coins_col = db['all_coins']
details_col = db['all_coins_details']

before_count = all_coins_col.count_documents({})
print(f'all_coins before: {before_count}')

added = 0
for doc in details_col.find({}, {'_id':0}):
    coin_id = doc.get('id')
    if not coin_id:
        continue
    record = {
        'id': coin_id,
        'symbol': doc.get('symbol') or coin_id,
        'name': doc.get('name') or coin_id,
        'image': doc.get('image'),
        'current_price': doc.get('current_price'),
        'market_cap': doc.get('market_cap'),
        'price_change_percentage_24h': doc.get('price_change_percentage_24h'),
        'last_updated': doc.get('last_updated')
    }
    res = all_coins_col.update_one({'id': coin_id}, {'$setOnInsert': record}, upsert=True)
    if res.upserted_id:
        added += 1

after_count = all_coins_col.count_documents({})
print(f'all_coins after: {after_count} (added {added})')
print('Merge completed.')
