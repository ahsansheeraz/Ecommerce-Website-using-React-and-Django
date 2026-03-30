import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { cartService } from '../services/cart';

// Async thunks
export const fetchCart = createAsyncThunk(
  'cart/fetchCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartService.getCart();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch cart');
    }
  }
);

export const addToCart = createAsyncThunk(
  'cart/addToCart',
  async ({ productId, quantity, variantId }, { rejectWithValue }) => {
    try {
      const response = await cartService.addToCart(productId, quantity, variantId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to add to cart');
    }
  }
);

export const updateCartItem = createAsyncThunk(
  'cart/updateCartItem',
  async ({ itemId, quantity }, { rejectWithValue }) => {
    try {
      const response = await cartService.updateCartItem(itemId, quantity);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update cart');
    }
  }
);

export const removeFromCart = createAsyncThunk(
  'cart/removeFromCart',
  async (itemId, { rejectWithValue }) => {
    try {
      const response = await cartService.removeFromCart(itemId);
      return { itemId, ...response.data };
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to remove from cart');
    }
  }
);

export const clearCart = createAsyncThunk(
  'cart/clearCart',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartService.clearCart();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to clear cart');
    }
  }
);

export const applyCoupon = createAsyncThunk(
  'cart/applyCoupon',
  async (code, { rejectWithValue }) => {
    try {
      const response = await cartService.applyCoupon(code);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to apply coupon');
    }
  }
);

export const removeCoupon = createAsyncThunk(
  'cart/removeCoupon',
  async (_, { rejectWithValue }) => {
    try {
      const response = await cartService.removeCoupon();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to remove coupon');
    }
  }
);

const initialState = {
  items: [],
  cartId: null,
  totalItems: 0,
  subtotal: 0,
  totalDiscount: 0,
  total: 0,
  appliedCoupons: [],
  loading: false,
  error: null,
  isOpen: false // for mini cart drawer
};

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    openCart: (state) => {
      state.isOpen = true;
    },
    closeCart: (state) => {
      state.isOpen = false;
    },
    toggleCart: (state) => {
      state.isOpen = !state.isOpen;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Cart
      .addCase(fetchCart.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCart.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items || [];
        state.cartId = action.payload.id;
        state.totalItems = action.payload.total_items || 0;
        state.subtotal = action.payload.subtotal || 0;
        state.totalDiscount = action.payload.total_discount || 0;
        state.total = action.payload.total || 0;
        state.appliedCoupons = action.payload.applied_coupons || [];
      })
      .addCase(fetchCart.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Add to Cart
      .addCase(addToCart.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(addToCart.fulfilled, (state, action) => {
        state.loading = false;
        state.items = action.payload.items || state.items;
        state.totalItems = action.payload.total_items || state.totalItems;
        state.subtotal = action.payload.subtotal || state.subtotal;
        state.total = action.payload.total || state.total;
        state.isOpen = true; // Open mini cart when item added
      })
      .addCase(addToCart.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Update Cart Item
      .addCase(updateCartItem.fulfilled, (state, action) => {
        state.items = action.payload.items || state.items;
        state.totalItems = action.payload.total_items || state.totalItems;
        state.subtotal = action.payload.subtotal || state.subtotal;
        state.total = action.payload.total || state.total;
      })

      // Remove from Cart
      .addCase(removeFromCart.fulfilled, (state, action) => {
        state.items = state.items.filter(item => item.id !== action.payload.itemId);
        state.totalItems = state.totalItems - 1;
        // You might want to recalculate totals from API response
        if (action.payload.subtotal) {
          state.subtotal = action.payload.subtotal;
          state.total = action.payload.total;
        }
      })

      // Clear Cart
      .addCase(clearCart.fulfilled, (state) => {
        state.items = [];
        state.totalItems = 0;
        state.subtotal = 0;
        state.totalDiscount = 0;
        state.total = 0;
        state.appliedCoupons = [];
      })

      // Apply Coupon
      .addCase(applyCoupon.fulfilled, (state, action) => {
        state.appliedCoupons = [...state.appliedCoupons, action.payload];
        // Recalculate totals
        if (action.payload.discount_amount) {
          state.totalDiscount += action.payload.discount_amount;
          state.total = state.subtotal - state.totalDiscount;
        }
      })

      // Remove Coupon
      .addCase(removeCoupon.fulfilled, (state) => {
        state.appliedCoupons = [];
        state.totalDiscount = 0;
        state.total = state.subtotal;
      });
  }
});

export const { openCart, closeCart, toggleCart, clearError } = cartSlice.actions;
export default cartSlice.reducer;