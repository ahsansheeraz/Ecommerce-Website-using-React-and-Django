import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineHeart } from 'react-icons/hi';

const WishlistEmpty = () => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="text-center py-20"
    >
      <div className="inline-block p-6 bg-pink-100 rounded-full mb-6">
        <HiOutlineHeart className="w-16 h-16 text-pink-500" />
      </div>
      
      <h2 className="text-2xl font-bold text-gray-900 mb-3">
        Your wishlist is empty
      </h2>
      
      <p className="text-gray-600 mb-8 max-w-md mx-auto">
        Save items you love to your wishlist and they'll appear here. 
        Start exploring our products!
      </p>

      <Link
        to="/shop"
        className="btn-primary inline-flex items-center space-x-2"
      >
        <span>Browse Products</span>
      </Link>
    </motion.div>
  );
};

export default WishlistEmpty;