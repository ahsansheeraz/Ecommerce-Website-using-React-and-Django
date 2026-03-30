import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineArrowLeft } from 'react-icons/hi';
import { fetchCart } from '../store/cartSlice';
import CartItem from '../components/cart/CartItem';
import CartSummary from '../components/cart/CartSummary';
import CartEmpty from '../components/cart/CartEmpty';

const CartPage = () => {
  const dispatch = useDispatch();
  const { items, totalItems, subtotal, totalDiscount, total, appliedCoupons, loading } = 
    useSelector((state) => state.cart);

  useEffect(() => {
    dispatch(fetchCart());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Shopping Cart</h1>
          <p className="text-gray-600 mt-2">
            {totalItems} {totalItems === 1 ? 'item' : 'items'} in your cart
          </p>
        </div>

        {items?.length === 0 ? (
          <CartEmpty />
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Cart Items */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-lg p-6">
                <AnimatePresence mode="popLayout">
                  {items.map((item) => (
                    <CartItem key={item.id} item={item} />
                  ))}
                </AnimatePresence>

                {/* Continue Shopping Link */}
                <div className="mt-6 pt-6 border-t">
                  <Link
                    to="/shop"
                    className="inline-flex items-center text-primary-600 hover:text-primary-700"
                  >
                    <HiOutlineArrowLeft className="w-4 h-4 mr-2" />
                    <span>Continue Shopping</span>
                  </Link>
                </div>
              </div>
            </div>

            {/* Cart Summary */}
            <div className="lg:col-span-1">
              <CartSummary
                subtotal={subtotal}
                totalDiscount={totalDiscount}
                total={total}
                appliedCoupons={appliedCoupons}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CartPage;