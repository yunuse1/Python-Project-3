import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

class CryptoAnalysisEngine:
    """
    Standalone module for crypto data analysis.
    Works with the 'price' column from historical data.
    """

    # --- 1. Technical Indicators (SMA & RSI) ---
    def calculate_technical_indicators(self, df):
        # Calculating Moving Averages for trend direction
        df['sma_7'] = df['price'].rolling(window=7).mean()
        df['sma_30'] = df['price'].rolling(window=30).mean()
        
        # Calculating RSI (Relative Strength Index)
        delta = df['price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        rs = gain / loss
        # Added a small epsilon (1e-9) to prevent division by zero
        df['rsi'] = 100 - (100 / (1 + rs + 1e-9))
        return df

    # --- 2. Volatility and Risk Analysis ---
    def calculate_risk_metrics(self, df):
        # Standard deviation shows how much the price fluctuates
        df['volatility'] = df['price'].rolling(window=7).std()
        
        # Finding the 30-day high and calculating the distance from it
        high_30d = df['price'].rolling(window=30).max()
        df['pct_from_high'] = ((high_30d - df['price']) / high_30d) * 100
        return df

    # --- 3. Correlation & Beta Analysis ---
    def get_correlation_with_btc(self, btc_df, altcoin_df):
        # Daily percentage change
        btc_returns = btc_df['price'].pct_change()
        alt_returns = altcoin_df['price'].pct_change()
        
        # Correlation Coefficient
        corr = alt_returns.corr(btc_returns)
        
        # Beta calculation: sensitivity of altcoin to Bitcoin moves
        covariance = alt_returns.cov(btc_returns)
        variance = btc_returns.var()
        beta = covariance / variance if variance != 0 else 0
        
        return {"correlation": round(corr, 4), "beta": round(beta, 4)}

    # --- 4. Portfolio Profit/Loss (PnL) ---
    def calculate_portfolio_pnl(self, current_price, buy_price, amount):
        # Calculate money earned or lost
        profit_usd = (current_price - buy_price) * amount
        profit_pct = ((current_price - buy_price) / buy_price) * 100
        
        return {
            "profit_usd": round(profit_usd, 2),
            "profit_pct": round(profit_pct, 2)
        }

    # --- 5. Simple Trend Forecasting ---
    def get_trend_prediction(self, df):
        # Use Linear Regression on the last 10 days of data
        if len(df) < 10:
            return "Incomplete Data"
            
        # Target (y) is price, Features (X) is time index
        y = df['price'].values[-10:].reshape(-1, 1)
        X = np.arange(len(y)).reshape(-1, 1)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Slope > 0 means the price trend is moving UP
        return "UPWARD" if model.coef_[0][0] > 0 else "DOWNWARD"