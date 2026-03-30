import api from './api';

export const cartService = {
  // Get cart
  async getCart() {
    try {
      const response = await api.get('/cart/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Add item to cart
  async addToCart(productId, quantity = 1, variantId = null) {
    try {
      const response = await api.post('/cart/items/add/', {
        product: productId,
        quantity,
        variant: variantId
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update cart item quantity
  async updateCartItem(itemId, quantity) {
    try {
      const response = await api.put(`/cart/items/${itemId}/`, { quantity });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Remove item from cart
  async removeFromCart(itemId) {
    try {
      const response = await api.delete(`/cart/items/${itemId}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Clear cart
  async clearCart() {
    try {
      const response = await api.delete('/cart/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get cart summary
  async getCartSummary() {
    try {
      const response = await api.get('/cart/summary/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Apply coupon
  async applyCoupon(code) {
    try {
      const response = await api.post('/cart/coupons/apply/', { code });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Remove coupon
  async removeCoupon() {
    try {
      const response = await api.delete('/cart/coupons/remove/');
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default cartService;