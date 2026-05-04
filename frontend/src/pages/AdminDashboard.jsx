import { useState, useEffect } from 'react';
import API_BASE from '../config';

function AdminDashboard() {
  const [adminData, setAdminData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchAdminData = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/api/admin/dashboard`, {
          // Token'ı başlığa ekliyoruz (Access Control)
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (response.ok) {
          setAdminData(data);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError('Failed to fetch admin data.');
      }
    };
    fetchAdminData();
  }, []);

  if (error) return <div className="text-center mt-20 text-red-500 text-xl font-bold bg-red-900/20 p-4 rounded-lg inline-block">{error}</div>;
  if (!adminData) return <div className="text-center mt-20 text-white text-xl">Loading Admin Panel...</div>;

  return (
    <div className="max-w-6xl mx-auto mt-10 p-6">
      <div className="bg-emerald-900/30 border border-emerald-500/50 p-6 rounded-xl shadow-lg mb-8">
        <h1 className="text-3xl font-bold text-emerald-400 mb-2">Admin Dashboard</h1>
        <p className="text-gray-300">Welcome, Admin. System overview and user management.</p>
        <div className="mt-4 inline-block bg-slate-900 px-4 py-2 rounded-lg border border-slate-700">
          <span className="text-gray-400">Total Registered Users: </span>
          <span className="text-white font-bold text-xl ml-2">{adminData.total_users}</span>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl shadow-lg border border-slate-700 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-700 bg-slate-850">
          <h2 className="text-xl font-bold text-white">System Users List</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="text-xs text-gray-300 uppercase bg-slate-900/50">
              <tr>
                <th className="px-6 py-3">Username</th>
                <th className="px-6 py-3">Role</th>
                <th className="px-6 py-3">Wallet Balance</th>
                <th className="px-6 py-3">Trades Count</th>
              </tr>
            </thead>
            <tbody>
              {adminData.users_data.map((user, index) => (
                <tr key={index} className="border-b border-slate-700 hover:bg-slate-750 transition-colors">
                  <td className="px-6 py-4 font-medium text-white">{user.username}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-bold ${user.role === 'Admin' ? 'bg-emerald-900/50 text-emerald-400 border border-emerald-500/30' : 'bg-blue-900/50 text-blue-400 border border-blue-500/30'}`}>
                      {user.role}
                    </span>
                  </td>
                  <td className="px-6 py-4">${user.wallet_balance.toFixed(2)}</td>
                  <td className="px-6 py-4">{user.trades?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default AdminDashboard;