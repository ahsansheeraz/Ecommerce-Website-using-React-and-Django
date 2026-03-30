import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { adminService } from '../services/admin';

// ============================================
// ASYNC THUNKS
// ============================================

// Dashboard
export const fetchDashboardStats = createAsyncThunk(
  'admin/fetchDashboardStats',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminService.getDashboardStats();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch dashboard stats');
    }
  }
);

// Products
export const fetchAdminProducts = createAsyncThunk(
  'admin/fetchAdminProducts',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await adminService.getProducts(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch products');
    }
  }
);

export const createProduct = createAsyncThunk(
  'admin/createProduct',
  async (productData, { rejectWithValue }) => {
    try {
      const response = await adminService.createProduct(productData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create product');
    }
  }
);

export const updateProduct = createAsyncThunk(
  'admin/updateProduct',
  async ({ id, productData }, { rejectWithValue }) => {
    try {
      const response = await adminService.updateProduct(id, productData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update product');
    }
  }
);

export const deleteProduct = createAsyncThunk(
  'admin/deleteProduct',
  async (id, { rejectWithValue }) => {
    try {
      const response = await adminService.deleteProduct(id);
      return { id, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to delete product');
    }
  }
);

// Categories
export const fetchCategories = createAsyncThunk(
  'admin/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminService.getCategories();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch categories');
    }
  }
);

export const createCategory = createAsyncThunk(
  'admin/createCategory',
  async (categoryData, { rejectWithValue }) => {
    try {
      const response = await adminService.createCategory(categoryData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create category');
    }
  }
);

export const updateCategory = createAsyncThunk(
  'admin/updateCategory',
  async ({ id, categoryData }, { rejectWithValue }) => {
    try {
      const response = await adminService.updateCategory(id, categoryData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update category');
    }
  }
);

export const deleteCategory = createAsyncThunk(
  'admin/deleteCategory',
  async (id, { rejectWithValue }) => {
    try {
      const response = await adminService.deleteCategory(id);
      return { id, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to delete category');
    }
  }
);

// Orders
export const fetchAdminOrders = createAsyncThunk(
  'admin/fetchAdminOrders',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await adminService.getOrders(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch orders');
    }
  }
);

export const updateOrderStatus = createAsyncThunk(
  'admin/updateOrderStatus',
  async ({ orderNumber, statusData }, { rejectWithValue }) => {
    try {
      const response = await adminService.updateOrderStatus(orderNumber, statusData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update order status');
    }
  }
);

// Users
export const fetchAdminUsers = createAsyncThunk(
  'admin/fetchAdminUsers',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await adminService.getUsers(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch users');
    }
  }
);

export const updateUserRole = createAsyncThunk(
  'admin/updateUserRole',
  async ({ userId, roleData }, { rejectWithValue }) => {
    try {
      const response = await adminService.updateUserRole(userId, roleData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update user role');
    }
  }
);

// Settings
export const fetchSettings = createAsyncThunk(
  'admin/fetchSettings',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminService.getSettings();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch settings');
    }
  }
);

export const updateSettings = createAsyncThunk(
  'admin/updateSettings',
  async (settingsData, { rejectWithValue }) => {
    try {
      const response = await adminService.updateSettings(settingsData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update settings');
    }
  }
);

// Reports
export const fetchReports = createAsyncThunk(
  'admin/fetchReports',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminService.getReports();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch reports');
    }
  }
);

