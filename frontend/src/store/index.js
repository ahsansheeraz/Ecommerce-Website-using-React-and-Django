import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import userReducer from './userSlice';

import productReducer from './productSlice';
import cartReducer from './cartSlice'; 
import wishlistReducer from './wishlistSlice'; 
import checkoutReducer from './checkoutSlice';  // 🔽 ADD THIS
import orderReducer from './orderSlice'; 
import adminReducer from './adminSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    user: userReducer,
    products: productReducer,
    cart: cartReducer,
    wishlist: wishlistReducer,
    checkout: checkoutReducer,  // 🔽 ADD THIS
    orders: orderReducer, 
    admin: adminReducer,
  },
});