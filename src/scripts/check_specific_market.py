import pymongo

client = pymongo.MongoClient('mongodb://localhost:27017/')
db = client['crypto_project_db']
market = db['market_data']
details = db['all_coins_details']

coins = ['bitcoin','ethereum']

for coin in coins:
    doc = details.find_one({'id': coin}, {'symbol': 1})
    sym = doc.get('symbol').upper() if doc and doc.get('symbol') else None
    candidates = [coin]
    if sym:
        candidates += [sym, sym + 'USDT', sym + 'BUSD', sym + 'USDC']
    candidates = list(dict.fromkeys(candidates))

    count = market.count_documents({'coin_id': {'$in': candidates}})
    sample = list(market.find({'coin_id': {'$in': candidates}}, {'_id':0}).limit(3))

    print(f"--- {coin} ---")
    print('Checked candidates:', candidates)
    print('Market rows found:', count)
    if sample:
        print('Sample row:', sample[0])
    else:
        print('No sample rows (no market data).')
    print()
