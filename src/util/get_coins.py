import requests
import time
import pymongo
from datetime import datetime
import pandas as pd

MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "crypto_project_db"
COLLECTION_NAME = "all_coins"

# Binance sembolü -> frontend id eşlemesi (manuel, popülerler için)
BINANCE_TO_ID = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'SOLUSDT': 'solana',
    'AVAXUSDT': 'avalanche-2',
    'BNBUSDT': 'binancecoin',
    'DOGEUSDT': 'dogecoin',
    'ADAUSDT': 'cardano',
    'XRPUSDT': 'ripple',
    'DOTUSDT': 'polkadot',
    'MATICUSDT': 'matic-network',
    'SHIBUSDT': 'shiba-inu',
    'TRXUSDT': 'tron',
    'LINKUSDT': 'chainlink',
    'LTCUSDT': 'litecoin',
    'BCHUSDT': 'bitcoin-cash',
    'UNIUSDT': 'uniswap',
    'XLMUSDT': 'stellar',
    'ATOMUSDT': 'cosmos',
    'ETCUSDT': 'ethereum-classic',
    'FILUSDT': 'filecoin',
    'HBARUSDT': 'hedera-hashgraph',
    'ICPUSDT': 'internet-computer',
    'VETUSDT': 'vechain',
    'AAVEUSDT': 'aave',
    'SANDUSDT': 'the-sandbox',
    'EGLDUSDT': 'elrond-erd-2',
    'MKRUSDT': 'maker',
    'NEARUSDT': 'near',
    'ALGOUSDT': 'algorand',
    'QNTUSDT': 'quant-network',
    'XTZUSDT': 'tezos',
    'GRTUSDT': 'the-graph',
    'AXSUSDT': 'axie-infinity',
    'FTMUSDT': 'fantom',
    'THETAUSDT': 'theta-token',
    'CAKEUSDT': 'pancakeswap-token',
    'KLAYUSDT': 'klay-token',
    'CHZUSDT': 'chiliz',
    'ENJUSDT': 'enjincoin',
    'ZILUSDT': 'zilliqa',
    'ONEUSDT': 'harmony',
    'XEMUSDT': 'nem',
    'HOTUSDT': 'holo',
    'DASHUSDT': 'dash',
    'COMPUSDT': 'compound-governance-token',
    'BATUSDT': 'basic-attention-token',
    'ZRXUSDT': '0x',
    'SNXUSDT': 'synthetix-network-token',
    'YFIUSDT': 'yearn-finance',
    'OMGUSDT': 'omisego',
    'BATUSDT': 'basic-attention-token',
    'RVNUSDT': 'ravencoin',
    'SCUSDT': 'siacoin',
    'DGBUSDT': 'digibyte',
    'LSKUSDT': 'lisk',
    'NANOUSDT': 'nano',
    'ZENUSDT': 'horizen',
    'ICXUSDT': 'icon',
    'STMXUSDT': 'stormx',
    'CELRUSDT': 'celer-network',
    'CTSIUSDT': 'cartesi',
    'BANDUSDT': 'band-protocol',
    'WRXUSDT': 'wazirx',
    'LRCUSDT': 'loopring',
    'CVCUSDT': 'civic',
    'DOCKUSDT': 'dock',
    'TWTUSDT': 'trust-wallet-token',
    'PERLUSDT': 'perlin',
    'TOMOUSDT': 'tomochain',
    'FETUSDT': 'fetch-ai',
    'CTKUSDT': 'certik',
    'AKROUSDT': 'akropolis',
    'LITUSDT': 'litentry',
    'PUNDIXUSDT': 'pundi-x',
    'FORTHUSDT': 'ampleforth-governance-token',
    'REEFUSDT': 'reef',
    'SXPUSDT': 'swipe',
    'BTSUSDT': 'bitshares',
    'XVSUSDT': 'venus',
    'BAKEUSDT': 'bakerytoken',
    'TLMUSDT': 'alien-worlds',
    'ALICEUSDT': 'myneighboralice',
    'DEGOUSDT': 'dego-finance',
    'DODOUSDT': 'dodo',
    'BELUSDT': 'bella-protocol',
    'WINGUSDT': 'wing-finance',
    'LINAUSDT': 'linear',
    'RAMPUSDT': 'ramp',
    'SFPUSDT': 'safe-pal',
    'C98USDT': 'coin98',
    'PORTOUSDT': 'porto',
    'CITYUSDT': 'manchester-city-fan-token',
    'PSGUSDT': 'paris-saint-germain-fan-token',
    'JUVUSDT': 'juventus-fan-token',
    'ATMUSDT': 'atletico-madrid-fan-token',
    'BARUSDT': 'fc-barcelona-fan-token',
    'ASRUSDT': 'as-roma-fan-token',
    'OGUSDT': 'og-fan-token',
    'LAZIOUSDT': 'ss-lazio-fan-token',
    'INTERUSDT': 'inter-milan-fan-token',
    'GALUSDT': 'galatasaray-fan-token',
    'TRAUSDT': 'trabzonspor-fan-token',
    'NAPUSDT': 'ssc-napoli-fan-token',
    'ACMUSDT': 'ac-milan-fan-token',
    'AFCUSDT': 'arsenal-fan-token',
    'SAOUSDT': 'saudi-arabia-fan-token',
    'PORTOUSDT': 'porto',
    'SANTOSUSDT': 'santos-fc-fan-token',
    'VOXELUSDT': 'voxels',
    'HIGHUSDT': 'highstreet',
    'CVXUSDT': 'convex-finance',
    'PEOPLEUSDT': 'constitutiondao',
    'ENSUSDT': 'ethereum-name-service',
    'GALAUSDT': 'gala',
    'JASMYUSDT': 'jasmycoin',
    'API3USDT': 'api3',
    'BICOUSDT': 'biconomy',
    'IMXUSDT': 'immutable-x',
    'SPELLUSDT': 'spell-token',
    'LDOUSDT': 'lido-dao',
    'STGUSDT': 'stargate-finance',
    'GMXUSDT': 'gmx',
    'OPUSDT': 'optimism',
    'ARBUSDT': 'arbitrum',
    'SUIUSDT': 'sui',
    'SEIUSDT': 'sei',
    'TIAUSDT': 'celestia',
    'ORDIUSDT': 'ordi',
    'MEMEUSDT': 'memecoin',
    'WIFUSDT': 'dogwifhat',
    'JUPUSDT': 'jupiter',
    'PYTHUSDT': 'pyth-network',
    'AEVOUSDT': 'aevo',
    'MANTAUSDT': 'manta-network',
    'STRKUSDT': 'starknet',
    'ETHFIUSDT': 'ether-fi',
    'ALTUSDT': 'altlayer',
    'ZETAUSDT': 'zetachain',
    'ENAUSDT': 'ethena',
    'TURBOUSDT': 'turbo',
    'HYPERUSDT': 'hyperliquid',
    'DOGUSDT': 'dogecoin',
    'USDTTRY': 'tether',
    'HYPEUSDT': 'hyperliquid',
}

