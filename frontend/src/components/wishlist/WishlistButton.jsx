import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { HiOutlineHeart, HiHeart } from 'react-icons/hi';
import { addToWishlist, removeFromWishlist, checkInWishlist, toggleWishlist } from '../../store/wishlistSlice';
import toast from 'react-hot-toast';

const WishlistButton = ({ productId, className = '', showText = false }) => {
  const dispatch = useDispatch();
  const { isAuthenticated } = useSelector((state) => state.auth);
  const { wishlistIds } = useSelector((state) => state.wishlist);
  const [loading, setLoading] = useState(false);
  const [isInWishlist, setIsInWishlist] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      setIsInWishlist(wishlistIds.includes(productId));
    }
  }, [isAuthenticated, wishlistIds, productId]);

  useEffect(() => {
    if (isAuthenticated && productId) {
      dispatch(checkInWishlist(productId));
    }
  }, [dispatch, isAuthenticated, productId]);

  const handleToggleWishlist = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      toast.error('Please login to add items to wishlist');
      return;
    }

    setLoading(true);
    
    // Optimistic update
    dispatch(toggleWishlist(productId));
    
    try {
      if (isInWishlist) {
        await dispatch(removeFromWishlist(productId)).unwrap();
        toast.success('Removed from wishlist');
      } else {
        await dispatch(addToWishlist(productId)).unwrap();
        toast.success('Added to wishlist');
      }
    } catch (error) {
      // Revert on error
      dispatch(toggleWishlist(productId));
      toast.error('Failed to update wishlist');
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <button
        onClick={handleToggleWishlist}
        className={`${className} text-gray-400 hover:text-pink-500 transition-colors`}
        title="Login to add to wishlist"
      >
        <HiOutlineHeart className="w-5 h-5" />
        {showText && <span className="ml-2">Add to Wishlist</span>}
      </button>
    );
  }

  return (
    <button
      onClick={handleToggleWishlist}
      disabled={loading}
      className={`${className} transition-colors ${
        isInWishlist ? 'text-pink-500' : 'text-gray-400 hover:text-pink-500'
      } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
      title={isInWishlist ? 'Remove from wishlist' : 'Add to wishlist'}
    >
      {loading ? (
        <div className="w-5 h-5 border-2 border-pink-500 border-t-transparent rounded-full animate-spin"></div>
      ) : isInWishlist ? (
        <HiHeart className="w-5 h-5" />
      ) : (
        <HiOutlineHeart className="w-5 h-5" />
      )}
      {showText && <span className="ml-2">{isInWishlist ? 'Remove from Wishlist' : 'Add to Wishlist'}</span>}
    </button>
  );
};

export default WishlistButton;