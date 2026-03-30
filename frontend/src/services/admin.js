// Change this line:
// import api from '../api';  // ❌ Wrong

// To this:
import api from './api';  // ✅ Correct - same directory mein hai

export const adminService = {
  // Dashboard
  async getDashboardStats() {
    try {
      const response = await api.get('/admin/dashboard/summary/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Products Management
  async getProducts(params = {}) {
    try {
      const response = await api.get('/products/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createProduct(productData) {
    try {
      const response = await api.post('/products/', productData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateProduct(id, productData) {
    try {
      const response = await api.put(`/products/${id}/`, productData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deleteProduct(id) {
    try {
      const response = await api.delete(`/products/${id}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Categories Management
  async getCategories() {
    try {
      const response = await api.get('/products/categories/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async createCategory(categoryData) {
    try {
      const response = await api.post('/products/categories/', categoryData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateCategory(id, categoryData) {
    try {
      const response = await api.put(`/products/categories/${id}/`, categoryData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async deleteCategory(id) {
    try {
      const response = await api.delete(`/products/categories/${id}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Orders Management
  async getOrders(params = {}) {
    try {
      const response = await api.get('/orders/admin/orders/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateOrderStatus(orderNumber, statusData) {
    try {
      const response = await api.post(`/orders/admin/status/${orderNumber}/`, statusData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Users Management
  async getUsers(params = {}) {
    try {
      const response = await api.get('/users/admin/users/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateUserRole(userId, roleData) {
    try {
      const response = await api.post(`/users/admin/users/${userId}/update-role/`, roleData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Settings
  async getSettings() {
    try {
      const response = await api.get('/admin/settings/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async updateSettings(settingsData) {
    try {
      const response = await api.post('/admin/settings/bulk_update/', { settings: settingsData });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Reports
  async generateReport(reportType, params = {}) {
    try {
      const response = await api.post(`/admin/reports/${reportType}/generate/`, params);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  async getReports() {
    try {
      const response = await api.get('/admin/report-templates/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Activity Logs
  async getActivityLogs(params = {}) {
    try {
      const response = await api.get('/admin/logs/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // System Health
  async getSystemHealth() {
    try {
      const response = await api.get('/admin/health/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Maintenance Mode
  async toggleMaintenance(maintenanceData) {
    try {
      const response = await api.post('/admin/maintenance/', maintenanceData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search
  async globalSearch(query) {
    try {
      const response = await api.get(`/admin/search/?q=${query}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default adminService;