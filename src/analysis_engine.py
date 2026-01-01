"""
Crypto Analysis Engine - Teknik analiz ve risk metrikleri hesaplama modülü
"""
import pandas as pd
import numpy as np


class CryptoAnalysisEngine:
    """
    Kripto para verileri için teknik analiz ve risk metrikleri hesaplayan modül.
    """

    # ==================== TEKNİK GÖSTERGELER ====================
    
    def calculate_sma(self, df, column='price', periods=[7, 14, 30]):
        """Simple Moving Average (Basit Hareketli Ortalama)"""
        df = df.copy()
        for period in periods:
            df[f'sma_{period}'] = df[column].rolling(window=period).mean()
        return df

    def calculate_ema(self, df, column='price', periods=[7, 14, 30]):
        """Exponential Moving Average (Üssel Hareketli Ortalama)"""
        df = df.copy()
        for period in periods:
            df[f'ema_{period}'] = df[column].ewm(span=period, adjust=False).mean()
        return df

    def calculate_rsi(self, df, column='price', period=14):
        """
        Relative Strength Index (Göreceli Güç Endeksi)
        RSI > 70: Aşırı alım (overbought)
        RSI < 30: Aşırı satım (oversold)
        """
        df = df.copy()
        delta = df[column].diff()
        
        gain = delta.where(delta > 0, 0)
        loss = (-delta).where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / (avg_loss + 1e-10)  # Division by zero koruması
        df['rsi'] = 100 - (100 / (1 + rs))
        
        return df

    def calculate_macd(self, df, column='price', fast=12, slow=26, signal=9):
        """
        MACD (Moving Average Convergence Divergence)
        Trend takip göstergesi
        """
        df = df.copy()
        ema_fast = df[column].ewm(span=fast, adjust=False).mean()
        ema_slow = df[column].ewm(span=slow, adjust=False).mean()
        
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=signal, adjust=False).mean()
        df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df

    def calculate_bollinger_bands(self, df, column='price', period=20, std_dev=2):
        """
        Bollinger Bands (Bollinger Bantları)
        Volatilite ve fiyat seviyelerini gösterir
        """
        df = df.copy()
        sma = df[column].rolling(window=period).mean()
        std = df[column].rolling(window=period).std()
        
        df['bb_middle'] = sma
        df['bb_upper'] = sma + (std * std_dev)
        df['bb_lower'] = sma - (std * std_dev)
        df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle'] * 100
        
        return df

    # ==================== RİSK METRİKLERİ ====================
    
    def calculate_volatility(self, df, column='price', periods=[7, 30]):
        """
        Volatilite hesaplama (günlük getiri standart sapması)
        """
        df = df.copy()
        df['daily_return'] = df[column].pct_change()
        
        for period in periods:
            df[f'volatility_{period}d'] = df['daily_return'].rolling(window=period).std() * np.sqrt(period) * 100
        
        return df

    def calculate_max_drawdown(self, df, column='price'):
        """
        Maximum Drawdown - En yüksek noktadan en büyük düşüş
        Risk ölçümü için kritik metrik
        """
        df = df.copy()
        rolling_max = df[column].expanding().max()
        drawdown = (df[column] - rolling_max) / rolling_max * 100
        
        df['drawdown'] = drawdown
        df['max_drawdown'] = drawdown.expanding().min()
        
        return df

    def calculate_sharpe_ratio(self, df, column='price', risk_free_rate=0.02, period=30):
        """
        Sharpe Ratio - Risk ayarlı getiri
        Yüksek değer = iyi risk/getiri oranı
        """
        df = df.copy()
        df['daily_return'] = df[column].pct_change()
        
        # Yıllık risk-free rate'i günlüğe çevir
        daily_rf = risk_free_rate / 365
        
        excess_return = df['daily_return'] - daily_rf
        
        mean_excess = excess_return.rolling(window=period).mean()
        std_excess = excess_return.rolling(window=period).std()
        
        # Yıllık Sharpe Ratio
        df['sharpe_ratio'] = (mean_excess / (std_excess + 1e-10)) * np.sqrt(365)
        
        return df

    def calculate_beta(self, coin_df, benchmark_df, column='price', period=30):
        """
        Beta - Piyasa (benchmark) ile korelasyon/hassasiyet
        Beta > 1: Piyasadan daha volatil
        Beta < 1: Piyasadan daha az volatil
        """
        coin_returns = coin_df[column].pct_change()
        bench_returns = benchmark_df[column].pct_change()
        
        # Aynı uzunlukta olduklarından emin ol
        min_len = min(len(coin_returns), len(bench_returns))
        coin_returns = coin_returns.tail(min_len)
        bench_returns = bench_returns.tail(min_len)
        
        covariance = coin_returns.rolling(window=period).cov(bench_returns)
        variance = bench_returns.rolling(window=period).var()
        
        beta = covariance / (variance + 1e-10)
        
        return beta

    # ==================== TREND ANALİZİ ====================
    
    def detect_trend(self, df, column='price', short_period=7, long_period=30):
        """
        Trend tespiti
        Returns: 'bullish', 'bearish', 'neutral'
        """
        df = df.copy()
        df['sma_short'] = df[column].rolling(window=short_period).mean()
        df['sma_long'] = df[column].rolling(window=long_period).mean()
        
        def get_trend(row):
            if pd.isna(row['sma_short']) or pd.isna(row['sma_long']):
                return 'neutral'
            if row['sma_short'] > row['sma_long'] * 1.02:
                return 'bullish'
            elif row['sma_short'] < row['sma_long'] * 0.98:
                return 'bearish'
            return 'neutral'
        
        df['trend'] = df.apply(get_trend, axis=1)
        
        return df

    def calculate_support_resistance(self, df, column='price', period=30):
        """
        Destek ve direnç seviyelerini hesapla
        """
        recent = df[column].tail(period)
        
        support = recent.min()
        resistance = recent.max()
        pivot = (support + resistance + recent.iloc[-1]) / 3
        
        return {
            'support': support,
            'resistance': resistance,
            'pivot': pivot,
            'r1': 2 * pivot - support,
            's1': 2 * pivot - resistance
        }

    # ==================== ÖZET ANALİZ ====================
    
    def get_full_analysis(self, df, column='price'):
        """
        Tüm analizleri birleştir ve özet döndür
        """
        df = df.copy()
        
        # Tüm göstergeleri hesapla
        df = self.calculate_sma(df, column, [7, 30])
        df = self.calculate_ema(df, column, [7, 30])
        df = self.calculate_rsi(df, column)
        df = self.calculate_macd(df, column)
        df = self.calculate_bollinger_bands(df, column)
        df = self.calculate_volatility(df, column)
        df = self.calculate_max_drawdown(df, column)
        df = self.calculate_sharpe_ratio(df, column)
        df = self.detect_trend(df, column)
        
        # Son değerleri al
        latest = df.iloc[-1]
        
        # RSI yorumu
        rsi_value = latest.get('rsi', 50)
        if rsi_value > 70:
            rsi_signal = 'overbought'
        elif rsi_value < 30:
            rsi_signal = 'oversold'
        else:
            rsi_signal = 'neutral'
        
        # MACD yorumu
        macd_signal = 'bullish' if latest.get('macd_histogram', 0) > 0 else 'bearish'
        
        # Bollinger pozisyonu
        current_price = latest[column]
        bb_upper = latest.get('bb_upper', current_price)
        bb_lower = latest.get('bb_lower', current_price)
        bb_middle = latest.get('bb_middle', current_price)
        
        if current_price > bb_upper:
            bb_position = 'above_upper'
        elif current_price < bb_lower:
            bb_position = 'below_lower'
        elif current_price > bb_middle:
            bb_position = 'upper_half'
        else:
            bb_position = 'lower_half'
        
        support_resistance = self.calculate_support_resistance(df, column)
        
        return {
            'current_price': current_price,
            'indicators': {
                'sma_7': latest.get('sma_7'),
                'sma_30': latest.get('sma_30'),
                'ema_7': latest.get('ema_7'),
                'ema_30': latest.get('ema_30'),
                'rsi': rsi_value,
                'rsi_signal': rsi_signal,
                'macd': latest.get('macd'),
                'macd_signal_line': latest.get('macd_signal'),
                'macd_histogram': latest.get('macd_histogram'),
                'macd_trend': macd_signal,
                'bb_upper': bb_upper,
                'bb_middle': bb_middle,
                'bb_lower': bb_lower,
                'bb_width': latest.get('bb_width'),
                'bb_position': bb_position
            },
            'risk_metrics': {
                'volatility_7d': latest.get('volatility_7d'),
                'volatility_30d': latest.get('volatility_30d'),
                'max_drawdown': latest.get('max_drawdown'),
                'sharpe_ratio': latest.get('sharpe_ratio')
            },
            'trend': {
                'direction': latest.get('trend', 'neutral'),
                'sma_short': latest.get('sma_short'),
                'sma_long': latest.get('sma_long')
            },
            'levels': support_resistance,
            'dataframe': df
        }

    def calculate_correlation_matrix(self, coin_dataframes):
        """
        Birden fazla coin için korelasyon matrisi hesapla
        coin_dataframes: {'bitcoin': df1, 'ethereum': df2, ...}
        """
        returns = {}
        for coin_name, df in coin_dataframes.items():
            if 'price' in df.columns:
                returns[coin_name] = df['price'].pct_change()
        
        returns_df = pd.DataFrame(returns).dropna()
        correlation_matrix = returns_df.corr()
        
        return correlation_matrix.to_dict()

    # ==================== ANOMALY DETECTION (DATA SCIENCE) ====================
    
    def detect_anomalies_zscore(self, df, column='price', threshold=3.0):
        """
        Z-Score tabanlı anomali tespiti
        threshold: Kaç standart sapma dışındaki değerler anomali sayılacak
        """
        df = df.copy()
        mean = df[column].mean()
        std = df[column].std()
        
        df['zscore'] = (df[column] - mean) / (std + 1e-10)
        df['is_anomaly_zscore'] = abs(df['zscore']) > threshold
        
        return df
    
    def detect_anomalies_iqr(self, df, column='price', multiplier=1.5):
        """
        IQR (Interquartile Range) tabanlı anomali tespiti
        Daha robust bir yöntem - outlier'lara duyarlı değil
        """
        df = df.copy()
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        df['iqr_lower_bound'] = lower_bound
        df['iqr_upper_bound'] = upper_bound
        df['is_anomaly_iqr'] = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        return df
    
    def detect_anomalies_rolling(self, df, column='price', window=20, threshold=2.5):
        """
        Rolling window tabanlı anomali tespiti
        Zamana bağlı trendleri dikkate alır
        """
        df = df.copy()
        rolling_mean = df[column].rolling(window=window).mean()
        rolling_std = df[column].rolling(window=window).std()
        
        df['rolling_zscore'] = (df[column] - rolling_mean) / (rolling_std + 1e-10)
        df['is_anomaly_rolling'] = abs(df['rolling_zscore']) > threshold
        
        return df
    
    def detect_price_spikes(self, df, column='price', pct_threshold=0.10):
        """
        Ani fiyat değişimlerini tespit et
        pct_threshold: Yüzdelik değişim eşiği (0.10 = %10)
        """
        df = df.copy()
        df['pct_change'] = df[column].pct_change()
        df['is_spike'] = abs(df['pct_change']) > pct_threshold
        df['spike_direction'] = df['pct_change'].apply(
            lambda x: 'up' if x > pct_threshold else ('down' if x < -pct_threshold else 'none')
        )
        
        return df
    
    def get_anomaly_summary(self, df, column='price'):
        """
        Tüm anomali tespit yöntemlerini birleştir ve özet döndür
        """
        df = df.copy()
        
        # Tüm anomali tespitlerini uygula
        df = self.detect_anomalies_zscore(df, column)
        df = self.detect_anomalies_iqr(df, column)
        df = self.detect_anomalies_rolling(df, column)
        df = self.detect_price_spikes(df, column)
        
        # En az bir yöntemle tespit edilen anomaliler
        df['is_anomaly_any'] = (
            df['is_anomaly_zscore'] | 
            df['is_anomaly_iqr'] | 
            df['is_anomaly_rolling'] |
            df['is_spike']
        )
        
        # Anomali sayısını ve yüzdesini hesapla
        total_points = len(df)
        anomaly_counts = {
            'zscore': df['is_anomaly_zscore'].sum(),
            'iqr': df['is_anomaly_iqr'].sum(),
            'rolling': df['is_anomaly_rolling'].sum(),
            'price_spike': df['is_spike'].sum(),
            'any_method': df['is_anomaly_any'].sum()
        }
        
        # Anomali tarihlerini listele
        anomaly_dates = df[df['is_anomaly_any']]['timestamp'].tolist() if 'timestamp' in df.columns else []
        
        return {
            'total_data_points': total_points,
            'anomaly_counts': anomaly_counts,
            'anomaly_percentage': round((anomaly_counts['any_method'] / total_points) * 100, 2),
            'anomaly_dates': anomaly_dates[-10:],  # Son 10 anomali
            'statistics': {
                'mean': df[column].mean(),
                'std': df[column].std(),
                'min': df[column].min(),
                'max': df[column].max(),
                'q1': df[column].quantile(0.25),
                'median': df[column].quantile(0.50),
                'q3': df[column].quantile(0.75),
                'iqr': df[column].quantile(0.75) - df[column].quantile(0.25),
                'skewness': df[column].skew(),
                'kurtosis': df[column].kurtosis()
            },
            'dataframe': df
        }

    # ==================== ADVANCED STATISTICAL ANALYSIS ====================
    
    def calculate_descriptive_statistics(self, df, column='price'):
        """
        Kapsamlı tanımlayıcı istatistikler
        """
        data = df[column].dropna()
        
        return {
            'count': len(data),
            'mean': data.mean(),
            'std': data.std(),
            'min': data.min(),
            'max': data.max(),
            'range': data.max() - data.min(),
            'variance': data.var(),
            'q1': data.quantile(0.25),
            'median': data.quantile(0.50),
            'q3': data.quantile(0.75),
            'iqr': data.quantile(0.75) - data.quantile(0.25),
            'skewness': data.skew(),
            'kurtosis': data.kurtosis(),
            'coefficient_of_variation': (data.std() / data.mean()) * 100 if data.mean() != 0 else 0
        }
    
    def calculate_returns_analysis(self, df, column='price'):
        """
        Getiri analizi - Günlük, haftalık, aylık
        """
        df = df.copy()
        df['daily_return'] = df[column].pct_change()
        df['log_return'] = np.log(df[column] / df[column].shift(1))
        
        daily_returns = df['daily_return'].dropna()
        
        return {
            'daily_returns': {
                'mean': daily_returns.mean() * 100,
                'std': daily_returns.std() * 100,
                'min': daily_returns.min() * 100,
                'max': daily_returns.max() * 100,
                'positive_days': (daily_returns > 0).sum(),
                'negative_days': (daily_returns < 0).sum(),
                'win_rate': ((daily_returns > 0).sum() / len(daily_returns)) * 100
            },
            'cumulative_return': ((df[column].iloc[-1] / df[column].iloc[0]) - 1) * 100,
            'annualized_return': ((1 + daily_returns.mean()) ** 365 - 1) * 100,
            'annualized_volatility': daily_returns.std() * np.sqrt(365) * 100
        }
    
    def calculate_risk_analysis(self, df, column='price', confidence_level=0.95):
        """
        Risk analizi - VaR, CVaR, Maximum Drawdown
        """
        df = df.copy()
        df['daily_return'] = df[column].pct_change()
        returns = df['daily_return'].dropna()
        
        # Value at Risk (VaR) - Parametrik
        mean_return = returns.mean()
        std_return = returns.std()
        z_score = 1.645 if confidence_level == 0.95 else 2.326  # 95% veya 99%
        var_parametric = mean_return - z_score * std_return
        
        # Value at Risk (VaR) - Historik
        var_historic = returns.quantile(1 - confidence_level)
        
        # Conditional VaR (CVaR / Expected Shortfall)
        cvar = returns[returns <= var_historic].mean()
        
        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        rolling_max = cumulative.expanding().max()
        drawdowns = (cumulative - rolling_max) / rolling_max
        max_drawdown = drawdowns.min()
        
        return {
            'var_parametric_95': var_parametric * 100,
            'var_historic_95': var_historic * 100,
            'cvar_95': cvar * 100 if not np.isnan(cvar) else None,
            'max_drawdown': max_drawdown * 100,
            'confidence_level': confidence_level * 100,
            'interpretation': {
                'var_meaning': f"1 günde %{confidence_level*100} olasılıkla en fazla %{abs(var_historic)*100:.2f} kayıp",
                'max_drawdown_meaning': f"En yüksek noktadan en düşüğe %{abs(max_drawdown)*100:.2f} düşüş"
            }
        }
    
    def generate_scientific_report(self, df, column='price', coin_name='Unknown'):
        """
        Kapsamlı bilimsel rapor oluştur
        """
        df = df.copy()
        
        # Tüm analizleri çalıştır
        descriptive = self.calculate_descriptive_statistics(df, column)
        returns = self.calculate_returns_analysis(df, column)
        risk = self.calculate_risk_analysis(df, column)
        anomalies = self.get_anomaly_summary(df, column)
        
        # Trend analizi
        df_trend = self.detect_trend(df, column)
        trend_counts = df_trend['trend'].value_counts().to_dict()
        
        return {
            'coin': coin_name,
            'analysis_period': {
                'start': df['timestamp'].iloc[0].isoformat() if 'timestamp' in df.columns else None,
                'end': df['timestamp'].iloc[-1].isoformat() if 'timestamp' in df.columns else None,
                'total_days': len(df)
            },
            'descriptive_statistics': descriptive,
            'returns_analysis': returns,
            'risk_analysis': risk,
            'anomaly_detection': {
                'total_anomalies': anomalies['anomaly_counts']['any_method'],
                'anomaly_percentage': anomalies['anomaly_percentage'],
                'by_method': anomalies['anomaly_counts']
            },
            'trend_analysis': {
                'current_trend': df_trend['trend'].iloc[-1],
                'trend_distribution': trend_counts
            },
            'data_quality': {
                'missing_values': df[column].isna().sum(),
                'data_completeness': ((len(df) - df[column].isna().sum()) / len(df)) * 100
            }
        }