export const generateReport = createAsyncThunk(
  'admin/generateReport',
  async ({ reportType, params }, { rejectWithValue }) => {
    try {
      const response = await adminService.generateReport(reportType, params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to generate report');
    }
  }
);

// Activity Logs
export const fetchActivityLogs = createAsyncThunk(
  'admin/fetchActivityLogs',
  async (params = {}, { rejectWithValue }) => {
    try {
      const response = await adminService.getActivityLogs(params);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch activity logs');
    }
  }
);

// System Health
export const fetchSystemHealth = createAsyncThunk(
  'admin/fetchSystemHealth',
  async (_, { rejectWithValue }) => {
    try {
      const response = await adminService.getSystemHealth();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch system health');
    }
  }
);

// Maintenance Mode
export const toggleMaintenance = createAsyncThunk(
  'admin/toggleMaintenance',
  async (maintenanceData, { rejectWithValue }) => {
    try {
      const response = await adminService.toggleMaintenance(maintenanceData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to toggle maintenance');
    }
  }
);

// GLOBAL SEARCH
export const globalSearch = createAsyncThunk(
  'admin/globalSearch',
  async (query, { rejectWithValue }) => {
    try {
      const response = await adminService.globalSearch(query);
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to search');
    }
  }
);

// ============================================
// INITIAL STATE
// ============================================
const initialState = {
  // Dashboard
  stats: {
    totalUsers: 0,
    newUsersToday: 0,
    totalOrders: 0,
    ordersToday: 0,
    totalRevenue: 0,
    revenueToday: 0,
    totalProducts: 0,
    lowStockProducts: 0
  },
  
  // Data tables
  products: [],
  orders: [],
  users: [],
  categories: [],
  reports: [],
  activityLogs: [],
  settings: [],
  systemHealth: [],
  
  // UI State
  loading: false,
  error: null,
  sidebarOpen: true,
  currentView: 'dashboard',
  
  // Pagination
  pagination: {
    products: { count: 0, next: null, previous: null },
    orders: { count: 0, next: null, previous: null },
    users: { count: 0, next: null, previous: null }
  },
  
  // Filters
  filters: {
    products: { page: 1, search: '', status: '' },
    orders: { page: 1, search: '', status: '' },
    users: { page: 1, search: '', role: '' }
  },
  
  // Search
  searchResults: [],
  searchQuery: ''
};

// ============================================
// SLICE
// ============================================
const adminSlice = createSlice({
  name: 'admin',
  initialState,
  reducers: {
    // UI Actions
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    
    setCurrentView: (state, action) => {
      state.currentView = action.payload;
    },
    
    // Filter Actions
    setProductFilters: (state, action) => {
      state.filters.products = { ...state.filters.products, ...action.payload };
    },
    
    setOrderFilters: (state, action) => {
      state.filters.orders = { ...state.filters.orders, ...action.payload };
    },
    
    setUserFilters: (state, action) => {
      state.filters.users = { ...state.filters.users, ...action.payload };
    },
    
    // Utility Actions
    clearError: (state) => {
      state.error = null;
    },
    
    // Clear Search
    clearSearch: (state) => {
      state.searchResults = [];
      state.searchQuery = '';
    }
  },
  extraReducers: (builder) => {
    builder
      // ========================================
      // Dashboard Stats
      // ========================================
      .addCase(fetchDashboardStats.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchDashboardStats.fulfilled, (state, action) => {
        state.loading = false;
        state.stats = action.payload;
      })
      .addCase(fetchDashboardStats.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // ========================================
      // Products - FIXED with safety checks
      // ========================================
      .addCase(fetchAdminProducts.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAdminProducts.fulfilled, (state, action) => {
        state.loading = false;
        // ✅ FIX: Safety check for undefined payload
        if (action.payload) {
          if (action.payload.results) {
            state.products = action.payload.results;
            state.pagination.products = {
              count: action.payload.count || 0,
              next: action.payload.next,
              previous: action.payload.previous
            };
          } else if (Array.isArray(action.payload)) {
            state.products = action.payload;
            state.pagination.products = {
              count: action.payload.length,
              next: null,
              previous: null
            };
          } else {
            state.products = [action.payload];
            state.pagination.products = {
              count: 1,
              next: null,
              previous: null
            };
          }
        } else {
          state.products = [];
          state.pagination.products = {
            count: 0,
            next: null,
            previous: null
          };
        }
      })
      .addCase(fetchAdminProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // ✅ FIX: createProduct with safety
      .addCase(createProduct.pending, (state) => {
        state.loading = true;
      })
      .addCase(createProduct.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload) {
          state.products = [action.payload, ...(state.products || [])];
          if (state.pagination.products) {
            state.pagination.products.count = (state.pagination.products.count || 0) + 1;
          }
        }
      })
      .addCase(createProduct.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(updateProduct.fulfilled, (state, action) => {
        if (action.payload) {
          const index = state.products.findIndex(p => p.id === action.payload.id);
          if (index !== -1) {
            state.products[index] = action.payload;
          }
        }
      })

      .addCase(deleteProduct.fulfilled, (state, action) => {
        if (action.payload) {
          state.products = state.products.filter(p => p.id !== action.payload.id);
          if (state.pagination.products) {
            state.pagination.products.count = Math.max(0, (state.pagination.products.count || 0) - 1);
          }
        }
      })

      // ========================================
      // Categories - FIXED
      // ========================================
      .addCase(fetchCategories.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.loading = false;
        state.categories = action.payload || [];
      })
      .addCase(fetchCategories.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(createCategory.fulfilled, (state, action) => {
        if (action.payload) {
          state.categories = [action.payload, ...(state.categories || [])];
        }
      })

      .addCase(updateCategory.fulfilled, (state, action) => {
        if (action.payload) {
          const index = (state.categories || []).findIndex(c => c.id === action.payload.id);
          if (index !== -1) {
            state.categories[index] = action.payload;
          }
        }
      })

      .addCase(deleteCategory.fulfilled, (state, action) => {
        if (action.payload) {
          state.categories = (state.categories || []).filter(c => c.id !== action.payload.id);
        }
      })

      // ========================================
      // Orders
      // ========================================
      .addCase(fetchAdminOrders.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAdminOrders.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload) {
          state.orders = action.payload.results || action.payload;
          state.pagination.orders = {
            count: action.payload.count || 0,
            next: action.payload.next,
            previous: action.payload.previous
          };
        } else {
          state.orders = [];
        }
      })
      .addCase(fetchAdminOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(updateOrderStatus.fulfilled, (state, action) => {
        if (action.payload) {
          const index = state.orders.findIndex(o => o.order_number === action.payload.order_number);
          if (index !== -1) {
            state.orders[index] = { ...state.orders[index], ...action.payload };
          }
        }
      })

      // ========================================
      // Users
      // ========================================
      .addCase(fetchAdminUsers.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchAdminUsers.fulfilled, (state, action) => {
        state.loading = false;
        if (action.payload) {
          state.users = action.payload.results || action.payload;
          state.pagination.users = {
            count: action.payload.count || 0,
            next: action.payload.next,
            previous: action.payload.previous
          };
        } else {
          state.users = [];
        }
      })
      .addCase(fetchAdminUsers.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      .addCase(updateUserRole.fulfilled, (state, action) => {
        if (action.payload) {
          const index = state.users.findIndex(u => u.id === action.payload.id);
          if (index !== -1) {
            state.users[index] = action.payload;
          }
        }
      })

      // ========================================
      // Settings
      // ========================================
      .addCase(fetchSettings.fulfilled, (state, action) => {
        state.settings = action.payload || [];
      })

      // ========================================
      // Reports
      // ========================================
      .addCase(fetchReports.fulfilled, (state, action) => {
        state.reports = action.payload || [];
      })

      // ========================================
      // Activity Logs
      // ========================================
      .addCase(fetchActivityLogs.fulfilled, (state, action) => {
        state.activityLogs = action.payload || [];
      })

      // ========================================
      // System Health
      // ========================================
      .addCase(fetchSystemHealth.fulfilled, (state, action) => {
        state.systemHealth = action.payload || [];
      })

      // ========================================
      // Global Search
      // ========================================
      .addCase(globalSearch.pending, (state) => {
        state.loading = true;
      })
      .addCase(globalSearch.fulfilled, (state, action) => {
        state.loading = false;
        state.searchResults = action.payload || [];
        state.searchQuery = action.meta.arg;
      })
      .addCase(globalSearch.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  }
});

// ============================================
// EXPORTS
// ============================================
export const { 
  toggleSidebar, 
  setCurrentView, 
  setProductFilters,
  setOrderFilters,
  setUserFilters,
  clearError,
  clearSearch
} = adminSlice.actions;

export default adminSlice.reducer;