import requests
import pandas as pd
from db import database_manager as db
from analysis_engine import CryptoAnalysisEngine

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
    engine = CryptoAnalysisEngine()
    all_coin_data = {}  # To store data for Step 3 and 4
    # List of coins to update in the database
    coins_to_track = ["bitcoin", "ethereum", "solana", "avalanche-2"]
    
    print("--- Starting Database Update ---")
    
    for coin in coins_to_track:
        print(f"Fetching data for: {coin}...")
        df = fetch_coin_history(coin)
        if not df.empty:
            # --- START OF NEW ANALYSIS ---
            # Step 1: Indicators (SMA/RSI)
            df = engine.calculate_technical_indicators(df)
            
            # Step 2: Risk (Volatility)
            df = engine.calculate_risk_metrics(df)
            
            # Step 5: Trend Prediction
            trend = engine.get_trend_prediction(df)
            print(f"Trend for {coin}: {trend}")
            
            # Save to dictionary for Steps 3 & 4
            all_coin_data[coin] = df 
            # --- END OF NEW ANALYSIS ---
            db.save_market_data(coin, df)
        else:
            print(f"Skipping {coin} due to missing data.")
    
    # --- STEP 3: Correlation Analysis ---
    if "bitcoin" in all_coin_data:
        btc_df = all_coin_data["bitcoin"]
        for coin_id, coin_df in all_coin_data.items():
            if coin_id != "bitcoin":
                corr = engine.get_correlation_with_btc(btc_df, coin_df)
                print(f"Correlation {coin_id} vs BTC: {corr['correlation']}")

    # --- STEP 4: Portfolio P/L Analysis ---
    try:
        users = list(db.users_collection.find({}, {"_id": 0}))
        for user in users:
            for trade in user.get('trades', []):
                c_id = trade['coin_id']
                if c_id in all_coin_data:
                    current = all_coin_data[c_id]['price'].iloc[-1]
                    pnl = engine.calculate_portfolio_pnl(current, trade['buy_price'], trade['amount'])
                    print(f"User {user.get('username')} {c_id} P/L: %{pnl['profit_pct']}")
    except Exception as e:
        print(f"Portfolio calculation error: {e}")        
    print("--- All updates completed successfully ---")

if __name__ == "__main__":
    main()