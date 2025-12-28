import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
// Standart ve temiz import
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function CoinDetail() {
  const { id } = useParams();
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`http://127.0.0.1:5000/api/market/${id}`);
        setChartData(res.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const formatDate = (dateString) => new Date(dateString).toLocaleDateString('tr-TR', {month:'short', day:'numeric'});

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <Link to="/" className="text-slate-400 hover:text-white mb-6 inline-block">← Listeye Dön</Link>
      
      <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700">
        <div className="flex items-center gap-4 mb-8">
            <h1 className="text-4xl font-bold capitalize">{id}</h1>
            <span className="bg-green-500/20 text-green-400 px-3 py-1 rounded-full text-sm font-semibold animate-pulse">Canlı Piyasa</span>
        </div>

        <div className="h-[500px] w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/30">
            {loading ? (
                <div className="h-full flex items-center justify-center">Yükleniyor...</div>
            ) : (
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                            </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                        <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                        <YAxis domain={['auto', 'auto']} stroke="#94a3b8" tickFormatter={(v) => `$${v}`} />
                        <Tooltip contentStyle={{backgroundColor: '#1e293b', borderColor: '#334155'}} />
                        <Area type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
                    </AreaChart>
                </ResponsiveContainer>
            )}
        </div>
      </div>
    </div>
  );
}

export default CoinDetail;