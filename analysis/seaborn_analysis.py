"""Seaborn Crypto Analysis
=========================
This script visualizes cryptocurrency data from MongoDB using Seaborn.
Outputs are saved to: analysis/plots/ folder.

Usage:
    python analysis/seaborn_analysis.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from db import database_manager as db
from scipy import stats

# Seaborn style settings
sns.set_theme(style="darkgrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Output directory
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_coin_data(coin_id):
    """Load and clean coin data"""
    df = db.get_market_data(coin_id)
    if df.empty:
        return None
    
    # Price column normalization
    if 'price' not in df.columns:
        if 'close' in df.columns:
            df['price'] = df['close']
        elif 'c' in df.columns:
            df['price'] = df['c']
    
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df = df.dropna(subset=['price'])
    
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
    
    # Calculate daily returns
    df['daily_return'] = df['price'].pct_change() * 100
    df['log_return'] = np.log(df['price'] / df['price'].shift(1)) * 100
    
    return df


def plot_price_distribution(df, coin_name, save=True):
    """
    1. Price Distribution - Histogram + KDE
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram + KDE
    sns.histplot(data=df, x='price', kde=True, ax=axes[0], color='#3498db', bins=30)
    axes[0].set_title(f'{coin_name} - Price Distribution', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Price (USD)')
    axes[0].set_ylabel('Frequency')
    
    # Box Plot
    sns.boxplot(data=df, y='price', ax=axes[1], color='#2ecc71')
    axes[1].set_title(f'{coin_name} - Price Box Plot', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Price (USD)')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_price_distribution.png'), dpi=150)
    plt.close()


