import api from './api';

export const userService = {
  // Get profile
  async getProfile() {
    try {
      const response = await api.get('/auth/profile/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update profile
  async updateProfile(profileData) {
    try {
      const response = await api.put('/auth/profile/', profileData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Change password
  async changePassword(passwordData) {
    try {
      const response = await api.post('/auth/change-password/', passwordData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get addresses
  async getAddresses() {
    try {
      const response = await api.get('/auth/addresses/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Add address
  async addAddress(addressData) {
    try {
      const response = await api.post('/auth/addresses/', addressData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Update address
  async updateAddress(id, addressData) {
    try {
      const response = await api.put(`/auth/addresses/${id}/`, addressData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Delete address
  async deleteAddress(id) {
    try {
      const response = await api.delete(`/auth/addresses/${id}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

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
};

// Also export individual functions for convenience
export const getProfile = (data) => userService.getProfile(data);
export const updateProfile = (data) => userService.updateProfile(data);
export const changePassword = (data) => userService.changePassword(data);
export const getAddresses = () => userService.getAddresses();
export const addAddress = (data) => userService.addAddress(data);
export const updateAddress = (id, data) => userService.updateAddress(id, data);
export const deleteAddress = (id) => userService.deleteAddress(id);
export const getWishlist = () => userService.getWishlist();
export const addToWishlist = (productId) => userService.addToWishlist(productId);
export const removeFromWishlist = (productId) => userService.removeFromWishlist(productId);

// Default export
export default userService;