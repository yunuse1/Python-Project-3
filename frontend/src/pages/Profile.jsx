import { useState, useEffect } from 'react';
import API_BASE from '../config';

function Profile() {
  const [userData, setUserData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_BASE}/api/user/profile`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (response.ok) {
          setUserData(data);
        } else {
          setError(data.error);
        }
      } catch (err) {
        setError('Failed to fetch profile data.');
      }
    };
    fetchProfile();
  }, []);

  if (error) return <div className="text-center mt-20 text-red-500 text-xl">{error}</div>;
  if (!userData) return <div className="text-center mt-20 text-white text-xl">Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto mt-10 p-6 bg-slate-800 rounded-xl shadow-lg border border-slate-700">
      <h1 className="text-3xl font-bold text-white mb-6 border-b border-slate-700 pb-4">User Profile</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-900 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold text-blue-400 mb-4">Account Details</h2>
          <p className="text-gray-300 mb-2"><span className="font-bold text-white">Username:</span> {userData.username}</p>
          <p className="text-gray-300 mb-2"><span className="font-bold text-white">Role:</span> {userData.role}</p>
          <p className="text-gray-300"><span className="font-bold text-white">Wallet Balance:</span> ${userData.wallet_balance.toFixed(2)}</p>
        </div>

        <div className="bg-slate-900 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold text-emerald-400 mb-4">Security (Encryption)</h2>
          <p className="text-gray-400 text-sm mb-4">This sensitive note is encrypted in the database and decrypted only when you log in.</p>
          <div className="bg-black/50 p-4 rounded border border-emerald-900/50">
            <p className="text-emerald-300 font-mono text-sm break-all">
              {userData.decrypted_wallet_note || "No secret note stored."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Profile;