import React, { useState, useEffect } from 'react';
import axios from 'axios';
// Standart ve temiz import
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Compare() {
  const [coin1, setCoin1] = useState('bitcoin');
  const [coin2, setCoin2] = useState('ethereum');
  const [data1, setData1] = useState([]);
  const [data2, setData2] = useState([]);
  const [allCoins, setAllCoins] = useState([]); 

  useEffect(() => {
    // Use market-only coins so compare select lists only coins with market data
    axios.get('http://127.0.0.1:5000/api/market-coins').then(res => setAllCoins(res.data));
  }, []);

  useEffect(() => {
    const fetchCompareData = async () => {
        try {
            const res1 = await axios.get(`http://127.0.0.1:5000/api/market/${coin1}`);
            const res2 = await axios.get(`http://127.0.0.1:5000/api/market/${coin2}`);
        // API may return an object with { error, data: [] } or a raw array.
        const normalize = (r) => {
          if (Array.isArray(r)) return r;
          if (r && Array.isArray(r.data)) return r.data;
          return [];
        };

        setData1(normalize(res1.data));
        setData2(normalize(res2.data));
        } catch (e) {
            console.error(e);
        setData1([]);
        setData2([]);
        }
    };
    fetchCompareData();
  }, [coin1, coin2]);

    // Merge two timeseries by index — handle differing lengths safely
    const maxLen = Math.max(data1.length, data2.length);
    const mergedData = Array.from({ length: maxLen }).map((_, index) => {
      const a = data1[index] || {};
      const b = data2[index] || {};
      return {
        timestamp: a.timestamp || b.timestamp || null,
        price1: a.price || 0,
        price2: b.price || 0
      };
    }).filter(d => d.timestamp !== null);

  const formatDate = (dateString) => new Date(dateString).toLocaleDateString('tr-TR', {month:'short', day:'numeric'});

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <h1 className="text-3xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-blue-500">
          Kripto Karşılaştırma Analizi
      </h1>

      <div className="flex justify-center gap-8 mb-10">
          <div className="flex flex-col">
              <label className="mb-2 text-blue-400 font-bold">1. Coin</label>
              <select 
                value={coin1} onChange={(e) => setCoin1(e.target.value)}
                className="bg-slate-800 border border-blue-500 text-white p-3 rounded-xl w-48"
              >
                  {allCoins.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
          </div>

          <div className="flex items-center pt-6">
            <span className="text-2xl text-slate-500 font-bold">VS</span>
          </div>

          <div className="flex flex-col">
              <label className="mb-2 text-purple-400 font-bold">2. Coin</label>
              <select 
                value={coin2} onChange={(e) => setCoin2(e.target.value)}
                className="bg-slate-800 border border-purple-500 text-white p-3 rounded-xl w-48"
              >
                  {allCoins.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
          </div>
      </div>

      <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl h-[500px]">
          <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mergedData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8"/>
                  <YAxis stroke="#94a3b8" />
                  <Tooltip labelFormatter={formatDate} contentStyle={{backgroundColor: '#0f172a'}}/>
                  <Legend />
                  <Line type="monotone" dataKey="price1" name={coin1.toUpperCase()} stroke="#3b82f6" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="price2" name={coin2.toUpperCase()} stroke="#a855f7" strokeWidth={3} dot={false} />
              </LineChart>
          </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Compare;