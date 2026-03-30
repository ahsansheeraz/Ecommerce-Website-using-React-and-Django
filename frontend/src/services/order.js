import api from './api';

export const orderService = {
  // Get all orders
  async getOrders(params = {}) {
    try {
      const response = await api.get('/orders/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get order by number
  async getOrderByNumber(orderNumber) {
    try {
      const response = await api.get(`/orders/${orderNumber}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Cancel order
  async cancelOrder(orderNumber, reason) {
    try {
      const response = await api.post(`/orders/${orderNumber}/cancel/`, { reason });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Return order
  async returnOrder(orderNumber, returnData) {
    try {
      const response = await api.post(`/orders/${orderNumber}/return/`, returnData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Track order
  async trackOrder(orderNumber) {
    try {
      const response = await api.get(`/orders/${orderNumber}/track/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default orderService;