def fetch_and_store_all_coin_details_full():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["all_coins_details"]
    all_coins = list(db["all_coins"].find({}, {"id": 1, "_id": 0}))
    print(f"Toplam {len(all_coins)} coin detayları çekilecek...")
    for idx, coin in enumerate(all_coins):
        coin_id = coin["id"]
        detail = fetch_coin_detail(coin_id)
        if detail:
            coin_data = {
                "id": detail.get("id"),
                "symbol": detail.get("symbol"),
                "name": detail.get("name"),
                "image": detail.get("image", {}).get("large"),
                "current_price": detail.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": detail.get("market_data", {}).get("market_cap", {}).get("usd"),
                "price_change_percentage_24h": detail.get("market_data", {}).get("price_change_percentage_24h"),
                "last_updated": datetime.now()
            }
            collection.update_one({"id": coin_id}, {"$set": coin_data}, upsert=True)
            print(f"[{idx+1}/{len(all_coins)}] {coin_id} detay kaydedildi.")
        else:
            print(f"{coin_id} detay alınamadı.")
        time.sleep(1.2)  # API rate limit için bekle
    print("Tüm coin detayları tamamlandı.")
    
def fetch_all_coins():
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url)
    if response.status_code == 200:
        coins = response.json()
        # Tüm USDT paritelerini al (sadece ilk 1000)
        filtered = [c for c in coins if c['symbol'].endswith('USDT')][:1000]
        result = []
        for coin in filtered:
            base = coin['symbol'][:-4]  # BTCUSDT -> BTC
            result.append({
                'id': coin['symbol'],
                'symbol': base,
                'name': base,
                'current_price': float(coin['price']),
                'market_cap': None,
                'image': None,
                'price_change_percentage_24h': None
            })
        print(f"API'dan {len(result)} USDT paritesi çekildi.")
        return result
    else:
        print("Binance API'dan coin listesi alınamadı.")
        return []

