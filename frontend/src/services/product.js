import api from './api';

export const productService = {
  // Get all products with filters
  async getProducts(params = {}) {
    try {
      const response = await api.get('/products/', { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get single product by slug
  async getProductBySlug(slug) {
    try {
      const response = await api.get(`/products/${slug}/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all categories
  async getCategories() {
    try {
      const response = await api.get('/products/categories/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get products by category
  async getProductsByCategory(categorySlug, params = {}) {
    try {
      const response = await api.get(`/products/categories/${categorySlug}/products/`, { params });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get all brands
  async getBrands() {
    try {
      const response = await api.get('/products/brands/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Search products
  async searchProducts(query) {
    try {
      const response = await api.get('/products/search/', { 
        params: { search: query } 
      });
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get featured products
  async getFeaturedProducts() {
    try {
      const response = await api.get('/products/featured/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get new arrivals
  async getNewArrivals() {
    try {
      const response = await api.get('/products/new-arrivals/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get best sellers
  async getBestSellers() {
    try {
      const response = await api.get('/products/best-sellers/');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Add review
  async addReview(productSlug, reviewData) {
    try {
      const response = await api.post(`/products/${productSlug}/add_review/`, reviewData);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  // Get related products
  async getRelatedProducts(productSlug) {
    try {
      const response = await api.get(`/products/${productSlug}/related_products/`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },
};

// Individual exports
export const getProducts = (params) => productService.getProducts(params);
export const getProductBySlug = (slug) => productService.getProductBySlug(slug);
export const getCategories = () => productService.getCategories();
export const getBrands = () => productService.getBrands();
export const searchProducts = (query) => productService.searchProducts(query);
export const getFeaturedProducts = () => productService.getFeaturedProducts();
export const addReview = (slug, data) => productService.addReview(slug, data);

export default productService;