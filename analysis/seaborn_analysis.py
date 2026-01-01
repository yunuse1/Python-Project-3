"""
Seaborn ile Kripto Para Analizi
===============================
Bu script, MongoDB'deki kripto para verilerini Seaborn ile görselleştirir.
Çıktılar: analysis/plots/ klasörüne kaydedilir.

Kullanım:
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

# Seaborn stil ayarları
sns.set_theme(style="darkgrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

# Çıktı klasörü
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'plots')
os.makedirs(OUTPUT_DIR, exist_ok=True)


def load_coin_data(coin_id):
    """Coin verilerini yükle ve temizle"""
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
    
    # Günlük getiri hesapla
    df['daily_return'] = df['price'].pct_change() * 100
    df['log_return'] = np.log(df['price'] / df['price'].shift(1)) * 100
    
    return df


def plot_price_distribution(df, coin_name, save=True):
    """
    1. Fiyat Dağılımı - Histogram + KDE
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram + KDE
    sns.histplot(data=df, x='price', kde=True, ax=axes[0], color='#3498db', bins=30)
    axes[0].set_title(f'{coin_name} - Fiyat Dağılımı', fontsize=14, fontweight='bold')
    axes[0].set_xlabel('Fiyat (USD)')
    axes[0].set_ylabel('Frekans')
    
    # Box Plot
    sns.boxplot(data=df, y='price', ax=axes[1], color='#2ecc71')
    axes[1].set_title(f'{coin_name} - Fiyat Box Plot', fontsize=14, fontweight='bold')
    axes[1].set_ylabel('Fiyat (USD)')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_price_distribution.png'), dpi=150)
        print(f"✅ Saved: {coin_name}_price_distribution.png")
    plt.close()


