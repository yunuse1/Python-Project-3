import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import pymongo

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "crypto_project_db"

client = pymongo.MongoClient(MONGO_URI)
db = client[DB_NAME]
all_coins_col = db['all_coins']
details_col = db['all_coins_details']

before_count = all_coins_col.count_documents({})
print(f'all_coins before: {before_count}')

# For each detail doc, ensure an all_coins entry exists (upsert by id or symbol)
added = 0
for doc in details_col.find({}, {'_id':0}):
    # choose key: use detail id as unique identifier in all_coins
    coin_id = doc.get('id')
    if not coin_id:
        continue
    # Build a canonical all_coins document
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
    # update_one with $setOnInsert returns upserted_id when inserted
    if res.upserted_id:
        added += 1

after_count = all_coins_col.count_documents({})
print(f'all_coins after: {after_count} (added {added})')
print('Merge completed.')
