import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link, useSearchParams } from 'react-router-dom';
import API_BASE from '../config';

function Home() {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams, setSearchParams] = useSearchParams();
  const [searchTerm, setSearchTerm] = useState('');
  
  const currentPage = parseInt(searchParams.get('page') || '1', 10);
  const setCurrentPage = (page) => {
    setSearchParams({ page: page.toString() });
  };
  
  const itemsPerPage = 10;

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        const res = await axios.get(`${API_BASE}/api/market-coins`);
        setCoins(res.data);
      } catch (err) {
        console.error("Failed to fetch data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCoins();
  }, []);

  useEffect(() => {
    if (searchTerm) {
      setSearchParams({ page: '1' });
    }
  }, [searchTerm]);

  const filteredCoins = coins.filter(coin => 
    coin.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    coin.symbol?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentCoins = filteredCoins.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredCoins.length / itemsPerPage);

  if (loading) return <div className="text-center mt-20 text-white animate-pulse">Loading Data...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 text-white">
      
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Market Overview</h1>
        <input 
          type="text" 
          placeholder="Search Coin (BTC, Solana...)" 
          className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      <div className="bg-slate-800 rounded-2xl overflow-hidden shadow-xl border border-slate-700">
        <table className="w-full text-left border-collapse table-fixed">
          <thead className="bg-slate-900 text-slate-400 uppercase text-xs">
            <tr>
              <th className="p-4 w-[40%]">Coin</th>
              <th className="p-4 w-[15%]">Symbol</th>
              <th className="p-4 w-[25%]">Price (USD)</th>
              <th className="p-4 w-[20%] text-center">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {currentCoins.map((coin) => (
              <tr key={coin.id} className="hover:bg-slate-700 transition-colors">
                <td className="p-4 font-semibold">
                  <div className="flex items-center gap-3">
                    <img 
                      src={coin.image} 
                      alt={coin.name} 
                      className="w-8 h-8 rounded-full bg-slate-600 flex-shrink-0" 
                      onError={(e) => {
                        e.target.onerror = null;
                        e.target.src = `https://ui-avatars.com/api/?name=${coin.symbol}&background=random&color=fff&size=64&bold=true`;
                      }}
                    />
                    <span className="truncate">{coin.name}</span>
                  </div>
                </td>
                <td className="p-4 text-slate-400 uppercase">{coin.symbol}</td>
                <td className="p-4">
                  <div className="flex items-center gap-2">
                    <span className="text-green-400 font-mono font-bold">
                      ${coin.current_price?.toLocaleString()}
                    </span>
                    {coin.price_change_24h !== undefined && coin.price_change_24h !== null && (
                      <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${
                        coin.price_change_24h >= 0 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-red-500/20 text-red-400'
                      }`}>
                        {coin.price_change_24h >= 0 ? '▲' : '▼'} {Math.abs(coin.price_change_24h).toFixed(2)}%
                      </span>
                    )}
                  </div>
                </td>
                <td className="p-4 text-center">
                  <Link 
                    to={`/coin/${coin.id}`} 
                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all inline-block"
                  >
                    Details & Chart
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-center mt-8 gap-2">
        <button 
          onClick={() => setCurrentPage(Math.max(currentPage - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 disabled:opacity-50"
        >
          &lt; Previous
        </button>
        <span className="px-4 py-2 bg-slate-900 rounded-lg text-slate-400 border border-slate-800">
          Page {currentPage} / {totalPages}
        </span>
        <button 
          onClick={() => setCurrentPage(Math.min(currentPage + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 disabled:opacity-50"
        >
          Next &gt;
        </button>
      </div>
    </div>
  );
}

export default Home;