def plot_returns_analysis(df, coin_name, save=True):
    """
    2. Getiri Analizi - Histogram, Violin, Box
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    returns = df['daily_return'].dropna()
    
    # Getiri Histogram + KDE
    sns.histplot(returns, kde=True, ax=axes[0, 0], color='#9b59b6', bins=30)
    axes[0, 0].axvline(x=0, color='red', linestyle='--', linewidth=2)
    axes[0, 0].set_title('Günlük Getiri Dağılımı', fontsize=12, fontweight='bold')
    axes[0, 0].set_xlabel('Günlük Getiri (%)')
    
    # Violin Plot
    sns.violinplot(y=returns, ax=axes[0, 1], color='#e74c3c')
    axes[0, 1].axhline(y=0, color='black', linestyle='--', linewidth=1)
    axes[0, 1].set_title('Getiri Violin Plot', fontsize=12, fontweight='bold')
    axes[0, 1].set_ylabel('Günlük Getiri (%)')
    
    # QQ Plot (Normal dağılıma karşı)
    from scipy import stats
    stats.probplot(returns, dist="norm", plot=axes[1, 0])
    axes[1, 0].set_title('Q-Q Plot (Normal Dağılım)', fontsize=12, fontweight='bold')
    
    # Strip Plot (zaman içinde getiriler)
    if len(returns) > 0:
        return_categories = pd.cut(returns, bins=[-np.inf, -5, -2, 0, 2, 5, np.inf], 
                                   labels=['<-5%', '-5 to -2%', '-2 to 0%', '0 to 2%', '2 to 5%', '>5%'])
        category_counts = return_categories.value_counts()
        sns.barplot(x=category_counts.index, y=category_counts.values, ax=axes[1, 1], palette='RdYlGn')
        axes[1, 1].set_title('Getiri Kategori Dağılımı', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel('Getiri Aralığı')
        axes[1, 1].set_ylabel('Gün Sayısı')
        axes[1, 1].tick_params(axis='x', rotation=45)
    
    plt.suptitle(f'{coin_name} - Getiri Analizi', fontsize=14, fontweight='bold', y=1.02)
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_returns_analysis.png'), dpi=150)
        print(f"✅ Saved: {coin_name}_returns_analysis.png")
    plt.close()


def plot_time_series(df, coin_name, save=True):
    """
    3. Zaman Serisi Analizi
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 12))
    
    # Fiyat trendi
    sns.lineplot(data=df, x='timestamp', y='price', ax=axes[0], color='#3498db', linewidth=2)
    axes[0].fill_between(df['timestamp'], df['price'], alpha=0.3)
    axes[0].set_title(f'{coin_name} - Fiyat Trendi', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('')
    axes[0].set_ylabel('Fiyat (USD)')
    
    # Rolling Mean + Std
    df['rolling_mean'] = df['price'].rolling(window=7).mean()
    df['rolling_std'] = df['price'].rolling(window=7).std()
    
    axes[1].plot(df['timestamp'], df['price'], label='Fiyat', alpha=0.5)
    axes[1].plot(df['timestamp'], df['rolling_mean'], label='7-Gün Ortalama', color='red', linewidth=2)
    axes[1].fill_between(df['timestamp'], 
                         df['rolling_mean'] - 2*df['rolling_std'],
                         df['rolling_mean'] + 2*df['rolling_std'],
                         alpha=0.2, color='red', label='±2 Std')
    axes[1].set_title('Fiyat + Rolling Statistics', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('')
    axes[1].set_ylabel('Fiyat (USD)')
    axes[1].legend(loc='upper left')
    
    # Günlük Getiri Bar
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['daily_return'].fillna(0)]
    axes[2].bar(df['timestamp'], df['daily_return'].fillna(0), color=colors, width=0.8)
    axes[2].axhline(y=0, color='black', linewidth=0.5)
    axes[2].set_title('Günlük Getiri', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Tarih')
    axes[2].set_ylabel('Getiri (%)')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_time_series.png'), dpi=150)
        print(f"✅ Saved: {coin_name}_time_series.png")
    plt.close()


def plot_correlation_heatmap(coins_data, save=True):
    """
    4. Korelasyon Isı Haritası
    """
    # Tüm coinlerin fiyatlarını birleştir
    price_df = pd.DataFrame()
    for coin_name, df in coins_data.items():
        if df is not None and 'price' in df.columns:
            price_df[coin_name] = df.set_index('timestamp')['price']
    
    if price_df.empty:
        print("⚠️ Korelasyon hesaplanamadı - yeterli veri yok")
        return
    
    # Getiri korelasyonu
    returns_df = price_df.pct_change().dropna()
    correlation = returns_df.corr()
    
    plt.figure(figsize=(12, 10))
    mask = np.triu(np.ones_like(correlation, dtype=bool))
    
    sns.heatmap(correlation, mask=mask, annot=True, fmt='.2f', 
                cmap='RdYlGn', center=0, 
                square=True, linewidths=0.5,
                cbar_kws={"shrink": 0.8, "label": "Korelasyon"})
    
    plt.title('Kripto Para Getiri Korelasyonu', fontsize=14, fontweight='bold')
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'correlation_heatmap.png'), dpi=150)
        print("✅ Saved: correlation_heatmap.png")
    plt.close()


