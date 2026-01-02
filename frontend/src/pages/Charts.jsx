import React, { useState } from 'react';

function Charts() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  
  // Charts created with Seaborn
  const charts = [
    // Bitcoin
    { id: 'bitcoin_price_distribution', title: 'Bitcoin - Price Distribution', category: 'bitcoin', description: 'Price distribution analysis with Histogram + KDE and Box Plot' },
    { id: 'bitcoin_returns_analysis', title: 'Bitcoin - Returns Analysis', category: 'bitcoin', description: 'Violin Plot, Q-Q Plot and returns category distribution' },
    { id: 'bitcoin_time_series', title: 'Bitcoin - Time Series', category: 'bitcoin', description: 'Price trend, rolling statistics and daily returns' },
    { id: 'bitcoin_anomaly_detection', title: 'Bitcoin - Anomaly Detection', category: 'bitcoin', description: 'Anomaly detection visualization with Z-Score' },
    // Ethereum
    { id: 'ethereum_price_distribution', title: 'Ethereum - Price Distribution', category: 'ethereum', description: 'Price distribution analysis with Histogram + KDE and Box Plot' },
    { id: 'ethereum_returns_analysis', title: 'Ethereum - Returns Analysis', category: 'ethereum', description: 'Violin Plot, Q-Q Plot and returns category distribution' },
    { id: 'ethereum_time_series', title: 'Ethereum - Time Series', category: 'ethereum', description: 'Price trend, rolling statistics and daily returns' },
    { id: 'ethereum_anomaly_detection', title: 'Ethereum - Anomaly Detection', category: 'ethereum', description: 'Anomaly detection visualization with Z-Score' },
    // Solana
    { id: 'solana_price_distribution', title: 'Solana - Price Distribution', category: 'solana', description: 'Price distribution analysis with Histogram + KDE and Box Plot' },
    { id: 'solana_returns_analysis', title: 'Solana - Returns Analysis', category: 'solana', description: 'Violin Plot, Q-Q Plot and returns category distribution' },
    { id: 'solana_time_series', title: 'Solana - Time Series', category: 'solana', description: 'Price trend, rolling statistics and daily returns' },
    { id: 'solana_anomaly_detection', title: 'Solana - Anomaly Detection', category: 'solana', description: 'Anomaly detection visualization with Z-Score' },
    // Comparison
    { id: 'correlation_heatmap', title: 'Correlation Heatmap', category: 'comparison', description: 'Returns correlation between 10 cryptocurrencies' },
    { id: 'volatility_comparison', title: 'Volatility Comparison', category: 'comparison', description: 'Risk-Return profile and volatility analysis' },
    { id: 'returns_pairplot', title: 'Returns Pair Plot', category: 'comparison', description: 'Inter-coin returns relationship scatter matrix' },
    { id: 'summary_dashboard', title: 'Summary Dashboard', category: 'comparison', description: 'Summary visualization of all analyses' },
  ];

  const categories = [
    { id: 'all', name: 'All', icon: '📊' },
    { id: 'bitcoin', name: 'Bitcoin', icon: '₿' },
    { id: 'ethereum', name: 'Ethereum', icon: 'Ξ' },
    { id: 'solana', name: 'Solana', icon: '◎' },
    { id: 'comparison', name: 'Comparison', icon: '📈' },
  ];

  const filteredCharts = selectedCategory === 'all' 
    ? charts 
    : charts.filter(c => c.category === selectedCategory);

  const [selectedImage, setSelectedImage] = useState(null);

  return (
    <div className="max-w-7xl mx-auto px-4 py-10 text-white">
      <h1 className="text-3xl font-bold mb-4 text-center bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-500">
        📊 Seaborn Visualizations
      </h1>
      <p className="text-center text-slate-400 mb-8">
        Statistical charts created with Python Seaborn library
      </p>

      {/* Kategori Filtreleri */}
      <div className="flex flex-wrap justify-center gap-2 mb-8">
        {categories.map(cat => (
          <button
            key={cat.id}
            onClick={() => setSelectedCategory(cat.id)}
            className={`px-4 py-2 rounded-xl font-medium transition-all ${
              selectedCategory === cat.id
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
            }`}
          >
            {cat.icon} {cat.name}
          </button>
        ))}
      </div>

      {/* Chart Count */}
      <p className="text-center text-slate-500 mb-6">
        Showing {filteredCharts.length} charts
      </p>

      {/* Grafik Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCharts.map(chart => (
          <div 
            key={chart.id}
            className="bg-slate-800/50 rounded-2xl border border-slate-700 overflow-hidden hover:border-blue-500 transition-all cursor-pointer group"
            onClick={() => setSelectedImage(chart)}
          >
            <div className="aspect-video bg-slate-900 flex items-center justify-center overflow-hidden">
              <img 
                src={`/plots/${chart.id}.png`}
                alt={chart.title}
                className="w-full h-full object-contain group-hover:scale-105 transition-transform"
                onError={(e) => {
                  e.target.onerror = null;
                  e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y="50" x="50" text-anchor="middle" fill="%23666">📊</text></svg>';
                }}
              />
            </div>
            <div className="p-4">
              <h3 className="font-bold text-white mb-1">{chart.title}</h3>
              <p className="text-sm text-slate-400">{chart.description}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Modal - Large View */}
      {selectedImage && (
        <div 
          className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-6xl w-full bg-slate-900 rounded-2xl overflow-hidden" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center p-4 border-b border-slate-700">
              <h2 className="text-xl font-bold text-white">{selectedImage.title}</h2>
              <button 
                onClick={() => setSelectedImage(null)}
                className="text-slate-400 hover:text-white text-2xl"
              >
                ✕
              </button>
            </div>
            <div className="p-4 bg-white">
              <img 
                src={`/plots/${selectedImage.id}.png`}
                alt={selectedImage.title}
                className="w-full h-auto"
              />
            </div>
            <div className="p-4 border-t border-slate-700">
              <p className="text-slate-300">{selectedImage.description}</p>
            </div>
          </div>
        </div>
      )}

      {/* Seaborn Info Card */}
      <div className="mt-12 bg-gradient-to-r from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700">
        <h2 className="text-xl font-bold mb-4 text-white">🐍 About Seaborn</h2>
        <div className="grid md:grid-cols-2 gap-6 text-slate-300">
          <div>
            <h3 className="font-semibold text-blue-400 mb-2">Functions Used</h3>
            <ul className="space-y-1 text-sm">
              <li>• <code className="bg-slate-700 px-1 rounded">sns.histplot()</code> - Histogram + KDE</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.boxplot()</code> - Box Plot (Quartiles)</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.violinplot()</code> - Violin Plot</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.heatmap()</code> - Correlation Heatmap</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.pairplot()</code> - Pair Plot (Scatter Matrix)</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.scatterplot()</code> - Scatter Plot</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.barplot()</code> - Bar Chart</li>
              <li>• <code className="bg-slate-700 px-1 rounded">sns.lineplot()</code> - Line Chart</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-green-400 mb-2">Statistical Analyses</h3>
            <ul className="space-y-1 text-sm">
              <li>• Price distribution and normality test (Q-Q Plot)</li>
              <li>• Returns volatility and risk analysis</li>
              <li>• Anomaly detection (Z-Score method)</li>
              <li>• Correlation matrix calculation</li>
              <li>• Rolling statistics (moving average)</li>
              <li>• Risk-Return profile analysis</li>
              <li>• Returns category distribution</li>
              <li>• Comparative volatility analysis</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Charts;
