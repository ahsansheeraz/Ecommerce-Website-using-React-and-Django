import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { productService } from '../services/product';

// Async thunks
export const fetchProducts = createAsyncThunk(
  'products/fetchProducts',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await productService.getProducts(params);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch products');
    }
  }
);

export const fetchProductBySlug = createAsyncThunk(
  'products/fetchProductBySlug',
  async (slug, { rejectWithValue }) => {
    try {
      const response = await productService.getProductBySlug(slug);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch product');
    }
  }
);

export const fetchCategories = createAsyncThunk(
  'products/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getCategories();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch categories');
    }
  }
);

export const fetchFeaturedProducts = createAsyncThunk(
  'products/fetchFeaturedProducts',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getFeaturedProducts();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch featured products');
    }
  }
);

export const fetchNewArrivals = createAsyncThunk(
  'products/fetchNewArrivals',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getNewArrivals();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch new arrivals');
    }
  }
);

export const fetchBestSellers = createAsyncThunk(
  'products/fetchBestSellers',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getBestSellers();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch best sellers');
    }
  }
);

export const addProductReview = createAsyncThunk(
  'products/addReview',
  async ({ slug, reviewData }, { rejectWithValue }) => {
    try {
      const response = await productService.addReview(slug, reviewData);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to add review');
    }
  }
);

// 🔽 NEW: Fetch brands thunk
export const fetchBrands = createAsyncThunk(
  'products/fetchBrands',
  async (_, { rejectWithValue }) => {
    try {
      const response = await productService.getBrands();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch brands');
    }
  }
);

// 🔽 NEW: Fetch products by category thunk (for CategoryPage)
export const fetchProductsByCategory = createAsyncThunk(
  'products/fetchProductsByCategory',
  async (categorySlug, { rejectWithValue }) => {
    try {
      const response = await productService.getProductsByCategory(categorySlug);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch category products');
    }
  }
);

// 🔽 NEW: Fetch related products thunk (for ProductDetailPage)
export const fetchRelatedProducts = createAsyncThunk(
  'products/fetchRelatedProducts',
  async (slug, { rejectWithValue }) => {
    try {
      const response = await productService.getRelatedProducts(slug);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch related products');
    }
  }
);

const initialState = {
  products: [],
  currentProduct: null,
  categories: [],
  brands: [],                // 🔽 NEW: Add brands to initialState
  featuredProducts: [],
  newArrivals: [],
  bestSellers: [],
  relatedProducts: [],       // 🔽 NEW: Add relatedProducts to initialState
  loading: false,
  error: null,
  filters: {
    category: '',
    brand: '',
    minPrice: '',
    maxPrice: '',
    sort: '-created_at',
    page: 1,
  },
  pagination: {
    count: 0,
    next: null,
    previous: null,
  },
};

const productSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    setFilters: (state, action) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = initialState.filters;
    },
    clearCurrentProduct: (state) => {
      state.currentProduct = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch Products
      .addCase(fetchProducts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload.results || action.payload;
        state.pagination = {
          count: action.payload.count || 0,
          next: action.payload.next,
          previous: action.payload.previous,
        };
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Single Product
      .addCase(fetchProductBySlug.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductBySlug.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProduct = action.payload;
      })
      .addCase(fetchProductBySlug.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Categories
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload;
      })

      // 🔽 NEW: Fetch Brands
      .addCase(fetchBrands.fulfilled, (state, action) => {
        state.brands = action.payload;
      })

      // 🔽 NEW: Fetch Products By Category
      .addCase(fetchProductsByCategory.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchProductsByCategory.fulfilled, (state, action) => {
        state.loading = false;
        state.products = action.payload.results || action.payload;
      })
      .addCase(fetchProductsByCategory.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // 🔽 NEW: Fetch Related Products
      .addCase(fetchRelatedProducts.fulfilled, (state, action) => {
        state.relatedProducts = action.payload;
      })

      // Fetch Featured Products
      .addCase(fetchFeaturedProducts.fulfilled, (state, action) => {
        state.featuredProducts = action.payload;
      })

      // Fetch New Arrivals
      .addCase(fetchNewArrivals.fulfilled, (state, action) => {
        state.newArrivals = action.payload;
      })

      // Fetch Best Sellers
      .addCase(fetchBestSellers.fulfilled, (state, action) => {
        state.bestSellers = action.payload;
      })

      // Add Review
      .addCase(addProductReview.fulfilled, (state, action) => {
        if (state.currentProduct) {
          state.currentProduct.reviews = [action.payload, ...(state.currentProduct.reviews || [])];
          state.currentProduct.reviews_count = (state.currentProduct.reviews_count || 0) + 1;
        }
      });
  },
});

export const { setFilters, clearFilters, clearCurrentProduct, clearError } = productSlice.actions;
export default productSlice.reducer;