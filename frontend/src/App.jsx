import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CoinDetail from './pages/CoinDetail';
import Compare from './pages/Compare';
import Analysis from './pages/Analysis';
import Report from './pages/Report';
import Charts from './pages/Charts';
import InvestorAnalysis from './pages/InvestorAnalysis';

// Yeni Eklenecek Güvenlik Sayfaları (Security Pages)
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import AdminDashboard from './pages/AdminDashboard';

// Rol ve Token kontrolü için basit yardımcı fonksiyonlar
const isAuthenticated = () => !!localStorage.getItem('token');
const isAdmin = () => localStorage.getItem('role') === 'Admin';

// Korumalı Rota (Sadece giriş yapanlar görebilir) - Authentication Required
const ProtectedRoute = ({ children }) => {
  if (!isAuthenticated()) {
    // Giriş yapmamışsa Login sayfasına yönlendir
    return <Navigate to="/login" replace />;
  }
  return children;
};

// Admin Rotası (Sadece Admin yetkisi olanlar görebilir) - RBAC (Role-Based Access Control)
const AdminRoute = ({ children }) => {
  if (!isAuthenticated() || !isAdmin()) {
    // Yetkisiz erişim denemesi (Unauthorized access prevented)
    return <Navigate to="/" replace />; 
  }
  return children;
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-[#0f172a] text-white font-sans selection:bg-blue-500 selection:text-white">
        <Navbar />
        <Routes>
          {/* Public Routes (Herkese Açık Sayfalar) */}
          <Route path="/" element={<Home />} />
          <Route path="/coin/:id" element={<CoinDetail />} />
          <Route path="/compare" element={<Compare />} />
          <Route path="/report" element={<Report />} />
          <Route path="/charts" element={<Charts />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Protected Routes (Sadece Giriş Yapan Kullanıcılar) */}
          <Route path="/analysis" element={
            <ProtectedRoute>
              <Analysis />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } />
          <Route path="/investors" element={
            <ProtectedRoute>
              <InvestorAnalysis />
            </ProtectedRoute>
          } />

          {/* Admin Route (Sadece Admin Rolü) - Unauthorized users must be blocked */}
          <Route path="/admin" element={
            <AdminRoute>
              <AdminDashboard />
            </AdminRoute>
          } />
        </Routes>
      </div>
    </Router>
  );
}

export default App;