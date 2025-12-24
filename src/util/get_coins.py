import requests
import argparse

def get_coingecko_price(coin_name):
    
    url = f"https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_name.lower(), "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    data = response.json()
    try:
        return data[coin_name.lower()]["usd"]
    except Exception:
        return None

def main():
    parser = argparse.ArgumentParser(description="CoinGecko ile coin ismiyle anlık fiyat sorgulama")
    parser.add_argument("--coin", type=str, help="Coin ismi (bitcoin gibi ismini yaz):")
    args = parser.parse_args()

    if args.coin:
        price = get_coingecko_price(args.coin)
        if price:
            print(f"{args.coin.title()} anlık fiyatı: {price} USD")
        else:
            print(f"Fiyat alınamadı veya coin bulunamadı: {args.coin}")
    else:
        coin = input("Coin ismini girin (bitcoin gibi yaz): ")
        price = get_coingecko_price(coin)
        if price:
            print(f"{coin.title()} anlık fiyatı: {price} USD")
        else:
            print(f"Fiyat alınamadı veya coin bulunamadı: {coin}")

if __name__ == "__main__":
    main()
