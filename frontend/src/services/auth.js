import api from './api';

export const authService = {
  // Register user
  async register(userData) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  // Login user
  async login(credentials) {
    const response = await api.post('/auth/login/', credentials);
    if (response.data.data) {
      localStorage.setItem('access_token', response.data.data.access_token);
      localStorage.setItem('refresh_token', response.data.data.refresh_token);
      localStorage.setItem('user', JSON.stringify(response.data.data.user));
    }
    return response.data;
  },

  // Logout
  async logout() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (refreshToken) {
      await api.post('/auth/logout/', { refresh_token: refreshToken });
    }
    localStorage.clear();
  },

  // Get current user
  getCurrentUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  // Check if authenticated
  isAuthenticated() {
    return !!localStorage.getItem('access_token');
  },
};