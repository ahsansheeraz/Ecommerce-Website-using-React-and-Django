import React from 'react';
import { Link } from 'react-router-dom';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineCheckCircle, HiOutlineShoppingBag, HiOutlineMail } from 'react-icons/hi';

const OrderConfirmation = () => {
  const { orderDetails, orderNumber } = useSelector((state) => state.checkout);
  const { user } = useSelector((state) => state.auth);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-white rounded-xl shadow-lg p-8 text-center"
    >
      {/* Success Icon */}
      <div className="inline-flex items-center justify-center w-20 h-20 bg-green-100 rounded-full mb-6">
        <HiOutlineCheckCircle className="w-10 h-10 text-green-600" />
      </div>

      {/* Title */}
      <h1 className="text-3xl font-bold text-gray-900 mb-3">
        Thank You for Your Order!
      </h1>
      
      <p className="text-gray-600 mb-6">
        Your order has been placed successfully.
      </p>

      {/* Order Number */}
      <div className="bg-primary-50 p-4 rounded-lg mb-6">
        <p className="text-sm text-gray-600 mb-1">Order Number</p>
        <p className="text-2xl font-bold text-primary-600">#{orderNumber}</p>
      </div>

      {/* Confirmation Email */}
      <div className="flex items-center justify-center space-x-2 text-gray-600 mb-8">
        <HiOutlineMail className="w-5 h-5" />
        <p className="text-sm">
          We've sent a confirmation email to <span className="font-medium">{user?.email}</span>
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Link
          to="/orders"
          className="btn-primary inline-flex items-center justify-center space-x-2"
        >
          <HiOutlineShoppingBag className="w-5 h-5" />
          <span>Track Your Order</span>
        </Link>
        
        <Link
          to="/shop"
          className="btn-secondary inline-flex items-center justify-center space-x-2"
        >
          <span>Continue Shopping</span>
        </Link>
      </div>

      {/* Order Details Link */}
      <p className="text-xs text-gray-500 mt-6">
        Need help? <a href="/contact" className="text-primary-600 hover:underline">Contact Support</a>
      </p>
    </motion.div>
  );
};

export default OrderConfirmation;