# ==================== USER PORTFOLIO ANALYSIS ====================
    
    def analyze_user_performance(self, user_data, current_market_prices):
        """
        Kullanıcının portföyünü piyasa verileriyle karşılaştırıp performans analizi yapar.
        current_market_prices: {'bitcoin': 64000, 'ethereum': 3500, ...} gibi bir sözlük bekler.
        """
        portfolio_report = []
        total_pnl = 0 # Toplam Kar/Zarar
        
        for trade in user_data.get('trades', []):
            coin = trade['coin']
            buy_price = trade['buy_price']
            amount = trade['amount']
            
            # Eğer bu coin için güncel fiyat market verisinde yoksa alış fiyatını baz al
            current_price = current_market_prices.get(coin, buy_price)
            
            # Kar/Zarar Hesaplamaları
            pnl = (current_price - buy_price) * amount
            pnl_percent = ((current_price - buy_price) / (buy_price + 1e-10)) * 100
            
            portfolio_report.append({
                "coin": coin,
                "amount": amount,
                "buy_price": buy_price,
                "current_price": current_price,
                "pnl": round(pnl, 2),
                "pnl_percent": round(pnl_percent, 2)
            })
            total_pnl += pnl
            
        return {
            "username": user_data.get('username'),
            "wallet_balance": user_data.get('wallet_balance'),
            "total_pnl": round(total_pnl, 2),
            "overall_status": "Profit" if total_pnl > 0 else "Loss",
            "portfolio_details": portfolio_report
        }
