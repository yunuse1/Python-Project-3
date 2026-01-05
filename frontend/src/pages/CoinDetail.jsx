import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import API_BASE from '../config';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer, LineChart, Line 
} from 'recharts';

function CoinDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [chartData, setChartData] = useState([]);
  const [indexedSummary, setIndexedSummary] = useState(null);
  const [forecastData, setForecastData] = useState([]); 
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API_BASE}/api/market/${id}`);
        const normalize = (r) => {
          if (Array.isArray(r)) return r;
          if (r && Array.isArray(r.data)) return r.data;
          if (r && Array.isArray(r?.data?.data)) return r.data.data;
          return [];
        };
        setChartData(normalize(res.data));

        const rIdx = await axios.get(`${API_BASE}/api/market/indexed?coins=${id}`);
        if (rIdx.data?.coins && rIdx.data.coins[id]) {
          setIndexedSummary(rIdx.data.coins[id].summary || null);
        }

        const rForecast = await axios.get(`${API_BASE}/api/forecast/${id}`);
        setForecastData(rForecast.data.forecast || []);

      } catch (err) {
        console.error("Data fetch error:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const formatDate = (dateString) => new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center">
        <div className="animate-spin inline-block w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full mb-4"></div>
        <p className="text-slate-400 font-bold animate-pulse uppercase tracking-widest">Loading...</p>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white font-sans">
      <button 
        onClick={() => navigate(-1)} 
        className="text-slate-400 hover:text-white mb-8 inline-flex items-center gap-2 transition-colors font-bold uppercase text-xs tracking-widest cursor-pointer bg-transparent border-none"
      >
        <span>←</span> Back to Market List
      </button>
      
      <div className="bg-slate-800/40 backdrop-blur-xl p-10 rounded-[3rem] shadow-2xl border border-slate-700/50 mb-10">
        <div className="flex items-center justify-between mb-10">
            <div className="flex items-center gap-4">
                <h1 className="text-5xl font-black capitalize tracking-tighter italic">{id}</h1>
                <span className="bg-emerald-500/20 text-emerald-400 px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest animate-pulse border border-emerald-500/30">
                  Live Data
                </span>
            </div>
            {indexedSummary && (
                <div className="text-right">
                    <p className="text-slate-400 text-[10px] font-bold uppercase tracking-widest mb-1 font-mono">30D Change</p>
                    <p className={`text-2xl font-black ${indexedSummary.percent_change >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {indexedSummary.percent_change >= 0 ? '▲' : '▼'} %{Math.abs(indexedSummary.percent_change).toFixed(2)}
                    </p>
                </div>
            )}
        </div>

        <div className="h-[450px] w-full bg-slate-950/40 rounded-[2rem] p-6 border border-white/5 shadow-inner">
            <ResponsiveContainer width="100%" height="100%">
                {(!chartData || chartData.length === 0) ? (
                  <div className="h-full flex items-center justify-center text-slate-500 font-bold uppercase tracking-widest font-mono">No Data</div>
                ) : (
                  <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.5} />
                        <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#64748b" tick={{fontSize: 12}} />
                        <YAxis domain={['auto', 'auto']} stroke="#64748b" tickFormatter={(v) => `$${v}`} tick={{fontSize: 12}} />
                        <Tooltip 
                            contentStyle={{backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '15px'}} 
                            itemStyle={{color: '#3b82f6', fontWeight: 'bold'}}
                        />
                        <Area type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={4} fillOpacity={1} fill="url(#colorPrice)" />
                  </AreaChart>
                )}
            </ResponsiveContainer>
        </div>

        {indexedSummary && (
          <div className="mt-6 p-6 bg-slate-900/40 rounded-3xl border border-slate-700/50 flex flex-col md:flex-row justify-between items-center gap-4 animate-in fade-in duration-500">
            <div className="flex items-center gap-3">
                <span className="p-2 bg-slate-700 text-slate-200 rounded-lg text-[10px] font-black uppercase tracking-tighter">Index</span>
                <p className="text-sm text-slate-400 font-medium font-mono">Analysis Start: <b className="text-white">{new Date(indexedSummary.base_date).toLocaleDateString('en-US')}</b></p>
            </div>
            <p className="text-sm font-black uppercase tracking-widest text-slate-500 font-mono">Benchmark Base Value: <b className="text-emerald-400 ml-2">100.00</b></p>
          </div>
        )}

        {forecastData && forecastData.length > 0 && (
          <div className="mt-10 bg-indigo-500/5 p-8 rounded-[2.5rem] border border-indigo-500/20 shadow-[0_0_50px_rgba(99,102,241,0.05)]">
            <div className="flex items-center gap-4 mb-8">
              <div className="p-3 bg-indigo-500/20 rounded-2xl text-2xl shadow-lg border border-indigo-500/30">🤖</div>
              <div>
                <h3 className="text-2xl font-black text-white uppercase tracking-tighter">7-Day Price Projection</h3>
                <p className="text-indigo-400/60 text-xs font-bold uppercase tracking-widest font-mono">Machine Learning Model</p>
              </div>
            </div>

            <div className="h-[300px] w-full bg-slate-950/20 rounded-3xl p-6 border border-white/5">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.3} />
                  <XAxis dataKey="day" stroke="#94a3b8" tick={{fontSize: 12, fontWeight: 'bold'}} />
                  <YAxis domain={['auto', 'auto']} stroke="#94a3b8" tick={{fontSize: 10}} tickFormatter={(v) => `$${v.toLocaleString()}`} />
                  <Tooltip 
                    contentStyle={{backgroundColor: '#1e1b4b', borderColor: '#4338ca', borderRadius: '16px'}}
                    itemStyle={{color: '#818cf8', fontWeight: '900'}}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted_price" 
                    stroke="#6366f1" 
                    strokeWidth={5} 
                    dot={{ r: 7, fill: '#818cf8', strokeWidth: 3, stroke: '#fff' }}
                    activeDot={{ r: 10, fill: '#fff' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            
            <div className="mt-6 flex items-center gap-3 text-slate-500 italic text-[11px] bg-slate-900/40 p-4 rounded-2xl">
              <span className="text-lg">⚠️</span>
              <p className="font-mono uppercase tracking-tighter leading-tight opacity-70">This prediction model is based on historical data. Not financial advice!</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CoinDetail;