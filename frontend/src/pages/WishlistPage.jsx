import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineArrowLeft, HiOutlineHeart } from 'react-icons/hi';
import { fetchWishlist } from '../store/wishlistSlice';
import WishlistItem from '../components/wishlist/WishlistItem';
import WishlistEmpty from '../components/wishlist/WishlistEmpty';

const WishlistPage = () => {
  const dispatch = useDispatch();
  const { items, loading, totalItems } = useSelector((state) => state.wishlist);

  useEffect(() => {
    dispatch(fetchWishlist());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-pink-200 border-t-pink-500 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
            <HiOutlineHeart className="w-6 h-6 text-pink-500 animate-pulse" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Wishlist</h1>
              <p className="text-gray-600 mt-2">
                {totalItems} {totalItems === 1 ? 'item' : 'items'} saved
              </p>
            </div>
            
            {/* Share Wishlist Button */}
            {totalItems > 0 && (
              <button className="btn-secondary flex items-center space-x-2">
                <span>Share Wishlist</span>
              </button>
            )}
          </div>
        </div>

        {items?.length === 0 ? (
          <WishlistEmpty />
        ) : (
          <>
            {/* Wishlist Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              <AnimatePresence mode="popLayout">
                {items.map((item) => (
                  <WishlistItem key={item.id} item={item} />
                ))}
              </AnimatePresence>
            </div>

            {/* Continue Shopping Link */}
            <div className="mt-8 text-center">
              <Link
                to="/shop"
                className="inline-flex items-center text-primary-600 hover:text-primary-700"
              >
                <HiOutlineArrowLeft className="w-4 h-4 mr-2" />
                <span>Continue Shopping</span>
              </Link>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default WishlistPage;