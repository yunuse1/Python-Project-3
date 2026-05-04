import { Link, useLocation, useNavigate } from 'react-router-dom';

function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();

  // LocalStorage'dan yetkilendirme (Authentication) ve rol (RBAC) bilgilerini alıyoruz
  const token = localStorage.getItem('token');
  const role = localStorage.getItem('role');
  const isAuthenticated = !!token;
  const isAdmin = role === 'Admin';

  const handleHomeClick = (e) => {
    if (location.pathname === '/') {
      e.preventDefault();
      window.location.reload();
    }
  };

  const handleLogout = () => {
    // Çıkış yapıldığında token'ları temizle ve Login'e at
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    navigate('/login');
    window.location.reload(); // State'i tamamen sıfırlamak için sayfayı yenile
  };

  return (
    <nav className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md bg-opacity-80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center">
            <Link to="/" onClick={handleHomeClick} className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-600">
              CryptoAnalyst
            </Link>
          </div>
          <div className="hidden md:flex flex-1 justify-center">
            <div className="flex items-baseline space-x-4">
              {/* Herkese Açık Sayfalar (Public Links) */}
              <Link to="/" onClick={handleHomeClick} className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                Home
              </Link>
              <Link to="/compare" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                Compare
              </Link>
              <Link to="/report" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                Scientific Report
              </Link>
              <Link to="/charts" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                Seaborn Charts
              </Link>

              {/* Korumalı Sayfalar (Protected Links - Sadece giriş yapanlar görebilir) */}
              {isAuthenticated && (
                <>
                  <Link to="/analysis" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                    Technical Analysis
                  </Link>
                  <Link to="/investors" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                    Investor Analysis
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Sağ Kısım: Kullanıcı ve Admin Kontrolleri */}
          <div className="hidden md:flex items-center space-x-4">
            {!isAuthenticated ? (
              <>
                <Link to="/login" className="text-gray-300 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                  Login
                </Link>
                <Link to="/register" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-all shadow-md">
                  Register
                </Link>
              </>
            ) : (
              <>
                {/* Admin Paneli Sadece 'Admin' rolüne görünür (Access Control) */}
                {isAdmin && (
                  <Link to="/admin" className="text-emerald-400 hover:text-white hover:bg-emerald-900/50 border border-emerald-500/30 px-3 py-2 rounded-md text-sm font-medium transition-all">
                    Admin Panel
                  </Link>
                )}
                
                <Link to="/profile" className="text-blue-400 hover:text-white hover:bg-slate-800 px-3 py-2 rounded-md text-sm font-medium transition-all">
                  Profile
                </Link>
                <button 
                  onClick={handleLogout}
                  className="text-red-400 hover:text-white hover:bg-red-900/50 px-3 py-2 rounded-md text-sm font-medium transition-all"
                >
                  Logout
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;