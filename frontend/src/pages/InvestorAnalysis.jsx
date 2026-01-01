import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE from '../config';

function InvestorAnalysis() {
  const [overview, setOverview] = useState(null);  
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 1. Sayfa yüklendiğinde kullanıcı listesini çek
  useEffect(() => {
  // Kullanıcı listesi (Zaten sende var)
  axios.get(`${API_BASE}/api/users`)
    .then(res => setUsers(res.data))
    .catch(err => console.error("Kullanıcı listesi alınamadı:", err));

  // Yeni: Borsa Genel Özeti
  axios.get(`${API_BASE}/api/exchange-overview`)
    .then(res => setOverview(res.data))
    .catch(err => console.error("Genel özet alınamadı:", err));
  }, []);
  
  // 2. Seçilen kullanıcı değiştiğinde performans analizini çek
  useEffect(() => {
    if (!selectedUser) return;

    const fetchUserPerformance = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API_BASE}/api/user-analysis/${selectedUser}`);
        setAnalysis(res.data);
      } catch (err) {
        setError('Yatırımcı verileri yüklenemedi.');
        setAnalysis(null);
      } finally {
        setLoading(false);
      }
    };
    fetchUserPerformance();
  }, [selectedUser]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <h1 className="text-3xl font-bold mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-500">
        Yatırımcı Performans Dashboard
      </h1>
      {/* 🏆 LIDERLIK PANELI (Borsa Genel Özeti) */}
{overview && (
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 bg-slate-900/40 p-6 rounded-3xl border border-blue-500/20 shadow-2xl backdrop-blur-sm">
    
    {/* 1. Borsanın Kralı */}
    <div className="text-center border-r border-slate-700/50 last:border-0">
      <div className="text-blue-400 text-xs font-bold uppercase tracking-widest mb-2 flex items-center justify-center gap-2">
        <span>🏆</span> Borsanın Kralı
      </div>
      <div className="text-2xl font-black text-white truncate px-2">
        {overview.king?.username || 'Hesaplanıyor...'}
      </div>
      <div className="text-emerald-400 text-sm font-mono font-bold mt-1">
        %{overview.king?.pnl_percent || 0} Başarı Oranı
      </div>
    </div>

    {/* 2. Toplam Hacim */}
    <div className="text-center border-r border-slate-700/50 last:border-0">
      <div className="text-orange-400 text-xs font-bold uppercase tracking-widest mb-2 flex items-center justify-center gap-2">
        <span>💰</span> Toplam Platform Hacmi
      </div>
      <div className="text-2xl font-black text-white">
        ${overview.total_liquidity?.toLocaleString()}
      </div>
      <div className="text-slate-500 text-[10px] mt-1 uppercase tracking-tighter">
        {overview.total_investors} Aktif Yatırımcı Mevcut
      </div>
    </div>

    {/* 3. En Popüler Coin */}
    <div className="text-center">
      <div className="text-purple-400 text-xs font-bold uppercase tracking-widest mb-2 flex items-center justify-center gap-2">
        <span>🔥</span> En Çok Tercih Edilen
      </div>
      <div className="text-2xl font-black text-white">
        {overview.most_popular_coin || '-'}
      </div>
      <div className="text-slate-500 text-[10px] mt-1 uppercase tracking-tighter">
        Portföylerin En Gözde Varlığı
      </div>
    </div>

  </div> )}
      
      {/* Yatırımcı Seçimi */}
      <div className="flex justify-center mb-8">
        <select
          value={selectedUser}
          onChange={(e) => setSelectedUser(e.target.value)}
          className="bg-slate-800 border border-emerald-500 text-white p-3 rounded-xl w-64 outline-none focus:ring-2 focus:ring-emerald-400"
        >
          <option value="">Bir Yatırımcı Seçin...</option>
          {users.map(u => <option key={u.username} value={u.username}>{u.username}</option>)}
        </select>
      </div>

      {loading && <div className="text-center animate-pulse text-emerald-400">Veriler işleniyor...</div>}
      {error && <div className="text-center text-red-400">{error}</div>}

      {analysis && !loading && (
        <>
          {/* Özet Kartlar */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl">
              <div className="text-slate-400 text-sm mb-1">Cüzdan Bakiyesi</div>
              <div className="text-3xl font-bold text-white">${analysis.wallet_balance?.toLocaleString()}</div>
            </div>

            <div className={`bg-slate-800/50 p-6 rounded-2xl border shadow-xl ${analysis.total_pnl >= 0 ? 'border-emerald-500/50' : 'border-red-500/50'}`}>
              <div className="text-slate-400 text-sm mb-1">Toplam Kâr/Zarar</div>
              <div className={`text-3xl font-bold ${analysis.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                ${analysis.total_pnl?.toLocaleString()}
              </div>
            </div>

            <div className="bg-slate-800/50 p-6 rounded-2xl border border-slate-700 shadow-xl">
              <div className="text-slate-400 text-sm mb-1">Hesap Durumu</div>
              <div className={`text-3xl font-bold ${analysis.overall_status === 'Profit' ? 'text-emerald-400' : 'text-red-400'}`}>
                {analysis.overall_status === 'Profit' ? '📈 KÂRDA' : '📉 ZARARDA'}
              </div>
            </div>
          </div>

          {/* Portföy Tablosu */}
          <div className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden shadow-2xl">
            <div className="p-6 border-b border-slate-700">
              <h3 className="text-xl font-bold text-slate-200">Portföy Detayları</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead className="bg-slate-900/50 text-slate-400 uppercase text-xs">
                  <tr>
                    <th className="p-4">Coin</th>
                    <th className="p-4">Miktar</th>
                    <th className="p-4">Alış Fiyatı</th>
                    <th className="p-4">Güncel Fiyat</th>
                    <th className="p-4">Kâr/Zarar ($)</th>
                    <th className="p-4">Değişim (%)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700 text-sm">
                  {analysis.portfolio_details.map((item, idx) => (
                    <tr key={idx} className="hover:bg-slate-700/30 transition-colors">
                      <td className="p-4 font-bold text-emerald-400">{item.coin.toUpperCase()}</td>
                      <td className="p-4 font-mono">{item.amount}</td>
                      <td className="p-4 text-slate-300">${item.buy_price.toLocaleString()}</td>
                      <td className="p-4 text-slate-300">${item.current_price.toLocaleString()}</td>
                      <td className={`p-4 font-bold ${item.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {item.pnl >= 0 ? '+' : ''}{item.pnl}
                      </td>
                      <td className={`p-4 font-bold ${item.pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                        {item.pnl_percent >= 0 ? '▲' : '▼'} %{Math.abs(item.pnl_percent)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default InvestorAnalysis;