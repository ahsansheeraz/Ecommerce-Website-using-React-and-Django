import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { userService } from '../services/user';

export const fetchProfile = createAsyncThunk(
  'user/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await userService.getProfile();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch profile');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'user/updateProfile',
  async (profileData, { rejectWithValue }) => {
    try {
      const response = await userService.updateProfile(profileData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to update profile');
    }
  }
);

export const fetchAddresses = createAsyncThunk(
  'user/fetchAddresses',
  async (_, { rejectWithValue }) => {
    try {
      const response = await userService.getAddresses();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to fetch addresses');
    }
  }
);

export const addAddress = createAsyncThunk(
  'user/addAddress',
  async (addressData, { rejectWithValue }) => {
    try {
      const response = await userService.addAddress(addressData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to add address');
    }
  }
);

export const deleteAddress = createAsyncThunk(
  'user/deleteAddress',
  async (id, { rejectWithValue }) => {
    try {
      await userService.deleteAddress(id);
      return id;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Failed to delete address');
    }
  }
);

const initialState = {
  profile: null,
  addresses: [],
  wishlist: [],
  loading: false,
  error: null,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch profile
      .addCase(fetchProfile.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload?.message;
      })
      // Update profile
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.profile = { ...state.profile, ...action.payload };
      })
      // Fetch addresses
      .addCase(fetchAddresses.fulfilled, (state, action) => {
        state.addresses = action.payload;
      })
      // Add address
      .addCase(addAddress.fulfilled, (state, action) => {
        state.addresses.push(action.payload);
      })
      // Delete address
      .addCase(deleteAddress.fulfilled, (state, action) => {
        state.addresses = state.addresses.filter(addr => addr.id !== action.payload);
      });
  },
});

export const { clearError } = userSlice.actions;
export default userSlice.reducer;