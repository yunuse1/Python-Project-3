import React, { useState, useEffect } from 'react';
import axios from 'axios';
import API_BASE from '../config';

function InvestorAnalysis() {
  // --- TAB AND GENERAL STATE MANAGEMENT ---
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'compare'
  const [overview, setOverview] = useState(null);
  const [users, setUsers] = useState([]);
  
  // --- TAB 1 (SINGLE SUMMARY) STATES ---
  const [selectedUser, setSelectedUser] = useState('');
  const [analysis, setAnalysis] = useState(null);

  // --- TAB 2 (COMPARISON) STATES ---
  const [userA, setUserA] = useState('');
  const [userB, setUserB] = useState('');
  const [analysisA, setAnalysisA] = useState(null);
  const [analysisB, setAnalysisB] = useState(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // 1. On page load, fetch user list and exchange overview
  useEffect(() => {
    axios.get(`${API_BASE}/api/users`)
      .then(res => setUsers(res.data))
      .catch(err => console.error("User list error:", err));

    axios.get(`${API_BASE}/api/exchange-overview`)
      .then(res => setOverview(res.data))
      .catch(err => console.error("Exchange overview error:", err));
  }, []);

  // 2. Fetch Single User Analysis
  useEffect(() => {
    if (selectedUser) {
      setLoading(true);
      axios.get(`${API_BASE}/api/user-analysis/${selectedUser}`)
        .then(res => {
          setAnalysis(res.data);
          setLoading(false);
        })
        .catch(() => setError('Failed to load data.'));
    }
  }, [selectedUser]);

  // 3. Fetch Comparison (Versus) Data
  useEffect(() => {
    if (userA) axios.get(`${API_BASE}/api/user-analysis/${userA}`).then(res => setAnalysisA(res.data));
  }, [userA]);

  useEffect(() => {
    if (userB) axios.get(`${API_BASE}/api/user-analysis/${userB}`).then(res => setAnalysisB(res.data));
  }, [userB]);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white font-sans">
      {/* HEADER */}
      <h1 className="text-4xl font-black mb-8 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 via-emerald-400 to-purple-500 uppercase tracking-tighter">
        Investor Analysis Center
      </h1>

      {/* 🧭 TAB MENU (TAB SWITCHER) */}
      <div className="flex justify-center mb-12">
        <div className="bg-slate-800/80 p-1.5 rounded-2xl border border-slate-700 inline-flex shadow-2xl backdrop-blur-md">
          <button
            onClick={() => setActiveTab('single')}
            className={`px-10 py-3 rounded-xl font-black transition-all duration-300 ${activeTab === 'single' ? 'bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.4)]' : 'text-slate-400 hover:text-white'}`}
          >
            📊 GENERAL
          </button>
          <button
            onClick={() => setActiveTab('compare')}
            className={`px-10 py-3 rounded-xl font-black transition-all duration-300 ${activeTab === 'compare' ? 'bg-blue-600 text-white shadow-[0_0_20px_rgba(37,99,235,0.4)]' : 'text-slate-400 hover:text-white'}`}
          >
            ⚔️ COMPARE
          </button>
        </div>
      </div>

      {/* ====================================================== */}
      {/* --- TAB 1: INVESTOR SUMMARY --- */}
      {/* ====================================================== */}
      {activeTab === 'single' && (
        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {/* 🏆 Leadership Panel */}
          {overview && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10 bg-slate-900/40 p-8 rounded-[2.5rem] border border-blue-500/20 shadow-2xl backdrop-blur-sm">
              <div className="text-center border-r border-slate-700/50 last:border-0 px-4">
                <div className="text-blue-400 text-xs font-bold uppercase mb-2 tracking-widest">🏆 Exchange King</div>
                <div className="text-3xl font-black text-white">{overview.king?.username}</div>
                <div className="text-emerald-400 text-sm font-mono font-bold mt-1">%{overview.king?.pnl_percent} Profit Rate</div>
              </div>
              <div className="text-center border-r border-slate-700/50 last:border-0 px-4">
                <div className="text-orange-400 text-xs font-bold uppercase mb-2 tracking-widest">💰 Total Platform Volume</div>
                <div className="text-3xl font-black text-white">${overview.total_liquidity?.toLocaleString()}</div>
                <div className="text-slate-500 text-xs mt-1 uppercase font-bold">{overview.total_investors} Active Wallets</div>
              </div>
              <div className="text-center px-4">
                <div className="text-purple-400 text-xs font-bold uppercase mb-2 tracking-widest">🔥 Favorite Coin</div>
                <div className="text-3xl font-black text-white uppercase">{overview.most_popular_coin}</div>
                <div className="text-slate-500 text-xs mt-1 uppercase font-bold">Most Preferred</div>
              </div>
            </div>
          )}

          {/* Investor Selection Dropdown */}
          <div className="flex justify-center mb-10">
            <select
              value={selectedUser}
              onChange={(e) => setSelectedUser(e.target.value)}
              className="bg-slate-800 border-2 border-emerald-500/30 text-white p-4 rounded-2xl w-80 outline-none focus:border-emerald-500 transition-all font-bold shadow-2xl cursor-pointer"
            >
              <option value="">Select Investor...</option>
              {users.map(u => <option key={u.username} value={u.username}>{u.username}</option>)}
            </select>
          </div>

          {loading && <div className="text-center animate-pulse text-emerald-400 text-xl font-bold">Loading Data...</div>}

          {analysis && !loading && (
            <div className="space-y-8">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700 shadow-xl">
                  <div className="text-slate-400 text-xs font-bold uppercase mb-2">Wallet Balance</div>
                  <div className="text-4xl font-black text-white">${analysis.wallet_balance?.toLocaleString()}</div>
                </div>
                <div className={`bg-slate-800/50 p-8 rounded-3xl border shadow-xl ${analysis.total_pnl >= 0 ? 'border-emerald-500/50' : 'border-red-500/50'}`}>
                  <div className="text-slate-400 text-xs font-bold uppercase mb-2">Total Profit/Loss</div>
                  <div className={`text-4xl font-black ${analysis.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {analysis.total_pnl >= 0 ? '+' : ''}${analysis.total_pnl?.toLocaleString()}
                  </div>
                </div>
                <div className="bg-slate-800/50 p-8 rounded-3xl border border-slate-700 shadow-xl">
                  <div className="text-slate-400 text-xs font-bold uppercase mb-2">Account Status</div>
                  <div className={`text-3xl font-black ${analysis.overall_status === 'Profit' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {analysis.overall_status === 'Profit' ? '📈 IN PROFIT' : '📉 IN LOSS'}
                  </div>
                </div>
              </div>

              {/* Portfolio Table */}
              <div className="bg-slate-800/50 rounded-[2rem] border border-slate-700 overflow-hidden shadow-2xl backdrop-blur-sm">
                <div className="p-6 bg-slate-900/50 border-b border-slate-700 flex justify-between items-center">
                  <h3 className="text-xl font-black text-slate-200 uppercase tracking-tighter">Portfolio Assets</h3>
                  <span className="text-slate-500 text-xs font-bold uppercase">{analysis.portfolio_details.length} Active Assets</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-900/80 text-slate-400 uppercase text-[10px] font-black tracking-widest">
                      <tr>
                        <th className="p-5">Asset</th>
                        <th className="p-5 text-center">Amount</th>
                        <th className="p-5 text-center">Buy Price</th>
                        <th className="p-5 text-center">Current Price</th>
                        <th className="p-5 text-right">Profit/Loss ($)</th>
                        <th className="p-5 text-right">Change (%)</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/50 text-sm">
                      {analysis.portfolio_details.map((item, idx) => (
                        <tr key={idx} className="hover:bg-slate-700/30 transition-all group">
                          <td className="p-5 font-black text-emerald-400 text-base">{item.coin.toUpperCase()}</td>
                          <td className="p-5 text-center font-mono font-bold">{item.amount}</td>
                          <td className="p-5 text-center text-slate-400 font-mono">${item.buy_price.toLocaleString()}</td>
                          <td className="p-5 text-center text-white font-mono font-bold">${item.current_price.toLocaleString()}</td>
                          <td className={`p-5 text-right font-black ${item.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {item.pnl >= 0 ? '+' : ''}{item.pnl.toLocaleString()}
                          </td>
                          <td className={`p-5 text-right font-black ${item.pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            <div className="flex items-center justify-end gap-1">
                              {item.pnl_percent >= 0 ? '▲' : '▼'}
                              %{Math.abs(item.pnl_percent)}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ====================================================== */}
      {/* --- TAB 2: COMPARISON (VERSUS MODE) --- */}
      {/* ====================================================== */}
      {activeTab === 'compare' && (
        <div className="animate-in fade-in zoom-in duration-500">
          {/* Selection Panels */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
            <div className="bg-red-500/5 p-8 rounded-[2rem] border border-red-500/20 shadow-lg">
              <label className="block text-red-500 text-xs font-black mb-4 uppercase text-center tracking-[0.3em]">Red Corner</label>
              <select value={userA} onChange={(e) => setUserA(e.target.value)} className="w-full bg-slate-800 border-2 border-red-500/30 text-white p-4 rounded-2xl outline-none font-bold focus:border-red-500 shadow-xl transition-all">
                <option value="">Select Investor A...</option>
                {users.map(u => <option key={u.username} value={u.username}>{u.username}</option>)}
              </select>
            </div>
            <div className="bg-blue-500/5 p-8 rounded-[2rem] border border-blue-500/20 shadow-lg">
              <label className="block text-blue-500 text-xs font-black mb-4 uppercase text-center tracking-[0.3em]">Blue Corner</label>
              <select value={userB} onChange={(e) => setUserB(e.target.value)} className="w-full bg-slate-800 border-2 border-blue-500/30 text-white p-4 rounded-2xl outline-none font-bold focus:border-blue-500 shadow-xl transition-all">
                <option value="">Select Investor B...</option>
                {users.map(u => <option key={u.username} value={u.username}>{u.username}</option>)}
              </select>
            </div>
          </div>

          {/* Battle Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* INVESTOR A */}
            <div className="bg-slate-800/40 p-8 rounded-[3rem] border-l-[12px] border-red-500 shadow-2xl backdrop-blur-md">
              {analysisA ? (
                <div>
                  <div className="text-center mb-8">
                    <h2 className="text-5xl font-black text-red-500 italic mb-3 tracking-tighter uppercase">{analysisA.username}</h2>
                    <div className="flex justify-center gap-6 text-xs font-black uppercase text-slate-500 tracking-widest">
                      <span>Wallet: <b className="text-white">${analysisA.wallet_balance?.toLocaleString()}</b></span>
                      <span>Net PnL: <b className={analysisA.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}>${analysisA.total_pnl?.toLocaleString()}</b></span>
                    </div>
                  </div>

                  {/* Detailed Asset List A */}
                  <div className="space-y-3">
                    <div className="grid grid-cols-4 text-[10px] uppercase font-black text-slate-600 px-3 tracking-widest mb-2">
                      <span>Asset</span>
                      <span className="text-center">Amount</span>
                      <span className="text-center">Current Price</span>
                      <span className="text-right">Status</span>
                    </div>
                    {analysisA.portfolio_details.map((p, i) => (
                      <div key={i} className="grid grid-cols-4 items-center bg-slate-900/60 p-4 rounded-2xl border border-white/5 group hover:bg-red-500/10 transition-all">
                        <span className="font-black text-sm text-red-400 uppercase tracking-tighter">{p.coin}</span>
                        <span className="text-center font-mono font-bold text-xs">{p.amount}</span>
                        <span className="text-center font-mono font-bold text-xs text-slate-300">${p.current_price.toLocaleString()}</span>
                        <span className={`text-right font-black text-xs ${p.pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {p.pnl_percent >= 0 ? '▲' : '▼'} %{Math.abs(p.pnl_percent)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : <div className="h-64 flex items-center justify-center text-slate-700 italic font-black uppercase tracking-widest animate-pulse text-xl">Corner A Empty...</div>}
            </div>

            {/* INVESTOR B */}
            <div className="bg-slate-800/40 p-8 rounded-[3rem] border-r-[12px] border-blue-500 shadow-2xl backdrop-blur-md">
              {analysisB ? (
                <div>
                  <div className="text-center mb-8">
                    <h2 className="text-5xl font-black text-blue-500 italic mb-3 tracking-tighter uppercase">{analysisB.username}</h2>
                    <div className="flex justify-center gap-6 text-xs font-black uppercase text-slate-500 tracking-widest">
                      <span>Wallet: <b className="text-white">${analysisB.wallet_balance?.toLocaleString()}</b></span>
                      <span>Net PnL: <b className={analysisB.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}>${analysisB.total_pnl?.toLocaleString()}</b></span>
                    </div>
                  </div>

                  {/* Detailed Asset List B */}
                  <div className="space-y-3">
                    <div className="grid grid-cols-4 text-[10px] uppercase font-black text-slate-600 px-3 tracking-widest mb-2">
                      <span>Asset</span>
                      <span className="text-center">Amount</span>
                      <span className="text-center">Current Price</span>
                      <span className="text-right">Status</span>
                    </div>
                    {analysisB.portfolio_details.map((p, i) => (
                      <div key={i} className="grid grid-cols-4 items-center bg-slate-900/60 p-4 rounded-2xl border border-white/5 group hover:bg-blue-500/10 transition-all">
                        <span className="font-black text-sm text-blue-400 uppercase tracking-tighter">{p.coin}</span>
                        <span className="text-center font-mono font-bold text-xs">{p.amount}</span>
                        <span className="text-center font-mono font-bold text-xs text-slate-300">${p.current_price.toLocaleString()}</span>
                        <span className={`text-right font-black text-xs ${p.pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                          {p.pnl_percent >= 0 ? '▲' : '▼'} %{Math.abs(p.pnl_percent)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : <div className="h-64 flex items-center justify-center text-slate-700 italic font-black uppercase tracking-widest animate-pulse text-xl">Corner B Empty...</div>}
            </div>
          </div>

          {/* WINNER PANEL */}
          {analysisA && analysisB && (
            <div className="mt-16 p-12 bg-slate-900/90 rounded-[5rem] border border-yellow-500/20 text-center shadow-[0_0_50px_rgba(234,179,8,0.1)] relative overflow-hidden group">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500/5 via-transparent to-blue-500/5 opacity-50"></div>
              <h3 className="text-slate-500 uppercase tracking-[0.6em] text-[11px] mb-6 font-black relative z-10">CURRENT PERFORMANCE LEADER</h3>
              <div className="text-7xl font-black text-yellow-400 italic tracking-tighter relative z-10 drop-shadow-[0_0_20px_rgba(250,204,21,0.5)] transition-transform group-hover:scale-110 duration-700 select-none">
                {analysisA.total_pnl > analysisB.total_pnl ? analysisA.username : analysisB.username} 👑
              </div>
              <p className="mt-6 text-slate-500 text-xs font-bold tracking-widest uppercase relative z-10 opacity-60">
                Leading Based on Net Profit
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default InvestorAnalysis;