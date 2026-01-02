import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, ScatterChart, Scatter, ReferenceLine, Cell } from 'recharts';
import API_BASE from '../config';

function Report() {
  const [coin, setCoin] = useState('bitcoin');
  const [allCoins, setAllCoins] = useState([]);
  const [report, setReport] = useState(null);
  const [anomalies, setAnomalies] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE}/api/market-coins`)
      .then(res => setAllCoins(res.data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const [reportRes, anomalyRes] = await Promise.all([
          axios.get(`${API_BASE}/api/report/${coin}`),
          axios.get(`${API_BASE}/api/anomalies/${coin}`)
        ]);
        setReport(reportRes.data);
        setAnomalies(anomalyRes.data);
      } catch (err) {
        setError(err.response?.data?.error || 'Report could not be loaded');
        setReport(null);
        setAnomalies(null);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [coin]);

  const formatNumber = (value, decimals = 2) => {
    if (value === null || value === undefined) return '-';
    if (Math.abs(value) >= 1000000) return `${(value/1000000).toFixed(decimals)}M`;
    if (Math.abs(value) >= 1000) return `${(value/1000).toFixed(decimals)}K`;
    return value.toFixed(decimals);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined) return '-';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const getColorByValue = (value, threshold = 0) => {
    if (value > threshold) return 'text-green-400';
    if (value < threshold) return 'text-red-400';
    return 'text-gray-400';
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-10 text-white">
        <div className="text-center animate-pulse">Preparing scientific report...</div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <h1 className="text-3xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-purple-400 to-pink-500">
        📊 Scientific Analysis Report
      </h1>

      {/* Coin Selection */}
      <div className="flex justify-center mb-8">
        <select
          value={coin}
          onChange={(e) => setCoin(e.target.value)}
          className="bg-slate-800 border border-purple-500 text-white p-3 rounded-xl w-64"
        >
          {allCoins.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
      </div>

      {error && (
        <div className="text-center text-red-400 mb-8">{error}</div>
      )}

      {report && (
        <>
          {/* Analysis Period */}
          <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 mb-8 text-center">
            <span className="text-slate-400">Analysis Period: </span>
            <span className="text-white font-mono">
              {report.analysis_period?.start?.split('T')[0]} → {report.analysis_period?.end?.split('T')[0]}
            </span>
            <span className="text-slate-400 ml-4">({report.analysis_period?.total_days} days)</span>
          </div>

          {/* Descriptive Statistics */}
          <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-300">📈 Descriptive Statistics</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              <StatCard label="Mean" value={`$${formatNumber(report.descriptive_statistics?.mean)}`} />
              <StatCard label="Std Dev" value={`$${formatNumber(report.descriptive_statistics?.std)}`} />
              <StatCard label="Min" value={`$${formatNumber(report.descriptive_statistics?.min)}`} color="text-red-400" />
              <StatCard label="Max" value={`$${formatNumber(report.descriptive_statistics?.max)}`} color="text-green-400" />
              <StatCard label="Median" value={`$${formatNumber(report.descriptive_statistics?.median)}`} />
              <StatCard label="IQR" value={`$${formatNumber(report.descriptive_statistics?.iqr)}`} />
              <StatCard label="Q1 (25%)" value={`$${formatNumber(report.descriptive_statistics?.q1)}`} />
              <StatCard label="Q3 (75%)" value={`$${formatNumber(report.descriptive_statistics?.q3)}`} />
              <StatCard label="Skewness" value={formatNumber(report.descriptive_statistics?.skewness, 3)} color={getColorByValue(report.descriptive_statistics?.skewness)} />
              <StatCard label="Kurtosis" value={formatNumber(report.descriptive_statistics?.kurtosis, 3)} />
              <StatCard label="CV (%)" value={formatNumber(report.descriptive_statistics?.coefficient_of_variation)} />
              <StatCard label="Range" value={`$${formatNumber(report.descriptive_statistics?.range)}`} />
            </div>
          </div>

          {/* Returns Analysis */}
          <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-300">💰 Returns Analysis</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard 
                label="Cumulative Return" 
                value={formatPercent(report.returns_analysis?.cumulative_return)} 
                color={getColorByValue(report.returns_analysis?.cumulative_return)}
              />
              <StatCard 
                label="Annualized Return" 
                value={formatPercent(report.returns_analysis?.annualized_return)} 
                color={getColorByValue(report.returns_analysis?.annualized_return)}
              />
              <StatCard 
                label="Annualized Volatility" 
                value={formatPercent(report.returns_analysis?.annualized_volatility)} 
                color="text-purple-400"
              />
              <StatCard 
                label="Win Rate" 
                value={`${report.returns_analysis?.daily_returns?.win_rate?.toFixed(1)}%`} 
                color={getColorByValue(report.returns_analysis?.daily_returns?.win_rate, 50)}
              />
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
              <StatCard label="Daily Avg Return" value={formatPercent(report.returns_analysis?.daily_returns?.mean)} />
              <StatCard label="Daily Volatility" value={formatPercent(report.returns_analysis?.daily_returns?.std)} />
              <StatCard label="Positive Days" value={report.returns_analysis?.daily_returns?.positive_days} color="text-green-400" />
              <StatCard label="Negative Days" value={report.returns_analysis?.daily_returns?.negative_days} color="text-red-400" />
            </div>
          </div>

          {/* Risk Analysis */}
          <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-300">⚠️ Risk Analysis</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatCard 
                label="VaR (95%)" 
                value={formatPercent(report.risk_analysis?.var_historic_95)} 
                color="text-red-400"
                subtitle="1-day loss risk"
              />
              <StatCard 
                label="CVaR / ES" 
                value={formatPercent(report.risk_analysis?.cvar_95)} 
                color="text-red-400"
                subtitle="Expected shortfall"
              />
              <StatCard 
                label="Max Drawdown" 
                value={formatPercent(report.risk_analysis?.max_drawdown)} 
                color="text-red-400"
                subtitle="Largest decline"
              />
              <StatCard 
                label="VaR Parametric" 
                value={formatPercent(report.risk_analysis?.var_parametric_95)} 
                color="text-orange-400"
              />
            </div>
            {report.risk_analysis?.interpretation && (
              <div className="mt-4 p-4 bg-slate-900/50 rounded-xl text-sm">
                <p className="text-slate-400">📌 {report.risk_analysis.interpretation.var_meaning}</p>
                <p className="text-slate-400 mt-1">📌 {report.risk_analysis.interpretation.max_drawdown_meaning}</p>
              </div>
            )}
          </div>

          {/* Anomaly Detection */}
          {anomalies && (
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
              <h2 className="text-xl font-bold mb-4 text-slate-300">🔍 Anomaly Detection</h2>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <StatCard 
                  label="Total Anomalies" 
                  value={anomalies.anomaly_counts?.any_method} 
                  color="text-yellow-400"
                />
                <StatCard 
                  label="Anomaly Rate" 
                  value={`${anomalies.anomaly_percentage}%`} 
                  color="text-yellow-400"
                />
                <StatCard 
                  label="Z-Score" 
                  value={anomalies.anomaly_counts?.zscore} 
                  subtitle="method"
                />
                <StatCard 
                  label="IQR" 
                  value={anomalies.anomaly_counts?.iqr} 
                  subtitle="method"
                />
                <StatCard 
                  label="Price Spike" 
                  value={anomalies.anomaly_counts?.price_spike} 
                  subtitle="method"
                />
              </div>

              {/* Anomaly Chart */}
              {anomalies.series && anomalies.series.length > 0 && (
                <div className="h-[250px]">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={anomalies.series}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                      <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                      <YAxis yAxisId="left" stroke="#94a3b8" />
                      <YAxis yAxisId="right" orientation="right" stroke="#a855f7" />
                      <Tooltip 
                        labelFormatter={formatDate}
                        contentStyle={{backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px'}}
                      />
                      <Legend />
                      <Line yAxisId="left" type="monotone" dataKey="price" stroke="#f59e0b" strokeWidth={2} name="Price" dot={false} />
                      <Line yAxisId="right" type="monotone" dataKey="zscore" stroke="#a855f7" strokeWidth={1} name="Z-Score" dot={false} />
                      <ReferenceLine yAxisId="right" y={3} stroke="#ef4444" strokeDasharray="3 3" />
                      <ReferenceLine yAxisId="right" y={-3} stroke="#ef4444" strokeDasharray="3 3" />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
          )}

          {/* Trend Distribution */}
          <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl mb-8">
            <h2 className="text-xl font-bold mb-4 text-slate-300">📊 Trend Distribution</h2>
            <div className="grid grid-cols-3 gap-4">
              <StatCard 
                label="Bullish" 
                value={report.trend_analysis?.trend_distribution?.bullish || 0} 
                color="text-green-400"
                subtitle="days"
              />
              <StatCard 
                label="Bearish" 
                value={report.trend_analysis?.trend_distribution?.bearish || 0} 
                color="text-red-400"
                subtitle="days"
              />
              <StatCard 
                label="Neutral" 
                value={report.trend_analysis?.trend_distribution?.neutral || 0} 
                color="text-gray-400"
                subtitle="days"
              />
            </div>
            <div className="mt-4 text-center">
              <span className="text-slate-400">Current Trend: </span>
              <span className={`font-bold ${
                report.trend_analysis?.current_trend === 'bullish' ? 'text-green-400' :
                report.trend_analysis?.current_trend === 'bearish' ? 'text-red-400' : 'text-gray-400'
              }`}>
                {report.trend_analysis?.current_trend === 'bullish' ? '📈 BULLISH' :
                 report.trend_analysis?.current_trend === 'bearish' ? '📉 BEARISH' : '➡️ NEUTRAL'}
              </span>
            </div>
          </div>

          {/* Data Quality */}
          <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-slate-300">✅ Data Quality</h2>
            <div className="grid grid-cols-2 gap-4">
              <StatCard 
                label="Missing Data" 
                value={report.data_quality?.missing_values || 0} 
                color={report.data_quality?.missing_values > 0 ? 'text-red-400' : 'text-green-400'}
              />
              <StatCard 
                label="Data Completeness" 
                value={`${report.data_quality?.data_completeness?.toFixed(1)}%`} 
                color="text-green-400"
              />
            </div>
          </div>
        </>
      )}
    </div>
  );
}

// Stat Card Component
function StatCard({ label, value, color = 'text-white', subtitle = null }) {
  return (
    <div className="bg-slate-900/50 p-3 rounded-lg text-center">
      <div className="text-slate-500 text-xs mb-1">{label}</div>
      <div className={`text-lg font-bold ${color}`}>{value}</div>
      {subtitle && <div className="text-slate-600 text-xs">{subtitle}</div>}
    </div>
  );
}

export default Report;
