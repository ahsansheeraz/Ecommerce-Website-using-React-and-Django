import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { wishlistService } from '../services/wishlist';

// Async thunks
export const fetchWishlist = createAsyncThunk(
  'wishlist/fetchWishlist',
  async (_, { rejectWithValue }) => {
    try {
      const response = await wishlistService.getWishlist();
      return response;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch wishlist');
    }
  }
);

export const addToWishlist = createAsyncThunk(
  'wishlist/addToWishlist',
  async (productId, { rejectWithValue }) => {
    try {
      const response = await wishlistService.addToWishlist(productId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to add to wishlist');
    }
  }
);

export const removeFromWishlist = createAsyncThunk(
  'wishlist/removeFromWishlist',
  async (productId, { rejectWithValue }) => {
    try {
      const response = await wishlistService.removeFromWishlist(productId);
      return { productId, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to remove from wishlist');
    }
  }
);

export const checkInWishlist = createAsyncThunk(
  'wishlist/checkInWishlist',
  async (productId, { rejectWithValue }) => {
    try {
      const response = await wishlistService.checkInWishlist(productId);
      return { productId, inWishlist: response.data.in_wishlist };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to check wishlist');
    }
  }
);

const initialState = {
  items: [],
  wishlistIds: [], // Store just IDs for quick lookup
  loading: false,
  error: null,
  totalItems: 0
};

const wishlistSlice = createSlice({
  name: 'wishlist',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    toggleWishlist: (state, action) => {
      // Optimistic update for UI
      const productId = action.payload;
      const index = state.wishlistIds.indexOf(productId);
      if (index === -1) {
        state.wishlistIds.push(productId);
      } else {
        state.wishlistIds.splice(index, 1);
      }
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Wishlist
      .addCase(fetchWishlist.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchWishlist.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload || [];
        state.wishlistIds = (action.payload || []).map(item => item.product?.id || item.product);
        state.totalItems = state.items.length;
      })
      .addCase(fetchWishlist.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Add to Wishlist
      .addCase(addToWishlist.fulfilled, (state, action) => {
        state.items.push(action.payload);
        state.wishlistIds.push(action.payload.product?.id || action.payload.product);
        state.totalItems = state.items.length;
      })

      // Remove from Wishlist
      .addCase(removeFromWishlist.fulfilled, (state, action) => {
        state.items = state.items.filter(item => 
          (item.product?.id || item.product) !== action.payload.productId
        );
        state.wishlistIds = state.wishlistIds.filter(id => id !== action.payload.productId);
        state.totalItems = state.items.length;
      })

      // Check in Wishlist
      .addCase(checkInWishlist.fulfilled, (state, action) => {
        const { productId, inWishlist } = action.payload;
        if (inWishlist && !state.wishlistIds.includes(productId)) {
          state.wishlistIds.push(productId);
        } else if (!inWishlist && state.wishlistIds.includes(productId)) {
          state.wishlistIds = state.wishlistIds.filter(id => id !== productId);
        }
      });
  }
});

export const { clearError, toggleWishlist } = wishlistSlice.actions;
export default wishlistSlice.reducer;