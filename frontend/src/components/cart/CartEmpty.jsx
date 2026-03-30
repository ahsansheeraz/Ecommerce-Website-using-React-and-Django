import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineShoppingCart } from 'react-icons/hi';

const CartEmpty = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-20"
    >
      <div className="inline-block p-6 bg-gray-100 rounded-full mb-6">
        <HiOutlineShoppingCart className="w-16 h-16 text-gray-400" />
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-3">
        Your cart is empty
      </h2>
      
      <p className="text-gray-600 mb-8 max-w-md mx-auto">
        Looks like you haven't added anything to your cart yet. 
        Start shopping to fill it up!
      </p>

      <Link
        to="/shop"
        className="btn-primary inline-flex items-center space-x-2"
      >
        <span>Continue Shopping</span>
      </Link>
    </motion.div>
  );
};

export default CartEmpty;