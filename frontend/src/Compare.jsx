import { useState, useEffect } from 'react';
import axios from 'axios';

function SimpleChart({ data, coins, normalized }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-slate-400">Veri bulunamadı</div>;
  }

  const width = 800;
  const height = 400;
  const margin = { top: 20, right: 80, bottom: 60, left: 80 };

  // Veri aralıklarını hesapla
  const allValues = coins.flatMap(coin => data.map(d => d[coin]).filter(v => v != null && !isNaN(v) && isFinite(v)));
  if (allValues.length === 0) {
    return <div className="flex items-center justify-center h-full text-slate-400">Geçerli veri bulunamadı</div>;
  }

  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const valueRange = maxValue - minValue || 1;

  // Ölçek fonksiyonları
  const xScale = (index) => margin.left + (index / (data.length - 1)) * (width - margin.left - margin.right);
  const yScale = (value) => margin.top + ((maxValue - value) / valueRange) * (height - margin.top - margin.bottom);

  // Tarih formatı
  const formatDate = (dateString) => {
    const options = { month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('tr-TR', options);
  };

  // Renkler
  const availableCoins = [
    { id: 'bitcoin', name: 'Bitcoin', color: '#f7931a' },
    { id: 'ethereum', name: 'Ethereum', color: '#627eea' },
    { id: 'solana', name: 'Solana', color: '#14f195' },
    { id: 'avalanche-2', name: 'Avalanche', color: '#e84142' },
    { id: 'ripple', name: 'Ripple', color: '#00aae4' },
  ];

  const getColor = (coinId) => {
    const coin = availableCoins.find(c => c.id === coinId);
    return coin?.color || '#8884d8';
  };

  // Çizgi noktalarını oluştur
  const createPath = (coinId) => {
    const points = data.map((d, i) => {
      const value = d[coinId];
      if (value == null || isNaN(value) || !isFinite(value)) return null;
      const x = xScale(i);
      const y = yScale(value);
      return `${x},${y}`;
    }).filter(p => p != null);

    if (points.length < 2) return '';
    return `M ${points.join(' L ')}`;
  };

  return (
    <div className="w-full h-full">
      <svg width="100%" height="100%" viewBox={`0 0 ${width} ${height}`} className="bg-slate-900/50 rounded-lg">
        {/* Grid lines */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => (
          <line
            key={`h-${ratio}`}
            x1={margin.left}
            y1={margin.top + innerHeight * ratio}
            x2={width - margin.right}
            y2={margin.top + innerHeight * ratio}
            stroke="#334155"
            strokeWidth="1"
            strokeDasharray="2,2"
          />
        ))}

        {/* Y-axis labels */}
        {[0, 0.25, 0.5, 0.75, 1].map(ratio => {
          const value = minValue + valueRange * ratio;
          return (
            <text
              key={`y-${ratio}`}
              x={margin.left - 10}
              y={margin.top + innerHeight * ratio + 4}
              textAnchor="end"
              fill="#94a3b8"
              fontSize="12"
            >
              {normalized ? value.toFixed(0) : `$${value.toLocaleString()}`}
            </text>
          );
        })}

        {/* X-axis labels */}
        {data.map((d, i) => {
          if (i % Math.ceil(data.length / 10) === 0) {
            return (
              <text
                key={`x-${i}`}
                x={margin.left + xScale(i)}
                y={height - margin.bottom + 20}
                textAnchor="middle"
                fill="#94a3b8"
                fontSize="12"
              >
                {formatDate(d.timestamp)}
              </text>
            );
          }
          return null;
        })}

        {/* Çizgiler */}
        {coins.map(coinId => {
          const path = createPath(coinId);
          console.log(`Path for ${coinId}:`, path.substring(0, 100));
          return (
            <path
              key={coinId}
              d={path}
              fill="none"
              stroke={getColor(coinId)}
              strokeWidth="2"
            />
          );
        })}

        {/* Legend */}
        <g transform={`translate(${width - margin.right + 10}, ${margin.top})`}>
          {coins.map((coinId, index) => (
            <g key={coinId} transform={`translate(0, ${index * 20})`}>
              <line
                x1="0"
                y1="0"
                x2="20"
                y2="0"
                stroke={getColor(coinId)}
                strokeWidth="2"
              />
              <text
                x="25"
                y="4"
                fill="#94a3b8"
                fontSize="12"
              >
                {availableCoins.find(c => c.id === coinId)?.name || coinId}
              </text>
            </g>
          ))}
        </g>
      </svg>
    </div>
  );
}