# ==================== GLOBAL EXCHANGE ANALYSIS ====================
    
    def calculate_exchange_overview(self, all_users, current_market_prices):
        """
        Tüm borsa verilerini analiz eder.
        """
        total_liquidity = 0
        user_performances = []
        coin_counts = {}

        for user in all_users:
            total_liquidity += user.get('wallet_balance', 0)
            
            user_buy_val = 0
            user_curr_val = 0
            
            for trade in user.get('trades', []):
                coin = trade['coin']
                amount = trade['amount']
                buy_p = trade['buy_price']
                curr_p = current_market_prices.get(coin, buy_p)
                
                user_buy_val += buy_p * amount
                user_curr_val += curr_p * amount
                
                # Popülerlik sayacı
                coin_counts[coin] = coin_counts.get(coin, 0) + 1
            
            # Kullanıcının toplam başarı yüzdesi
            pnl_perc = ((user_curr_val - user_buy_val) / (user_buy_val + 1e-10)) * 100
            user_performances.append({
                "username": user.get('username'),
                "pnl_percent": round(pnl_perc, 2)
            })

        # Borsanın Kralı (En yüksek % kâr)
        king = max(user_performances, key=lambda x: x['pnl_percent']) if user_performances else None
        
        # En popüler coin
        popular = max(coin_counts, key=coin_counts.get) if coin_counts else "N/A"

        return {
            "king": king,
            "total_liquidity": round(total_liquidity, 2),
            "most_popular_coin": popular.upper(),
            "total_investors": len(all_users)
        }