import React, { useState, useEffect } from 'react';
import axios from 'axios';
// Standart ve temiz import
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function Compare() {
  const [coin1, setCoin1] = useState('bitcoin');
  const [coin2, setCoin2] = useState('ethereum');
  // Prevent same coin selection
  // Sadece iki farklı coin seçiliyse fetch et
  useEffect(() => {
    if (coin1 === coin2) return;
    // ...fetch işlemleri useEffect içinde zaten var...
  }, [coin1, coin2]);
  const [data1, setData1] = useState([]);
  const [data2, setData2] = useState([]);
  const [allCoins, setAllCoins] = useState([]); 
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    // Use market-only coins so compare select lists only coins with market data
    axios.get('http://127.0.0.1:5000/api/market-coins').then(res => setAllCoins(res.data));
  }, []);

  useEffect(() => {
    const fetchCompareData = async () => {
        try {
            console.debug('compare: selected coins', coin1, coin2);
            const res1 = await axios.get(`http://127.0.0.1:5000/api/market/${coin1}`);
            const res2 = await axios.get(`http://127.0.0.1:5000/api/market/${coin2}`);
        // Normalize API responses into sorted arrays of { timestamp: ISO, price: number|null }
        const normalize = (r) => {
          const raw = Array.isArray(r) ? r : (r && Array.isArray(r.data) ? r.data : []);
          const out = raw.map(item => {
            const ts = item && item.timestamp ? new Date(item.timestamp) : null;
            return {
              timestamp: ts ? ts.toISOString() : null,
              price: (item && item.price !== undefined && item.price !== null) ? Number(item.price) : null
            };
          }).filter(x => x.timestamp !== null);
          return out.sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp));
        };

        const nd1 = normalize(res1.data);
        const nd2 = normalize(res2.data);
        console.debug('compare: data lengths', nd1.length, nd2.length);
        console.debug('compare sample1', nd1.slice(0,6));
        console.debug('compare sample2', nd2.slice(0,6));
        setData1(nd1);
        setData2(nd2);
        } catch (e) {
            console.error(e);
        setData1([]);
        setData2([]);
        }
    };
    fetchCompareData();

    // fetch indexed analysis for both coins
    const fetchAnalysis = async () => {
      try {
        const r = await axios.get(`http://127.0.0.1:5000/api/market/indexed?coins=${coin1},${coin2}`);
        console.debug('compare: analysis keys', Object.keys(r.data.coins || {}));
        setAnalysis(r.data || null);
      } catch (e) {
        console.error('analysis fetch error', e);
        setAnalysis(null);
      }
    };
    fetchAnalysis();
  }, [coin1, coin2]);

    // Merge two timeseries by timestamp union so points align correctly
    const map = new Map();
    data1.forEach(d => {
      if (!d || !d.timestamp) return;
      map.set(d.timestamp, { timestamp: d.timestamp, price1: d.price ?? null, price2: null });
    });
    data2.forEach(d => {
      if (!d || !d.timestamp) return;
      const entry = map.get(d.timestamp);
      if (entry) entry.price2 = d.price ?? null;
      else map.set(d.timestamp, { timestamp: d.timestamp, price1: null, price2: d.price ?? null });
    });

    const mergedData = Array.from(map.values())
      .sort((a,b) => new Date(a.timestamp) - new Date(b.timestamp))
      .filter(d => (d.price1 !== null) || (d.price2 !== null));

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
                value={coin1} 
                onChange={(e) => setCoin1(e.target.value)}
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
                value={coin2} 
                onChange={(e) => setCoin2(e.target.value)}
                className="bg-slate-800 border border-purple-500 text-white p-3 rounded-xl w-48"
              >
                  {allCoins.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
          </div>
      </div>

      {/* Debug: seçili coinler ve analysis objesi */}
      <div className="text-xs text-slate-400 mb-2 text-center">Seçili: {coin1} vs {coin2}</div>
      {analysis && analysis.ranking && coin1 !== coin2 && (
        <div className="max-w-3xl mx-auto mb-6 text-center text-slate-300">
          <strong>{analysis.ranking[0].coin.toUpperCase()}</strong> bu periyot içinde en iyi performansı gösteriyor ({analysis.ranking[0].percent_change.toFixed(2)}%).{' '}
          <span className="text-slate-500">{analysis.ranking.length > 1 ? `${analysis.ranking[1].coin.toUpperCase()} ise ${analysis.ranking[1].percent_change.toFixed(2)}%` : ''}</span>
        </div>
      )}

      <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl h-[500px]">
        <ResponsiveContainer width="100%" height="100%">
          {analysis && analysis.coins && analysis.coins[coin1] && analysis.coins[coin2] && coin1 !== coin2 ? (
            (() => {
              // Merge indexed series by timestamp union
              const s1 = (analysis.coins[coin1].series || []).map(x => ({ timestamp: x.timestamp, indexed1: x.indexed }));
              const s2 = (analysis.coins[coin2].series || []).map(x => ({ timestamp: x.timestamp, indexed2: x.indexed }));
              const allTimestamps = Array.from(new Set([...s1.map(x=>x.timestamp), ...s2.map(x=>x.timestamp)]));
              const merged = allTimestamps.map(ts => {
                const d1 = s1.find(x => x.timestamp === ts);
                const d2 = s2.find(x => x.timestamp === ts);
                return {
                  timestamp: ts,
                  indexed1: d1 ? d1.indexed1 : null,
                  indexed2: d2 ? d2.indexed2 : null
                };
              }).filter(d => (d.indexed1 !== null && d.indexed1 !== 0) || (d.indexed2 !== null && d.indexed2 !== 0));
              if (merged.length === 0) {
                return <div className="text-center text-red-400 pt-20">Karşılaştırma için yeterli veri yok.</div>;
              }
              return (
                <LineChart data={merged}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="timestamp" tickFormatter={formatDate} stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip labelFormatter={formatDate} contentStyle={{backgroundColor: '#0f172a'}} formatter={(v,name)=>[v, name.includes('1')?coin1.toUpperCase():coin2.toUpperCase()]} />
                  <Legend />
                  <Line type="monotone" dataKey="indexed1" name={`${coin1.toUpperCase()} (indexed)`} stroke="#3b82f6" strokeWidth={3} dot={false} />
                  <Line type="monotone" dataKey="indexed2" name={`${coin2.toUpperCase()} (indexed)`} stroke="#a855f7" strokeWidth={3} dot={false} />
                </LineChart>
              );
            })()
          ) : (
            <div className="text-center text-red-400 pt-20">Karşılaştırma için yeterli veri yok.</div>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Compare;