def plot_volatility_comparison(coins_data, save=True):
    """
    5. Volatilite Karşılaştırması
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
    
    # Volatilite Bar
    sns.barplot(data=vol_df.sort_values('volatility', ascending=False), 
                x='coin', y='volatility', ax=axes[0], palette='Reds_r')
    axes[0].set_title('Günlük Volatilite', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Coin')
    axes[0].set_ylabel('Std Sapma (%)')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Ortalama Getiri Bar
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in vol_df.sort_values('mean_return', ascending=False)['mean_return']]
    sns.barplot(data=vol_df.sort_values('mean_return', ascending=False), 
                x='coin', y='mean_return', ax=axes[1], palette=colors)
    axes[1].set_title('Ortalama Günlük Getiri', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Coin')
    axes[1].set_ylabel('Ortalama (%)')
    axes[1].axhline(y=0, color='black', linestyle='--')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Risk-Return Scatter
    sns.scatterplot(data=vol_df, x='volatility', y='mean_return', 
                    hue='coin', s=200, ax=axes[2])
    axes[2].axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    axes[2].axvline(x=vol_df['volatility'].mean(), color='gray', linestyle='--', alpha=0.5)
    axes[2].set_title('Risk-Getiri Profili', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Volatilite (Risk)')
    axes[2].set_ylabel('Ortalama Getiri')
    axes[2].legend(loc='best')
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'volatility_comparison.png'), dpi=150)
        print("✅ Saved: volatility_comparison.png")
    plt.close()


def plot_statistical_summary(coins_data, save=True):
    """
    6. İstatistiksel Özet - Pair Plot ve Joint Plot
    """
    # En fazla 4 coin ile pair plot
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
    g.fig.suptitle('Getiri Pair Plot', y=1.02, fontsize=14, fontweight='bold')
    
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'returns_pairplot.png'), dpi=150)
        print("✅ Saved: returns_pairplot.png")
    plt.close()


def plot_anomaly_visualization(df, coin_name, save=True):
    """
    7. Anomali Görselleştirme
    """
    df = df.copy()
    
    # Z-Score hesapla
    mean = df['price'].mean()
    std = df['price'].std()
    df['zscore'] = (df['price'] - mean) / std
    df['is_anomaly'] = abs(df['zscore']) > 2.5
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Fiyat + Anomaliler
    normal = df[~df['is_anomaly']]
    anomaly = df[df['is_anomaly']]
    
    axes[0].plot(df['timestamp'], df['price'], color='#3498db', alpha=0.7, label='Fiyat')
    axes[0].scatter(anomaly['timestamp'], anomaly['price'], color='red', s=100, 
                    label=f'Anomali ({len(anomaly)} adet)', zorder=5, edgecolors='black')
    axes[0].axhline(y=mean, color='green', linestyle='--', label=f'Ortalama: ${mean:,.0f}')
    axes[0].axhline(y=mean + 2.5*std, color='orange', linestyle=':', label='±2.5 Std')
    axes[0].axhline(y=mean - 2.5*std, color='orange', linestyle=':')
    axes[0].set_title(f'{coin_name} - Anomali Tespiti (Z-Score)', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Fiyat (USD)')
    axes[0].legend(loc='upper left')
    
    # Z-Score zaman serisi
    colors = ['#e74c3c' if x else '#3498db' for x in df['is_anomaly']]
    axes[1].bar(df['timestamp'], df['zscore'], color=colors, width=0.8)
    axes[1].axhline(y=2.5, color='red', linestyle='--', label='Eşik (±2.5)')
    axes[1].axhline(y=-2.5, color='red', linestyle='--')
    axes[1].axhline(y=0, color='black', linewidth=0.5)
    axes[1].set_title('Z-Score Zaman Serisi', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Tarih')
    axes[1].set_ylabel('Z-Score')
    axes[1].legend()
    
    plt.tight_layout()
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, f'{coin_name}_anomaly_detection.png'), dpi=150)
        print(f"✅ Saved: {coin_name}_anomaly_detection.png")
    plt.close()


def generate_summary_dashboard(coins_data, save=True):
    """
    8. Özet Dashboard
    """
    fig = plt.figure(figsize=(16, 12))
    
    # Layout
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    ax1 = fig.add_subplot(gs[0, :2])  # Fiyat trendi (geniş)
    ax2 = fig.add_subplot(gs[0, 2])   # Volatilite bar
    ax3 = fig.add_subplot(gs[1, 0])   # Korelasyon
    ax4 = fig.add_subplot(gs[1, 1])   # Getiri dağılımı
    ax5 = fig.add_subplot(gs[1, 2])   # Box plot
    ax6 = fig.add_subplot(gs[2, :])   # Risk-Return scatter (geniş)
    
    # 1. Fiyat Trendi (normalize edilmiş)
    for coin_name, df in list(coins_data.items())[:5]:
        if df is not None and 'price' in df.columns:
            normalized = df['price'] / df['price'].iloc[0] * 100
            ax1.plot(df['timestamp'], normalized, label=coin_name, linewidth=2)
    ax1.set_title('Normalize Fiyat Trendi (Başlangıç=100)', fontweight='bold')
    ax1.set_ylabel('İndeks')
    ax1.legend(loc='upper left', fontsize=8)
    ax1.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    
    # 2. Volatilite
    vol_data = []
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            vol_data.append({'coin': coin_name[:6], 'vol': df['daily_return'].std()})
    if vol_data:
        vol_df = pd.DataFrame(vol_data).sort_values('vol', ascending=False).head(8)
        sns.barplot(data=vol_df, x='coin', y='vol', ax=ax2, palette='Reds_r')
        ax2.set_title('Volatilite', fontweight='bold')
        ax2.set_xlabel('')
        ax2.tick_params(axis='x', rotation=45)
    
    # 3. Korelasyon (mini)
    price_df = pd.DataFrame()
    for coin_name, df in list(coins_data.items())[:5]:
        if df is not None:
            price_df[coin_name[:4]] = df.set_index('timestamp')['price']
    if not price_df.empty:
        corr = price_df.pct_change().dropna().corr()
        sns.heatmap(corr, annot=True, fmt='.1f', cmap='RdYlGn', center=0, ax=ax3, 
                    cbar=False, square=True, annot_kws={'size': 8})
        ax3.set_title('Korelasyon', fontweight='bold')
    
    # 4. Getiri Dağılımı (tüm coinler)
    all_returns = []
    for coin_name, df in coins_data.items():
        if df is not None and 'daily_return' in df.columns:
            all_returns.extend(df['daily_return'].dropna().tolist())
    if all_returns:
        sns.histplot(all_returns, kde=True, ax=ax4, color='#9b59b6', bins=40)
        ax4.axvline(x=0, color='red', linestyle='--')
        ax4.set_title('Tüm Getiri Dağılımı', fontweight='bold')
        ax4.set_xlabel('Günlük Getiri (%)')
    
    # 5. Box Plot karşılaştırma
    box_data = []
    for coin_name, df in list(coins_data.items())[:6]:
        if df is not None and 'daily_return' in df.columns:
            for ret in df['daily_return'].dropna():
                box_data.append({'coin': coin_name[:6], 'return': ret})
    if box_data:
        box_df = pd.DataFrame(box_data)
        sns.boxplot(data=box_df, x='coin', y='return', ax=ax5, palette='Set2')
        ax5.set_title('Getiri Box Plot', fontweight='bold')
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
        ax6.set_title('Risk-Getiri Profili (Yeşil: Pozitif, Kırmızı: Negatif)', fontweight='bold')
        ax6.set_xlabel('Risk (Volatilite %)')
        ax6.set_ylabel('Ortalama Getiri (%)')
    
    plt.suptitle('📊 Kripto Para Analiz Dashboard', fontsize=16, fontweight='bold', y=1.01)
    
    if save:
        plt.savefig(os.path.join(OUTPUT_DIR, 'summary_dashboard.png'), dpi=150, bbox_inches='tight')
        print("✅ Saved: summary_dashboard.png")
    plt.close()


def main():
    """Ana fonksiyon - tüm analizleri çalıştır"""
    print("=" * 60)
    print("🔬 Seaborn Kripto Para Analizi")
    print("=" * 60)
    
    # Analiz edilecek coinler
    target_coins = ['bitcoin', 'ethereum', 'solana', 'cardano', 'ripple', 
                    'dogecoin', 'polkadot', 'avalanche-2', 'chainlink', 'litecoin']
    
    print(f"\n📥 Veri yükleniyor ({len(target_coins)} coin)...")
    coins_data = {}
    
    for coin in target_coins:
        df = load_coin_data(coin)
        if df is not None and len(df) > 10:
            coins_data[coin] = df
            print(f"  ✓ {coin}: {len(df)} veri noktası")
        else:
            print(f"  ✗ {coin}: Veri bulunamadı")
    
    if not coins_data:
        print("\n❌ Hiç veri yüklenemedi! MongoDB bağlantısını kontrol edin.")
        return
    
    print(f"\n📊 Görselleştirmeler oluşturuluyor...")
    print("-" * 40)
    
    # 1. Her coin için bireysel analizler
    for coin_name, df in list(coins_data.items())[:3]:  # İlk 3 coin
        plot_price_distribution(df, coin_name)
        plot_returns_analysis(df, coin_name)
        plot_time_series(df, coin_name)
        plot_anomaly_visualization(df, coin_name)
    
    # 2. Karşılaştırmalı analizler
    plot_correlation_heatmap(coins_data)
    plot_volatility_comparison(coins_data)
    plot_statistical_summary(coins_data)
    
    # 3. Özet Dashboard
    generate_summary_dashboard(coins_data)
    
    print("-" * 40)
    print(f"\n✅ Tüm grafikler kaydedildi: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == '__main__':
    main()
