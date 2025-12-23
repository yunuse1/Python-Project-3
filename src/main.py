import requests
import pandas as pd
import matplotlib.pyplot as plt

# CoinGecko API'den veri çekme fonksiyonu
def fetch_coin_history(coin_id, days=5):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    response = requests.get(url, params=params)
    data = response.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df

# Örnek kullanım: Bitcoin'in son 5 günlük fiyatı
def main():
    coin_id = "bitcoin"
    df = fetch_coin_history(coin_id, days=5)
    plt.figure(figsize=(10,5))
    plt.plot(df["timestamp"], df["price"], label="Bitcoin")
    plt.title("Bitcoin Son 5 Günlük Fiyat Grafiği")
    plt.xlabel("Tarih")
    plt.ylabel("Fiyat (USD)")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
