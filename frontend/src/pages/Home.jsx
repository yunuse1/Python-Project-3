import { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';

function Home() {
  const [coins, setCoins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  
  const itemsPerPage = 10; // Her sayfada kaç coin görünsün

  useEffect(() => {
    const fetchCoins = async () => {
      try {
        // Backend'deki sadece market verisi olan coinleri çeken endpoint
        const res = await axios.get('http://127.0.0.1:5000/api/market-coins');
        setCoins(res.data);
      } catch (err) {
        console.error("Veri çekilemedi:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCoins();
  }, []);

  // Arama filtresi
  const filteredCoins = coins.filter(coin => 
    coin.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
    coin.symbol?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination Mantığı
  const indexOfLastItem = currentPage * itemsPerPage;
  const indexOfFirstItem = indexOfLastItem - itemsPerPage;
  const currentCoins = filteredCoins.slice(indexOfFirstItem, indexOfLastItem);
  const totalPages = Math.ceil(filteredCoins.length / itemsPerPage);

  if (loading) return <div className="text-center mt-20 text-white animate-pulse">Veriler Yükleniyor...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 text-white">
      
      {/* Arama Kutusu */}
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-3xl font-bold">Piyasa Genel Bakış</h1>
        <input 
          type="text" 
          placeholder="Coin Ara (BTC, Solana...)" 
          className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Tablo */}
      <div className="bg-slate-800 rounded-2xl overflow-hidden shadow-xl border border-slate-700">
        <table className="w-full text-left border-collapse">
          <thead className="bg-slate-900 text-slate-400 uppercase text-xs">
            <tr>
              <th className="p-4">Coin</th>
              <th className="p-4">Sembol</th>
              <th className="p-4">Fiyat (USD)</th>
              <th className="p-4 text-center">İşlem</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {currentCoins.map((coin) => (
              <tr key={coin.id} className="hover:bg-slate-700 transition-colors">
                <td className="p-4 font-semibold flex items-center gap-3">
                  <img 
                    src={coin.image} 
                    alt={coin.name} 
                    className="w-8 h-8 rounded-full bg-slate-600" 
                    onError={(e) => {
                      e.target.onerror = null;
                      e.target.src = `https://ui-avatars.com/api/?name=${coin.symbol}&background=random&color=fff&size=64&bold=true`;
                    }}
                  />
                  {coin.name}
                </td>
                <td className="p-4 text-slate-400 uppercase">{coin.symbol}</td>
                <td className="p-4 text-green-400 font-mono font-bold">
                  ${coin.current_price?.toLocaleString()}
                </td>
                <td className="p-4 text-center">
                  <Link 
                    to={`/coin/${coin.id}`} 
                    className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all"
                  >
                    Detay & Grafik
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Butonları */}
      <div className="flex justify-center mt-8 gap-2">
        <button 
          onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
          disabled={currentPage === 1}
          className="px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 disabled:opacity-50"
        >
          &lt; Önceki
        </button>
        <span className="px-4 py-2 bg-slate-900 rounded-lg text-slate-400 border border-slate-800">
          Sayfa {currentPage} / {totalPages}
        </span>
        <button 
          onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
          disabled={currentPage === totalPages}
          className="px-4 py-2 bg-slate-800 rounded-lg hover:bg-slate-700 disabled:opacity-50"
        >
          Sonraki &gt;
        </button>
      </div>
    </div>
  );
}

export default Home;