import { useState, useEffect } from 'react';
import axios from 'axios';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area
} from 'recharts';

function App() {
  // Tüm coinler için state
  const [allCoins, setAllCoins] = useState([]);
  const [allCoinsLoading, setAllCoinsLoading] = useState(true);
  const [allCoinsError, setAllCoinsError] = useState(null);

  // Hangi coinin seçili olduğunu tutan state
  const [selectedCoin, setSelectedCoin] = useState('bitcoin');
  const [marketData, setMarketData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  // Popüler coinler için state
  const [popularCoins, setPopularCoins] = useState([]);
  const [popularLoading, setPopularLoading] = useState(true);
  const [popularError, setPopularError] = useState(null);

  // Tüm coinleri çek
  useEffect(() => {
    const fetchAllCoins = async () => {
      setAllCoinsLoading(true);
      setAllCoinsError(null);
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/all-coins');
        setAllCoins(response.data);
      } catch (err) {
        setAllCoinsError('Tüm coinler alınamadı. Backend çalışıyor mu?');
      } finally {
        setAllCoinsLoading(false);
      }
    };
    fetchAllCoins();
  }, []);

  // Takip ettiğimiz coinlerin listesi (Butonlar için)
  const coins = [
    { id: 'bitcoin', name: 'Bitcoin', color: '#f7931a' },
    { id: 'ethereum', name: 'Ethereum', color: '#627eea' },
    { id: 'solana', name: 'Solana', color: '#14f195' },
    { id: 'avalanche-2', name: 'Avalanche', color: '#e84142' },
  ];
  // Popüler coinleri çek
  useEffect(() => {
    const fetchPopular = async () => {
      setPopularLoading(true);
      setPopularError(null);
      try {
        const response = await axios.get('http://127.0.0.1:5000/api/popular-coins');
        setPopularCoins(response.data);
      } catch (err) {
        setPopularError('Popüler coinler alınamadı. Backend çalışıyor mu?');
      } finally {
        setPopularLoading(false);
      }
    };
    fetchPopular();
  }, []);

  useEffect(() => {
    // Seçili coin değiştiğinde veriyi tekrar çek
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Backend'e seçili coini soruyoruz
        const response = await axios.get(`http://127.0.0.1:5000/api/market/${selectedCoin}`);
        setMarketData(response.data);
      } catch (err) {
        console.error("Error:", err);
        setError("Veriye ulaşılamadı. Backend çalışıyor mu?");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [selectedCoin]); // [selectedCoin] demek: "Bu değişken değişince kodu tekrar çalıştır"

  const formatDate = (dateString) => {
    const options = { month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('en-US', options);
  };

  // Seçili coinin rengini bulalım
  const currentColor = coins.find(c => c.id === selectedCoin)?.color || '#8b5cf6';

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8 font-sans selection:bg-blue-500 selection:text-white">
      {/* BAŞLIK ALANI */}
      <header className="mb-12 text-center">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 drop-shadow-lg">
          Kripto Analiz Paneli
        </h1>
        <p className="text-slate-400 mt-3 text-lg">Gerçek Zamanlı Piyasa Verileri</p>
      </header>

      {/* TÜM COINLER TABLOSU */}
      <div className="max-w-6xl mx-auto mb-12">
        <div className="bg-slate-800/70 rounded-2xl shadow-xl p-6 border border-slate-700/40">
          <h2 className="text-2xl font-bold mb-4 text-center">Tüm Coinler</h2>
          {allCoinsLoading ? (
            <div className="flex justify-center items-center py-8">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="ml-4 text-slate-400">Yükleniyor...</span>
            </div>
          ) : allCoinsError ? (
            <div className="text-red-400 text-center py-4">{allCoinsError}</div>
          ) : (
            <div className="overflow-x-auto max-h-[400px]">
              <table className="min-w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-400">
                    <th className="py-2 px-3">Coin</th>
                    <th className="py-2 px-3">Fiyat (USD)</th>
                    <th className="py-2 px-3">Market Cap</th>
                    <th className="py-2 px-3">24s Değişim</th>
                  </tr>
                </thead>
                <tbody>
                  {allCoins.map((coin) => (
                    <tr key={coin.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition">
                      <td className="py-2 px-3 flex items-center gap-2">
                        {coin.image && <img src={coin.image} alt={coin.name} className="w-5 h-5 rounded-full" />}
                        <span className="font-semibold">{coin.name}</span>
                        <span className="text-slate-400 text-xs uppercase">{coin.symbol}</span>
                      </td>
                      <td className="py-2 px-3 font-mono">{coin.current_price !== undefined ? `$${coin.current_price?.toLocaleString()}` : '-'}</td>
                      <td className="py-2 px-3 font-mono">{coin.market_cap !== undefined ? `$${coin.market_cap?.toLocaleString()}` : '-'}</td>
                      <td className={`py-2 px-3 font-mono ${coin.price_change_percentage_24h > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {coin.price_change_percentage_24h !== undefined && coin.price_change_percentage_24h !== null ? `${coin.price_change_percentage_24h.toFixed(2)}%` : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
      <div className="max-w-4xl mx-auto mb-12">
        <div className="bg-slate-800/70 rounded-2xl shadow-xl p-6 border border-slate-700/40">
          <h2 className="text-2xl font-bold mb-4 text-center">Popüler Coinler</h2>
          {popularLoading ? (
            <div className="flex justify-center items-center py-8">
              <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="ml-4 text-slate-400">Yükleniyor...</span>
            </div>
          ) : popularError ? (
            <div className="text-red-400 text-center py-4">{popularError}</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="text-slate-400 text-sm">
                    <th className="py-2 px-3">Coin</th>
                    <th className="py-2 px-3">Fiyat (USD)</th>
                    <th className="py-2 px-3">Market Cap</th>
                    <th className="py-2 px-3">24s Değişim</th>
                  </tr>
                </thead>
                <tbody>
                  {popularCoins.map((coin) => (
                    <tr key={coin.id} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition">
                      <td className="py-2 px-3 flex items-center gap-2">
                        {coin.image && <img src={coin.image} alt={coin.name} className="w-6 h-6 rounded-full" />}
                        <span className="font-semibold">{coin.name}</span>
                        <span className="text-slate-400 text-xs uppercase">{coin.symbol}</span>
                      </td>
                      <td className="py-2 px-3 font-mono">${coin.current_price?.toLocaleString() ?? '-'}</td>
                      <td className="py-2 px-3 font-mono">${coin.market_cap?.toLocaleString() ?? '-'}</td>
                      <td className={`py-2 px-3 font-mono ${coin.price_change_percentage_24h > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {coin.price_change_percentage_24h?.toFixed(2) ?? '-'}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-7xl mx-auto">
        
        {/* BUTONLAR (COIN SEÇİMİ) */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          {coins.map((coin) => (
            <button
              key={coin.id}
              onClick={() => setSelectedCoin(coin.id)}
              className={`px-6 py-3 rounded-xl font-bold transition-all duration-300 transform hover:scale-105 shadow-lg
                ${selectedCoin === coin.id 
                  ? 'bg-slate-700 text-white ring-2 ring-offset-2 ring-offset-[#0f172a]' 
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                }`}
              style={{
                borderColor: selectedCoin === coin.id ? coin.color : 'transparent',
                borderWidth: selectedCoin === coin.id ? '2px' : '0px',
                boxShadow: selectedCoin === coin.id ? `0 0 20px ${coin.color}40` : 'none'
              }}
            >
              {coin.name}
            </button>
          ))}
        </div>

        {/* GRAFİK KARTI */}
        <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700/50">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold capitalize flex items-center gap-3">
                <span className="w-4 h-4 rounded-full shadow-[0_0_10px]" style={{backgroundColor: currentColor}}></span>
                {selectedCoin} <span className="text-slate-500 text-lg font-normal">Fiyat Geçmişi</span>
              </h2>
            </div>
            <div className="px-4 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
              <span className="text-green-400 text-sm font-semibold animate-pulse">● Canlı Veri</span>
            </div>
          </div>

          <div className="h-[500px] w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/30">
            {loading ? (
              <div className="h-full flex flex-col items-center justify-center space-y-4">
                <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-slate-400 animate-pulse">Veriler Yükleniyor...</p>
              </div>
            ) : error ? (
              <div className="h-full flex items-center justify-center text-red-400">
                <p>{error}</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={marketData}>
                  <defs>
                    <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor={currentColor} stopOpacity={0.3}/>
                      <stop offset="95%" stopColor={currentColor} stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                  <XAxis 
                    dataKey="timestamp" 
                    tickFormatter={formatDate}
                    stroke="#94a3b8"
                    tick={{fontSize: 12}}
                    tickMargin={10}
                    axisLine={false}
                  />
                  <YAxis 
                    domain={['auto', 'auto']}
                    stroke="#94a3b8"
                    tick={{fontSize: 12}}
                    axisLine={false}
                    tickFormatter={(value) => `$${value.toLocaleString()}`}
                  />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#1e293b', 
                      borderColor: '#334155', 
                      borderRadius: '12px',
                      boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.5)'
                    }}
                    itemStyle={{ color: '#fff' }}
                    labelFormatter={formatDate}
                    formatter={(value) => [`$${value.toLocaleString()}`, 'Fiyat']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="price" 
                    stroke={currentColor} 
                    strokeWidth={3}
                    fillOpacity={1} 
                    fill="url(#colorPrice)" 
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;