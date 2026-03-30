import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor - add token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - handle errors
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Token expired error (401)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        if (response.data.access) {
          localStorage.setItem('access_token', response.data.access);
          originalRequest.headers.Authorization = `Bearer ${response.data.access}`;
          return api(originalRequest);
        }
      } catch (refreshError) {
        // Refresh token failed - redirect to login
        localStorage.clear();
        window.location.href = '/login';
        toast.error('Session expired. Please login again.');
      }
    }

    // Show error message
    if (error.response?.data?.message) {
      toast.error(error.response.data.message);
    } else if (error.response?.data?.errors) {
      Object.values(error.response.data.errors).forEach((err) => {
        toast.error(Array.isArray(err) ? err[0] : err);
      });
    } else {
      toast.error('Something went wrong. Please try again.');
    }

    return Promise.reject(error);
  }
);

export default api;