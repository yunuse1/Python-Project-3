import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CoinDetail from './pages/CoinDetail';
import Compare from './pages/Compare';
import Analysis from './pages/Analysis';
import Report from './pages/Report';
import Charts from './pages/Charts';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#0f172a] text-white font-sans selection:bg-blue-500 selection:text-white">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/coin/:id" element={<CoinDetail />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/analysis" element={<Analysis />} />
          <Route path="/report" element={<Report />} />
          <Route path="/charts" element={<Charts />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;