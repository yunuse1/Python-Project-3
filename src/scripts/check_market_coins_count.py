import pymongo
client = pymongo.MongoClient('mongodb://localhost:27017/')
market_ids = set(client['crypto_project_db']['market_data'].distinct('coin_id'))
all_details = list(client['crypto_project_db']['all_coins_details'].find({}, {'_id':0}))
count = 0
for d in all_details:
    coin_id = str(d.get('id'))
    sym = (d.get('symbol') or '').upper()
    candidates = {coin_id, sym, sym + 'USDT', sym + 'BUSD', sym + 'USDC'}
    if market_ids.intersection(candidates):
        count += 1
print('market coins count:', count)
print('total all_coins_details:', len(all_details))
