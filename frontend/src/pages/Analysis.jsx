import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area, BarChart, Bar, ReferenceLine } from 'recharts';
import API_BASE from '../config';

function Analysis() {
  const [coin, setCoin] = useState('bitcoin');
  const [allCoins, setAllCoins] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/api/market-coins`)
      .then(res => setAllCoins(res.data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const fetchAnalysis = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API_BASE}/api/analysis/${coin}`);
        setAnalysis(res.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Analiz yüklenemedi');
        setAnalysis(null);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalysis();
  }, [coin]);

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' });
  };

  const formatPrice = (value) => {
    if (value === null || value === undefined) return '-';
    if (value >= 1000) return `$${(value/1000).toFixed(1)}K`;
    if (value >= 1) return `$${value.toFixed(2)}`;
    return `$${value.toFixed(6)}`;
  };

  // RSI rengi
  const getRsiColor = (rsi) => {
    if (rsi > 70) return 'text-red-400';
    if (rsi < 30) return 'text-green-400';
    return 'text-yellow-400';
  };

  // Trend rengi
  const getTrendColor = (trend) => {
    if (trend === 'bullish') return 'text-green-400';
    if (trend === 'bearish') return 'text-red-400';
    return 'text-gray-400';
  };

  // Trend ikonu
  const getTrendIcon = (trend) => {
    if (trend === 'bullish') return '📈';
    if (trend === 'bearish') return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10 text-white">
        <div className="text-center animate-pulse">Analiz yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <h1 className="text-3xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-yellow-400 to-orange-500">
        Teknik Analiz Dashboard
      </h1>

      {/* Coin Seçimi */}
      <div className="flex justify-center mb-8">
        <select
          value={coin}
          onChange={(e) => setCoin(e.target.value)}
          className="bg-slate-800 border border-yellow-500 text-white p-3 rounded-xl w-64"
        >
          {allCoins.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {error && (
        <div className="text-center text-red-400 mb-8">{error}</div>
      )}

      {analysis && (
        <>
          {/* Özet Kartlar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {/* Fiyat */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Güncel Fiyat</div>
              <div className="text-2xl font-bold text-white">
                {formatPrice(analysis.current_price)}
              </div>
            </div>

            {/* RSI */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">RSI (14)</div>
              <div className={`text-2xl font-bold ${getRsiColor(analysis.indicators?.rsi)}`}>
                {analysis.indicators?.rsi?.toFixed(1) || '-'}
              </div>
              <div className="text-xs text-slate-500">
                {analysis.indicators?.rsi_signal === 'overbought' && '⚠️ Aşırı Alım'}
                {analysis.indicators?.rsi_signal === 'oversold' && '✅ Aşırı Satım'}
                {analysis.indicators?.rsi_signal === 'neutral' && 'Nötr'}
              </div>
            </div>

            {/* Trend */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Trend</div>
              <div className={`text-2xl font-bold ${getTrendColor(analysis.trend?.direction)}`}>
                {getTrendIcon(analysis.trend?.direction)} {analysis.trend?.direction?.toUpperCase() || '-'}
              </div>
            </div>

            {/* Volatilite */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Volatilite (30g)</div>
              <div className="text-2xl font-bold text-purple-400">
                {analysis.risk_metrics?.volatility_30d?.toFixed(1) || '-'}%
              </div>
            </div>
          </div>

          {/* İkinci Satır Kartlar */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {/* MACD */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">MACD Trend</div>
              <div className={`text-xl font-bold ${analysis.indicators?.macd_trend === 'bullish' ? 'text-green-400' : 'text-red-400'}`}>
                {analysis.indicators?.macd_trend === 'bullish' ? '📈 Yükseliş' : '📉 Düşüş'}
              </div>
            </div>

            {/* Sharpe Ratio */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Sharpe Ratio</div>
              <div className={`text-2xl font-bold ${(analysis.risk_metrics?.sharpe_ratio || 0) > 1 ? 'text-green-400' : 'text-yellow-400'}`}>
                {analysis.risk_metrics?.sharpe_ratio?.toFixed(2) || '-'}
              </div>
            </div>

            {/* Max Drawdown */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Max Drawdown</div>
              <div className="text-2xl font-bold text-red-400">
                {analysis.risk_metrics?.max_drawdown?.toFixed(1) || '-'}%
              </div>
            </div>

            {/* Bollinger Position */}
            <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700">
              <div className="text-slate-400 text-sm">Bollinger Pozisyonu</div>
              <div className="text-lg font-bold text-blue-400">
                {analysis.indicators?.bb_position === 'above_upper' && '⬆️ Üst Bant Üstü'}
                {analysis.indicators?.bb_position === 'below_lower' && '⬇️ Alt Bant Altı'}
                {analysis.indicators?.bb_position === 'upper_half' && '↗️ Üst Yarı'}
                {analysis.indicators?.bb_position === 'lower_half' && '↘️ Alt Yarı'}
              </div>
            </div>
          </div>

          {/* Destek/Direnç Seviyeleri */}
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 mb-8">
            <h3 className="text-lg font-bold mb-3 text-slate-300">Destek & Direnç Seviyeleri</h3>
            <div className="grid grid-cols-5 gap-4 text-center">
              <div>
                <div className="text-xs text-slate-500">Direnç 1</div>
                <div className="text-red-400 font-mono">{formatPrice(analysis.levels?.r1)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Direnç</div>
                <div className="text-orange-400 font-mono">{formatPrice(analysis.levels?.resistance)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Pivot</div>
                <div className="text-yellow-400 font-mono">{formatPrice(analysis.levels?.pivot)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Destek</div>
                <div className="text-green-400 font-mono">{formatPrice(analysis.levels?.support)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Destek 1</div>
                <div className="text-emerald-400 font-mono">{formatPrice(analysis.levels?.s1)}</div>
              </div>
            </div>
          </div>

          {/* Fiyat + Bollinger Bands Grafiği */}
          {analysis.series && analysis.series.length > 0 && (
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
              <h3 className="text-lg font-bold mb-4 text-slate-300">Fiyat & Bollinger Bands</h3>
              <div className="h-[350px]">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={analysis.series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" tickFormatter={formatPrice} domain={['auto', 'auto']} />
                    <Tooltip 
                      labelFormatter={formatDate}
                      contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px'}}
                      formatter={(value, name) => [formatPrice(value), name]}
                    />
                    <Legend />
                    <Area type="monotone" dataKey="bb_upper" stroke="#6366f1" fill="#6366f130" name="BB Üst" />
                    <Area type="monotone" dataKey="bb_lower" stroke="#6366f1" fill="#6366f130" name="BB Alt" />
                    <Line type="monotone" dataKey="bb_middle" stroke="#6366f1" strokeDasharray="5 5" name="BB Orta" dot={false} />
                    <Line type="monotone" dataKey="price" stroke="#f59e0b" strokeWidth={2} name="Fiyat" dot={false} />
                    <Line type="monotone" dataKey="sma_7" stroke="#10b981" strokeWidth={1} name="SMA 7" dot={false} />
                    <Line type="monotone" dataKey="sma_30" stroke="#ef4444" strokeWidth={1} name="SMA 30" dot={false} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* RSI Grafiği */}
          {analysis.series && analysis.series.length > 0 && (
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
              <h3 className="text-lg font-bold mb-4 text-slate-300">RSI (Relative Strength Index)</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={analysis.series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" domain={[0, 100]} />
                    <Tooltip 
                      labelFormatter={formatDate}
                      contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px'}}
                    />
                    <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label={{ value: 'Aşırı Alım', fill: '#ef4444', fontSize: 12 }} />
                    <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Aşırı Satım', fill: '#10b981', fontSize: 12 }} />
                    <Line type="monotone" dataKey="rsi" stroke="#a855f7" strokeWidth={2} name="RSI" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* MACD Grafiği */}
          {analysis.series && analysis.series.length > 0 && (
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl">
              <h3 className="text-lg font-bold mb-4 text-slate-300">MACD</h3>
              <div className="h-[200px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={analysis.series}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip 
                      labelFormatter={formatDate}
                      contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px'}}
                    />
                    <Legend />
                    <ReferenceLine y={0} stroke="#475569" />
                    <Bar dataKey="macd_histogram" name="MACD Histogram" fill="#3b82f6" />
                    <Line type="monotone" dataKey="macd" stroke="#f59e0b" strokeWidth={2} name="MACD" dot={false} />
                    <Line type="monotone" dataKey="macd_signal" stroke="#ef4444" strokeWidth={2} name="Signal" dot={false} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Analysis;
