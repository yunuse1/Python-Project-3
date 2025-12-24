import requests
import pandas as pd
from db import database_manager as db

def fetch_coin_history(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": "daily"
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        prices = data.get("prices", [])
        if not prices:
            print(f"No price data found for {coin_id}")
            return pd.DataFrame()

        df = pd.DataFrame(prices, columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        
        return df
        
    except Exception as e:
        print(f"Error fetching {coin_id}: {e}")
        return pd.DataFrame()

def main():
    # List of coins to update in the database
    coins_to_track = ["bitcoin", "ethereum", "solana", "avalanche-2"]
    
    print("--- Starting Database Update ---")
    
    for coin in coins_to_track:
        print(f"Fetching data for: {coin}...")
        df = fetch_coin_history(coin)
        
        if not df.empty:
            db.save_market_data(coin, df)
        else:
            print(f"Skipping {coin} due to missing data.")
            
    print("--- All updates completed successfully ---")

if __name__ == "__main__":
    main()