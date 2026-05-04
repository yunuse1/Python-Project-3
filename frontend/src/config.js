// API Base URL - uses relative path in production, localhost in development
const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:5000';

// JWT Token'ı ve Rolü LocalStorage'dan alan yardımcı fonksiyonlar (Authentication & RBAC)
export const getAuthToken = () => localStorage.getItem('token');
export const getUserRole = () => localStorage.getItem('role');

export default API_BASE;