def fetch_coin_detail(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def upsert_coins_to_db(coins):
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    for coin in coins:
        coin["last_updated"] = datetime.now()
        collection.update_one({"id": coin["id"]}, {"$set": coin}, upsert=True)
    print(f"{len(coins)} coin güncellendi/eklendi.")

# Popüler coinlerin detaylı verisi için ayrı koleksiyon
POPULAR_COINS = ["bitcoin", "ethereum", "solana", "avalanche-2"]
POPULAR_COLLECTION = "popular_coins"

def fetch_and_store_popular_coins():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[POPULAR_COLLECTION]
    for coin_id in POPULAR_COINS:
        detail = fetch_coin_detail(coin_id)
        if detail:
            # Sadece temel alanları kaydet
            coin_data = {
                "id": detail.get("id"),
                "symbol": detail.get("symbol"),
                "name": detail.get("name"),
                "image": detail.get("image", {}).get("large"),
                "current_price": detail.get("market_data", {}).get("current_price", {}).get("usd"),
                "market_cap": detail.get("market_data", {}).get("market_cap", {}).get("usd"),
                "price_change_percentage_24h": detail.get("market_data", {}).get("price_change_percentage_24h"),
                "last_updated": datetime.now()
            }
            collection.update_one({"id": coin_id}, {"$set": coin_data}, upsert=True)
            print(f"{coin_id} güncellendi.")
        else:
            print(f"{coin_id} verisi alınamadı.")


def update_all_coins():
    print(f"[ {datetime.now()} ] Coin listesi çekiliyor...")
    coins = fetch_all_coins()
    if coins:
        upsert_coins_to_db(coins)
    else:
        print("Coin listesi alınamadı.")
    print(f"[ {datetime.now()} ] Popüler coinler güncelleniyor...")
    fetch_and_store_popular_coins()
    print(f"[ {datetime.now()} ] Tüm coinlerin detayları güncelleniyor...")
    fetch_and_store_all_coin_details()

def fetch_and_store_all_coin_details():
    client = pymongo.MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db["all_coins_details"]
    per_page = 250
    total_inserted = 0
    max_pages = 4  # İlk 1000 popüler coin
    for page in range(1, max_pages + 1):
        url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page={per_page}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print(f"API hatası: {response.status_code}")
            break
        coins = response.json()
        if not coins:
            break
        print(f"Sayfa {page} - {len(coins)} coin işleniyor...")
        for idx, coin in enumerate(coins):
            coin_data = {
                "id": coin.get("id"),
                "symbol": coin.get("symbol"),
                "name": coin.get("name"),
                "image": coin.get("image"),
                "current_price": coin.get("current_price"),
                "market_cap": coin.get("market_cap"),
                "price_change_percentage_24h": coin.get("price_change_percentage_24h"),
                "last_updated": datetime.now()
            }
            collection.update_one({"id": coin["id"]}, {"$set": coin_data}, upsert=True)
            total_inserted += 1
        print(f"Toplam eklenen/güncellenen: {total_inserted}")
        time.sleep(2)  # API rate limit için bekle
    print(f"İlk 1000 popüler coin detayları güncellendi. Toplam: {total_inserted}")

def fetch_and_store_binance_ohlc(symbol, interval="1d", limit=90):
    """
    Binance API'dan geçmiş fiyat verisi (OHLC) çekip market_data'ya kaydeder.
    symbol: Binance sembolü (örn: BTCUSDT)
    interval: Zaman aralığı (örn: 1d, 4h, 1h)
    limit: Kaç veri çekilecek (maks 1000)
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Binance kline API hatası: {response.status_code}")
        return
    data = response.json()
    if not data:
        print(f"Veri yok: {symbol}")
        return
    # Her satırı dict'e çevir
    from datetime import datetime as dt
    records = []
    for row in data:
        # Timestamp milisaniye cinsinden, ISO formatına çevir
        timestamp_ms = row[0]
        timestamp_iso = dt.utcfromtimestamp(timestamp_ms / 1000).isoformat() + 'Z'
        records.append({
            "coin_id": symbol,
            "timestamp": timestamp_iso,
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "price": float(row[4]),  # Frontend için "price" alanı (close fiyatı)
            "volume": float(row[5])
        })
    # MongoDB'ye kaydet
    client = pymongo.MongoClient(MONGO_URI)
    db_ = client[DB_NAME]
    market_collection = db_["market_data"]
    market_collection.delete_many({"coin_id": symbol})
    # Ek olarak, mapping varsa frontend id'siyle de kaydet
    frontend_id = BINANCE_TO_ID.get(symbol)
    if frontend_id:
        market_collection.delete_many({"coin_id": frontend_id})
    if records:
        market_collection.insert_many(records)
        print(f"{symbol} için {len(records)} OHLC veri kaydedildi.")
        # Frontend id ile de kopya kaydet (aynı _id çakışmasını önlemek için _id kaldır)
        if frontend_id:
            mapped = []
            for r in records:
                r2 = r.copy()
                r2.pop("_id", None)
                r2["coin_id"] = frontend_id
                mapped.append(r2)
            if mapped:
                market_collection.insert_many(mapped)
                print(f"Ek olarak {frontend_id} id ile de {len(mapped)} veri kaydedildi.")
    else:
        print(f"{symbol} için veri yok.")

def main():
    while True:
        update_all_coins()
        print("1 dakika bekleniyor...")
        time.sleep(60)

if __name__ == "__main__":
    main()
