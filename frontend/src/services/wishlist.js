import api from './api';

export const wishlistService = {
  // Get wishlist
  async getWishlist() {
    try {
      const response = await api.get('/auth/wishlist/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Add to wishlist
  async addToWishlist(productId) {
    try {
      const response = await api.post('/auth/wishlist/', { product: productId });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Remove from wishlist
  async removeFromWishlist(productId) {
    try {
      const response = await api.delete(`/auth/wishlist/${productId}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Check if product is in wishlist
  async checkInWishlist(productId) {
    try {
      const response = await api.get(`/auth/wishlist/check/${productId}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default wishlistService;