function Compare() {
  const [activeTab, setActiveTab] = useState('compare');
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedCoins, setSelectedCoins] = useState(['bitcoin', 'ethereum']);
  const [normalized, setNormalized] = useState(false);

  // Popüler coinler için seçenekler
  const availableCoins = [
    { id: 'bitcoin', name: 'Bitcoin', color: '#f7931a' },
    { id: 'ethereum', name: 'Ethereum', color: '#627eea' },
    { id: 'solana', name: 'Solana', color: '#14f195' },
    { id: 'avalanche-2', name: 'Avalanche', color: '#e84142' },
    { id: 'ripple', name: 'Ripple', color: '#00aae4' },
  ];

  useEffect(() => {
    const fetchSeries = async () => {
      setLoading(true);
      setError(null);
      try {
        const coinsParam = selectedCoins.join(',');
        const response = await axios.get(`http://127.0.0.1:5000/api/market/series?coins=${coinsParam}`);

        // API'den gelen veriyi grafik formatına dönüştür
        const { timestamps, ...coinData } = response.data;
        const data = timestamps.map((timestamp, index) => {
          const dataPoint = { timestamp };
          selectedCoins.forEach(coin => {
            if (coinData[coin] && coinData[coin][index] !== null) {
              dataPoint[coin] = coinData[coin][index];
            }
          });
          return dataPoint;
        });

        setChartData(data);
      } catch (err) {
        console.error('Zaman serisi verisi alınamadı:', err);
        setError('Zaman serisi verisi alınamadı. Backend çalışıyor mu?');
      } finally {
        setLoading(false);
      }
    };

    if (selectedCoins.length > 0) {
      fetchSeries();
    }
  }, [selectedCoins]);

  // Normalizasyon uygula
  const processedData = normalized && chartData.length > 0 ? chartData.map(point => {
    const normalizedPoint = { timestamp: point.timestamp };
    selectedCoins.forEach(coin => {
      if (point[coin] !== undefined) {
        // İlk geçerli değeri bul
        const firstValue = chartData.find(p => p[coin] !== undefined)?.[coin];
        if (firstValue && firstValue > 0) {
          normalizedPoint[coin] = (point[coin] / firstValue) * 100;
        }
      }
    });
    return normalizedPoint;
  }) : chartData;

  // Verileri analiz et
  const analyzeData = (data, coins) => {
    if (!data || data.length < 2) return null;

    const analysis = {};
    const availableCoins = [
      { id: 'bitcoin', name: 'Bitcoin' },
      { id: 'ethereum', name: 'Ethereum' },
      { id: 'solana', name: 'Solana' },
      { id: 'avalanche-2', name: 'Avalanche' },
      { id: 'ripple', name: 'Ripple' },
    ];

    coins.forEach(coinId => {
      const coinData = data.map(d => d[coinId]).filter(v => v != null && !isNaN(v));
      if (coinData.length >= 2) {
        const firstValue = coinData[0];
        const lastValue = coinData[coinData.length - 1];
        const changePercent = ((lastValue - firstValue) / firstValue) * 100;

        analysis[coinId] = {
          name: availableCoins.find(c => c.id === coinId)?.name || coinId,
          changePercent,
          firstValue,
          lastValue,
          isPositive: changePercent > 0
        };
      }
    });

    return analysis;
  };

  const analysis = analyzeData(processedData, selectedCoins);

  // Analiz metnini oluştur
  const generateAnalysisText = (analysis) => {
    if (!analysis || Object.keys(analysis).length === 0) return "Yeterli veri bulunamadı.";

    const sortedCoins = Object.entries(analysis).sort((a, b) => b[1].changePercent - a[1].changePercent);
    const bestPerformer = sortedCoins[0];
    const worstPerformer = sortedCoins[sortedCoins.length - 1];

    const timeFrame = processedData.length > 20 ? "son dönemde" : "verilen dönemde";
    const period = processedData.length > 20 ? "ayın" : "dönemin";

    let analysisText = `${timeFrame} `;

    if (bestPerformer[1].isPositive) {
      analysisText += `${bestPerformer[1].name} %${bestPerformer[1].changePercent.toFixed(1)} artış göstererek `;
      if (sortedCoins.length > 1) {
        analysisText += `piyasayı domine etti. `;
      }
    } else {
      analysisText += `${bestPerformer[1].name} %${Math.abs(bestPerformer[1].changePercent).toFixed(1)} düşüş yaşadı. `;
    }

    if (sortedCoins.length > 1 && worstPerformer[1].changePercent !== bestPerformer[1].changePercent) {
      if (worstPerformer[1].isPositive) {
        analysisText += `${worstPerformer[1].name} ise %${worstPerformer[1].changePercent.toFixed(1)} artış gösterdi.`;
      } else {
        analysisText += `${worstPerformer[1].name} ise %${Math.abs(worstPerformer[1].changePercent).toFixed(1)} düşüş yaşadı.`;
      }
    }

    // Trend analizi
    const positiveCoins = sortedCoins.filter(([_, data]) => data.isPositive);
    const negativeCoins = sortedCoins.filter(([_, data]) => !data.isPositive);

    if (positiveCoins.length > negativeCoins.length) {
      analysisText += ` Genel olarak yükseliş eğilimi hakim.`;
    } else if (negativeCoins.length > positiveCoins.length) {
      analysisText += ` Genel olarak düşüş eğilimi gözleniyor.`;
    } else {
      analysisText += ` Piyasa dengede.`;
    }

    return analysisText;
  };

  const toggleCoin = (coinId) => {
    setSelectedCoins(prev =>
      prev.includes(coinId)
        ? prev.filter(id => id !== coinId)
        : [...prev, coinId]
    );
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-white p-8 font-sans">
      {/* Tab Navigation */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="flex justify-center">
          <div className="bg-slate-800/70 rounded-xl p-1 border border-slate-700/40">
            <button
              onClick={() => window.location.href = '/'}
              className={`px-6 py-2 rounded-lg font-semibold transition-all duration-300 ${
                activeTab === 'dashboard'
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Ana Panel
            </button>
            <button
              onClick={() => setActiveTab('compare')}
              className={`px-6 py-2 rounded-lg font-semibold transition-all duration-300 ${
                activeTab === 'compare'
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              Coin Karşılaştırma
            </button>
          </div>
        </div>
      </div>

      <header className="mb-12 text-center">
        <h1 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-purple-500 to-pink-500 drop-shadow-lg">
          Coin Karşılaştırma ve Analizi
        </h1>
        <p className="text-slate-400 mt-3 text-lg">Fiyat Geçmişlerini Karşılaştırın ve Analiz Edin</p>
      </header>

      {/* Analiz Bölümü */}
      {analysis && Object.keys(analysis).length > 0 && (
        <div className="max-w-4xl mx-auto mb-8 p-6 bg-gradient-to-r from-blue-900/20 to-purple-900/20 border border-blue-500/20 rounded-xl backdrop-blur-sm">
          <h3 className="text-2xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            📊 Analiz Sayfası
          </h3>

          {/* Performans Tablosu */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {Object.entries(analysis).map(([coinId, data]) => (
              <div key={coinId} className="bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-slate-300">{data.name}</span>
                  <span className={`text-sm font-bold px-2 py-1 rounded ${
                    data.isPositive
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}>
                    {data.isPositive ? '+' : ''}{data.changePercent.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-slate-500">
                  {normalized ? 'Normalized' : `$${data.lastValue.toLocaleString()}`}
                </div>
              </div>
            ))}
          </div>

          {/* Analiz Metni */}
          <div className="bg-slate-800/30 p-4 rounded-lg border border-slate-600/30">
            <p className="text-slate-300 leading-relaxed">
              {generateAnalysisText(analysis)}
            </p>
          </div>
        </div>
      )}

      {/* Coin Seçimi */}
      <div className="max-w-4xl mx-auto mb-8">
        <div className="bg-slate-800/70 rounded-2xl shadow-xl p-6 border border-slate-700/40">
          <h2 className="text-2xl font-bold mb-4 text-center">Karşılaştırılacak Coinleri Seçin</h2>
          <div className="flex flex-wrap justify-center gap-4 mb-4">
            {availableCoins.map((coin) => (
              <button
                key={coin.id}
                onClick={() => toggleCoin(coin.id)}
                className={`px-4 py-2 rounded-lg font-semibold transition-all duration-300 ${
                  selectedCoins.includes(coin.id)
                    ? 'bg-slate-700 text-white ring-2'
                    : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-white'
                }`}
                style={{
                  borderColor: selectedCoins.includes(coin.id) ? coin.color : 'transparent',
                  boxShadow: selectedCoins.includes(coin.id) ? `0 0 10px ${coin.color}40` : 'none'
                }}
              >
                {coin.name}
              </button>
            ))}
          </div>

          {/* Normalizasyon Toggle */}
          <div className="flex justify-center">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={normalized}
                onChange={(e) => setNormalized(e.target.checked)}
                className="w-4 h-4 text-blue-600 bg-slate-700 border-slate-600 rounded focus:ring-blue-500"
              />
              <span className="text-slate-300">Fiyatları Normalize Et (Başlangıç = 100)</span>
            </label>
          </div>
        </div>
      </div>

      {/* Grafik */}
      <div className="max-w-7xl mx-auto">
        <div className="bg-slate-800/50 backdrop-blur-xl p-8 rounded-3xl shadow-2xl border border-slate-700/50">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h2 className="text-3xl font-bold flex items-center gap-3">
                Coin Karşılaştırma Grafiği
              </h2>
              <p className="text-slate-500 text-sm mt-1">
                {normalized ? 'Normalize edilmiş fiyatlar (100 = başlangıç)' : 'Gerçek fiyatlar (USD)'}
              </p>
            </div>
            <div className="px-4 py-1 bg-green-500/10 border border-green-500/20 rounded-full">
              <span className="text-green-400 text-sm font-semibold animate-pulse">● Canlı Veri</span>
            </div>
          </div>

          <div className="h-[600px] w-full bg-slate-900/50 rounded-2xl p-4 border border-slate-700/30">
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
              <SimpleChart data={processedData} coins={selectedCoins} normalized={normalized} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Compare;