def plot_returns_analysis(df, coin_name, save=True):
    """
    2. Returns Analysis - Histogram, Violin, Box
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    returns = df['daily_return'].dropna()
    
    # Returns Histogram + KDE
    sns.histplot(returns, kde=True, ax=axes[0, 0], color='#9b59b6', bins=30)
    axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0, 0].set_title('Daily Return Distribution', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Daily Return (%)')
    
    # Violin Plot
    sns.violinplot(y=returns, ax=axes[0, 1], color='#e74c3c')
    axes[0, 1].axhline(y=0, color='black', linestyle='--', linewidth=1)
    axes[0, 1].set_title('Return Violin Plot', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Daily Return (%)')
    
    # QQ Plot (against normal distribution)
    stats.probplot(returns, dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title('Q-Q Plot (Normal Distribution)', fontsize=12, fontweight='bold')
    
    # Strip Plot (returns over time)
    if len(returns) > 0:
        return_categories = pd.cut(returns, bins=[-np.inf, -5, -2, 0, 2, 5, np.inf], 
                                   labels=['<-5%', '-5 to -2%', '-2 to 0%', '0 to 2%', '2 to 5%', '>5%'])
        category_counts = return_categories.value_counts()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=axes[1, 1], palette='RdYlGn')
        axes[1, 1].set_title('Return Category Distribution', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Return Range')
        axes[1, 1].set_ylabel('Number of Days')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.suptitle(f'{coin_name} - Returns Analysis', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_returns_analysis.png'), dpi=150)
    plt.close()


def plot_time_series(df, coin_name, save=True):
    """
    3. Time Series Analysis
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Price trend
    sns.lineplot(data=df, x='timestamp', y='price', ax=axes[0], color='#3498db', linewidth=2)
    axes[0].fill_between(df['timestamp'], df['price'], alpha=0.3)
    axes[0].set_title(f'{coin_name} - Price Trend', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Price (USD)')
    
    # Rolling Mean + Std
    df['rolling_mean'] = df['price'].rolling(window=7).mean()
    df['rolling_std'] = df['price'].rolling(window=7).std()
    
    axes[1].plot(df['timestamp'], df['price'], label='Price', alpha=0.5)
    axes[1].plot(df['timestamp'], df['rolling_mean'], label='7-Day Average', color='red', linewidth=2)
    axes[1].fill_between(df['timestamp'], 
                         df['rolling_mean'] - 2*df['rolling_std'],
                         df['rolling_mean'] + 2*df['rolling_std'],
                         alpha=0.2, color='red', label='±2 Std')
    axes[1].set_title('Price + Rolling Statistics', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Price (USD)')
    axes[1].legend(loc='upper left')
    
    # Daily Return Bar
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['daily_return'].fillna(0)]
    axes[2].bar(df['timestamp'], df['daily_return'].fillna(0), color=colors, width=0.8)
    axes[2].axhline(y=0, color='black', linewidth=0.5)
    axes[2].set_title('Daily Return', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Date')
    axes[2].set_ylabel('Return (%)')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_time_series.png'), dpi=150)
    plt.close()


def plot_correlation_heatmap(coins_data, save=True):
    """
    4. Correlation Heatmap
    """
    # Combine prices from all coins
    price_df = pd.DataFrame()
    for coin_name, df in coins_data.items():
        if df is not None and 'price' in df.columns:
            price_df[coin_name] = df.set_index('timestamp')['price']
    
    if price_df.empty:
        return
    
    # Return correlation
    returns_df = price_df.pct_change().dropna()
    correlation = returns_df.corr()
    
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    
    sns.heatmap(correlation, mask=mask, annot=True, fmt='.2f', 
                cmap='RdYlGn', center=0, 
                square=True, linewidths=0.5,
                cbar_kws={"shrink": 0.8, "label": "Correlation"})
    
    plt.title('Cryptocurrency Return Correlation', fontsize=14, fontweight='bold')
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'), dpi=150)
    plt.close()


def plot_volatility_comparison(coins_data, save=True):
    """
    5. Volatility Comparison
    """
    volatility_data = []
    
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            returns = df['daily_return'].dropna()
            volatility_data.append({
                'coin': coin_name,
                'volatility': returns.std(),
                'mean_return': returns.mean(),
                'sharpe': returns.mean() / returns.std() if returns.std() > 0 else 0
            })
    
    if not volatility_data:
        return
    
    vol_df = pd.DataFrame(volatility_data)
    
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    # Volatility Bar
    sns.barplot(data=vol_df.sort_values('volatility', ascending=False), 
                x='coin', y='volatility', ax=axes[0], palette='Reds_r')
    axes[0].set_title('Daily Volatility', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Coin')
    axes[0].set_ylabel('Std Deviation (%)')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Average Return Bar
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in vol_df.sort_values('mean_return', ascending=False)['mean_return']]
    sns.barplot(data=vol_df.sort_values('mean_return', ascending=False), 
                x='coin', y='mean_return', ax=axes[1], palette=colors)
    axes[1].set_title('Average Daily Return', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Coin')
    axes[1].set_ylabel('Average (%)')
    axes[1].axhline(y=0, color='black', linestyle='--')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Risk-Return Scatter
    sns.scatterplot(data=vol_df, x='volatility', y='mean_return', 
                    hue='coin', s=200, ax=axes[2])
    axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[2].axvline(x=vol_df['volatility'].mean(), color='gray', linestyle='--', alpha=0.5)
    axes[2].set_title('Risk-Return Profile', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Volatility (Risk)')
    axes[2].set_ylabel('Average Return')
    axes[2].legend(loc='best')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_comparison.png'), dpi=150)
    plt.close()


def plot_statistical_summary(coins_data, save=True):
    """
    6. Statistical Summary - Pair Plot and Joint Plot
    """
    # Pair plot with max 4 coins
    sample_coins = list(coins_data.keys())[:4]
    price_df = pd.DataFrame()
    
    for coin_name in sample_coins:
        df = coins_data.get(coin_name)
        if df is not None and 'price' in df.columns:
            price_df[coin_name] = df.set_index('timestamp')['price']
    
    if len(price_df.columns) < 2:
        return
    
    returns_df = price_df.pct_change().dropna() * 100
    
    # Pair Plot
    g = sns.pairplot(returns_df, diag_kind='kde', corner=True,
                     plot_kws={'alpha': 0.5, 's': 30},
                     diag_kws={'fill': True})
    g.fig.suptitle('Returns Pair Plot', y=1.02, fontsize=14, fontweight='bold')
    
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'returns_pairplot.png'), dpi=150)
    plt.close()


def plot_anomaly_visualization(df, coin_name, save=True):
    """
    7. Anomaly Visualization
    """
    df = df.copy()
    
    # Calculate Z-Score
    mean = df['price'].mean()
    std = df['price'].std()
    df['zscore'] = (df['price'] - mean) / std
    df['is_anomaly'] = abs(df['zscore']) > 2.5
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Price + Anomalies
    normal = df[~df['is_anomaly']]
    anomaly = df[df['is_anomaly']]
    
    axes[0].plot(df['timestamp'], df['price'], color='#3498db', alpha=0.7, label='Price')
    axes[0].scatter(anomaly['timestamp'], anomaly['price'], color='red', s=100, 
                    label=f'Anomaly ({len(anomaly)} points)', zorder=5, edgecolors='black')
    axes[0].axhline(y=mean, color='green', linestyle='--', label=f'Mean: ${mean:,.0f}')
    axes[0].axhline(y=mean + 2.5*std, color='orange', linestyle=':', label='±2.5 Std')
    axes[0].axhline(y=mean - 2.5*std, color='orange', linestyle=':')
    axes[0].set_title(f'{coin_name} - Anomaly Detection (Z-Score)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Price (USD)')
    axes[0].legend(loc='upper left')
    
    # Z-Score time series
    colors = ['#e74c3c' if x else '#3498db' for x in df['is_anomaly']]
    axes[1].bar(df['timestamp'], df['zscore'], color=colors, width=0.8)
    axes[1].axhline(y=2.5, color='red', linestyle='--', label='Threshold (±2.5)')
    axes[1].axhline(y=-2.5, color='red', linestyle='--')
    axes[1].axhline(y=0, color='black', linewidth=0.5)
    axes[1].set_title('Z-Score Time Series', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Date')
    axes[1].set_ylabel('Z-Score')
    axes[1].legend()
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_anomaly_detection.png'), dpi=150)
    plt.close()


def generate_summary_dashboard(coins_data, save=True):
    """
    8. Summary Dashboard
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Layout
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, :2])  # Price trend (wide)
    ax2 = fig.add_subplot(gs[0, 2])   # Volatility bar
    ax3 = fig.add_subplot(gs[1, 0])   # Correlation
    ax4 = fig.add_subplot(gs[1, 1])   # Return distribution
    ax5 = fig.add_subplot(gs[1, 2])   # Box plot
    ax6 = fig.add_subplot(gs[2, :])   # Risk-Return scatter (wide)
    
    # 1. Price Trend (normalized)
    for coin_name, df in list(coins_data.items())[:5]:
        if df is not None and 'price' in df.columns:
            normalized = df['price'] / df['price'].iloc[0] * 100
            ax1.plot(df['timestamp'], normalized, label=coin_name, linewidth=2)
    ax1.set_title('Normalized Price Trend (Start=100)', fontweight='bold')
    ax1.set_ylabel('Index')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    # 2. Volatility
    vol_data = []
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            vol_data.append({'coin': coin_name[:6], 'vol': df['daily_return'].std()})
    if vol_data:
        vol_df = pd.DataFrame(vol_data).sort_values('vol', ascending=False).head(8)
        sns.barplot(data=vol_df, x='coin', y='vol', ax=ax2, palette='Reds_r')
        ax2.set_title('Volatility', fontweight='bold')
        ax2.set_xlabel('')
        ax2.tick_params(axis='x', rotation=45)
    
    # 3. Correlation (mini)
    price_df = pd.DataFrame()
    for coin_name, df in list(coins_data.items())[:5]:
        if df is not None:
            price_df[coin_name[:4]] = df.set_index('timestamp')['price']
    if not price_df.empty:
        corr = price_df.pct_change().dropna().corr()
        sns.heatmap(corr, annot=True, fmt='.1f', cmap='RdYlGn', center=0, ax=ax3, 
                    cbar=False, square=True, annot_kws={'size': 8})
        ax3.set_title('Correlation', fontweight='bold')
    
    # 4. Return Distribution (all coins)
    all_returns = []
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            all_returns.extend(df['daily_return'].dropna().tolist())
    if all_returns:
        sns.histplot(all_returns, kde=True, ax=ax4, color='#9b59b6', bins=40)
        ax4.axvline(x=0, color='red', linestyle='--')
        ax4.set_title('All Returns Distribution', fontweight='bold')
        ax4.set_xlabel('Daily Return (%)')
    
    # 5. Box Plot comparison
    box_data = []
    for coin_name, df in list(coins_data.items())[:6]:
        if df is not None and 'daily_return' in df.columns:
            for ret in df['daily_return'].dropna():
                box_data.append({'coin': coin_name[:6], 'return': ret})
    if box_data:
        box_df = pd.DataFrame(box_data)
        sns.boxplot(data=box_df, x='coin', y='return', ax=ax5, palette='Set2')
        ax5.set_title('Return Box Plot', fontweight='bold')
        ax5.set_xlabel('')
        ax5.tick_params(axis='x', rotation=45)
        ax5.set_ylim(-15, 15)
    
    # 6. Risk-Return Scatter
    scatter_data = []
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            returns = df['daily_return'].dropna()
            scatter_data.append({
                'coin': coin_name,
                'risk': returns.std(),
                'return': returns.mean(),
                'sharpe': returns.mean() / returns.std() if returns.std() > 0 else 0
            })
    if scatter_data:
        scatter_df = pd.DataFrame(scatter_data)
        colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in scatter_df['return']]
        ax6.scatter(scatter_df['risk'], scatter_df['return'], c=colors, s=150, alpha=0.7, edgecolors='black')
        for _, row in scatter_df.iterrows():
            ax6.annotate(row['coin'][:8], (row['risk'], row['return']), fontsize=8, ha='center', va='bottom')
        ax6.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
        ax6.axvline(x=scatter_df['risk'].mean(), color='gray', linestyle='--', alpha=0.5)
        ax6.set_title('Risk-Return Profile (Green: Positive, Red: Negative)', fontweight='bold')
        ax6.set_xlabel('Risk (Volatility %)')
        ax6.set_ylabel('Average Return (%)')
    
    plt.suptitle('📊 Crypto Analysis Dashboard', fontsize=16, fontweight='bold', y=1.01)
    
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'summary_dashboard.png'), dpi=150, bbox_inches='tight')
    plt.close()


def main():
    """Main function - run all analyses"""
    # Coins to analyze
    target_coins = ['bitcoin', 'ethereum', 'solana', 'cardano', 'ripple', 
                    'dogecoin', 'polkadot', 'avalanche-2', 'chainlink', 'litecoin']
    
    coins_data = {}
    
    for coin in target_coins:
        df = load_coin_data(coin)
        if df is not None and len(df) > 10:
            coins_data[coin] = df
    
    if not coins_data:
        return
    
    # 1. Individual analyses for each coin
    for coin_name, df in list(coins_data.items())[:3]:  # First 3 coins
        plot_price_distribution(df, coin_name)
        plot_returns_analysis(df, coin_name)
        plot_time_series(df, coin_name)
        plot_anomaly_visualization(df, coin_name)
    
    # 2. Comparative analyses
    plot_correlation_heatmap(coins_data)
    plot_volatility_comparison(coins_data)
    plot_statistical_summary(coins_data)
    
    # 3. Summary Dashboard
    generate_summary_dashboard(coins_data)


if __name__ == '__main__':
    main()
