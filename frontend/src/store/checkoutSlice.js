import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { checkoutService } from '../services/checkout';

// Async thunks
export const createOrder = createAsyncThunk(
  'checkout/createOrder',
  async (orderData, { rejectWithValue }) => {
    try {
      const response = await checkoutService.createOrder(orderData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create order');
    }
  }
);

export const fetchShippingMethods = createAsyncThunk(
  'checkout/fetchShippingMethods',
  async (_, { rejectWithValue }) => {
    try {
      const response = await checkoutService.getShippingMethods();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch shipping methods');
    }
  }
);

export const fetchPaymentMethods = createAsyncThunk(
  'checkout/fetchPaymentMethods',
  async (_, { rejectWithValue }) => {
    try {
      const response = await checkoutService.getPaymentMethods();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch payment methods');
    }
  }
);

export const validateCoupon = createAsyncThunk(
  'checkout/validateCoupon',
  async (code, { rejectWithValue }) => {
    try {
      const response = await checkoutService.validateCoupon(code);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Invalid coupon');
    }
  }
);

export const createPaymentIntent = createAsyncThunk(
  'checkout/createPaymentIntent',
  async ({ orderId, amount }, { rejectWithValue }) => {
    try {
      const response = await checkoutService.createPaymentIntent(orderId, amount);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to create payment');
    }
  }
);

const initialState = {
  currentStep: 1,
  shippingAddress: null,
  billingAddress: null,
  shippingMethod: null,
  paymentMethod: null,
  couponCode: null,
  discountAmount: 0,
  orderDetails: null,
  paymentIntent: null,
  shippingMethods: [],
  paymentMethods: [],
  loading: false,
  error: null,
  orderComplete: false,
  orderNumber: null
};

const checkoutSlice = createSlice({
  name: 'checkout',
  initialState,
  reducers: {
    setStep: (state, action) => {
      state.currentStep = action.payload;
    },
    nextStep: (state) => {
      state.currentStep += 1;
    },
    prevStep: (state) => {
      state.currentStep -= 1;
    },
    setShippingAddress: (state, action) => {
      state.shippingAddress = action.payload;
    },
    setBillingAddress: (state, action) => {
      state.billingAddress = action.payload;
    },
    setShippingMethod: (state, action) => {
      state.shippingMethod = action.payload;
    },
    setPaymentMethod: (state, action) => {
      state.paymentMethod = action.payload;
    },
    setCoupon: (state, action) => {
      state.couponCode = action.payload.code;
      state.discountAmount = action.payload.discount;
    },
    clearCoupon: (state) => {
      state.couponCode = null;
      state.discountAmount = 0;
    },
    resetCheckout: () => initialState,
    clearError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Create Order
      .addCase(createOrder.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOrder.fulfilled, (state, action) => {
        state.loading = false;
        state.orderDetails = action.payload;
        state.orderNumber = action.payload.order_number;
        state.orderComplete = true;
      })
      .addCase(createOrder.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })

      // Fetch Shipping Methods
      .addCase(fetchShippingMethods.fulfilled, (state, action) => {
        state.shippingMethods = action.payload;
      })

      // Fetch Payment Methods
      .addCase(fetchPaymentMethods.fulfilled, (state, action) => {
        state.paymentMethods = action.payload;
      })

      // Validate Coupon
      .addCase(validateCoupon.fulfilled, (state, action) => {
        state.couponCode = action.payload.code;
        state.discountAmount = action.payload.discount_amount;
      })

      // Create Payment Intent
      .addCase(createPaymentIntent.fulfilled, (state, action) => {
        state.paymentIntent = action.payload;
      });
  }
});

export const { 
  setStep, nextStep, prevStep,
  setShippingAddress, setBillingAddress,
  setShippingMethod, setPaymentMethod,
  setCoupon, clearCoupon, resetCheckout, clearError 
} = checkoutSlice.actions;

export default checkoutSlice.reducer;