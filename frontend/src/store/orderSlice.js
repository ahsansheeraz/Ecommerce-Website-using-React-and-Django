import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { orderService } from '../services/order';

// Async thunks
export const fetchOrders = createAsyncThunk(
  'orders/fetchOrders',
  async (_, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrders();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch orders');
    }
  }
);

export const fetchOrderByNumber = createAsyncThunk(
  'orders/fetchOrderByNumber',
  async (orderNumber, { rejectWithValue }) => {
    try {
      const response = await orderService.getOrderByNumber(orderNumber);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch order');
    }
  }
);

export const cancelOrder = createAsyncThunk(
  'orders/cancelOrder',
  async (orderNumber, { rejectWithValue }) => {
    try {
      const response = await orderService.cancelOrder(orderNumber);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to cancel order');
    }
  }
);

export const returnOrder = createAsyncThunk(
  'orders/returnOrder',
  async ({ orderNumber, returnData }, { rejectWithValue }) => {
    try {
      const response = await orderService.returnOrder(orderNumber, returnData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to return order');
    }
  }
);

const initialState = {
  orders: [],
  currentOrder: null,
  loading: false,
  error: null,
  pagination: {
    count: 0,
    next: null,
    previous: null,
  }
};

const orderSlice = createSlice({
  name: 'orders',
  initialState,
  reducers: {
    clearCurrentOrder: (state) => {
      state.currentOrder = null;
    },
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch Orders
      .addCase(fetchOrders.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrders.fulfilled, (state, action) => {
        state.loading = false;
        state.orders = action.payload.results || action.payload;
        state.pagination = {
          count: action.payload.count || 0,
          next: action.payload.next,
          previous: action.payload.previous,
        };
      })
      .addCase(fetchOrders.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Order by Number
      .addCase(fetchOrderByNumber.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOrderByNumber.fulfilled, (state, action) => {
        state.loading = false;
        state.currentOrder = action.payload;
      })
      .addCase(fetchOrderByNumber.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Cancel Order
      .addCase(cancelOrder.fulfilled, (state, action) => {
        if (state.currentOrder && state.currentOrder.order_number === action.payload.order_number) {
          state.currentOrder.status = 'cancelled';
        }
        const index = state.orders.findIndex(o => o.order_number === action.payload.order_number);
        if (index !== -1) {
          state.orders[index].status = 'cancelled';
        }
      })

      // Return Order
      .addCase(returnOrder.fulfilled, (state, action) => {
        // Handle return logic
      });
  }
});

export const { clearCurrentOrder, clearError } = orderSlice.actions;
export default orderSlice.reducer;