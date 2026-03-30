import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineTrash, 
  HiOutlineShoppingCart,
  HiOutlineStar,
  HiOutlineHeart 
} from 'react-icons/hi';
import { removeFromWishlist } from '../../store/wishlistSlice';
import { addToCart } from '../../store/cartSlice';
import toast from 'react-hot-toast';

const WishlistItem = ({ item }) => {
  const dispatch = useDispatch();
  const [removing, setRemoving] = useState(false);
  const [addingToCart, setAddingToCart] = useState(false);

  // Handle different response structures
  const product = item.product_details || item.product || {};
  const productId = product.id || item.product;

  const {
    name,
    slug,
    primary_image,
    current_price,
    regular_price,
    sale_price,
    discount_percentage,
    average_rating,
    in_stock
  } = product;

  const handleRemove = async () => {
    setRemoving(true);
    try {
      await dispatch(removeFromWishlist(productId)).unwrap();
      toast.success('Removed from wishlist');
    } catch (error) {
      toast.error('Failed to remove');
    } finally {
      setRemoving(false);
    }
  };

  const handleAddToCart = async () => {
    setAddingToCart(true);
    try {
      await dispatch(addToCart({ productId, quantity: 1 })).unwrap();
      toast.success('Added to cart!');
    } catch (error) {
      toast.error('Failed to add to cart');
    } finally {
      setAddingToCart(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all overflow-hidden group"
    >
      <div className="relative">
        {/* Image */}
        <Link to={`/product/${slug}`} className="block aspect-square bg-gray-100">
          {primary_image ? (
            <img
              src={primary_image}
              alt={name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              <HiOutlineHeart className="w-12 h-12" />
            </div>
          )}
        </Link>

        {/* Discount Badge */}
        {discount_percentage > 0 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
            -{discount_percentage}%
          </div>
        )}

        {/* Remove Button */}
        <button
          onClick={handleRemove}
          disabled={removing}
          className="absolute top-2 right-2 bg-white p-2 rounded-full shadow-lg hover:bg-red-50 transition-colors"
        >
          {removing ? (
            <div className="w-4 h-4 border-2 border-red-500 border-t-transparent rounded-full animate-spin"></div>
          ) : (
            <HiOutlineTrash className="w-4 h-4 text-red-500" />
          )}
        </button>

        {/* Out of Stock Overlay */}
        {!in_stock && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="bg-red-500 text-white px-3 py-1 rounded-lg text-sm font-semibold transform -rotate-12">
              Out of Stock
            </span>
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="p-4">
        <Link to={`/product/${slug}`}>
          <h3 className="font-semibold text-gray-800 hover:text-primary-600 transition-colors line-clamp-2 mb-2">
            {name}
          </h3>
        </Link>

        {/* Rating */}
        <div className="flex items-center mb-2">
          <div className="flex items-center text-yellow-400">
            {[...Array(5)].map((_, i) => (
              <HiOutlineStar
                key={i}
                className={`w-4 h-4 ${i < Math.floor(average_rating || 0) ? 'fill-current' : ''}`}
              />
            ))}
          </div>
          <span className="text-xs text-gray-500 ml-2">({average_rating || 0})</span>
        </div>

        {/* Price */}
        <div className="flex items-center space-x-2 mb-3">
          <span className="text-lg font-bold text-primary-600">
            ${current_price || regular_price}
          </span>
          {sale_price && (
            <span className="text-sm text-gray-400 line-through">
              ${regular_price}
            </span>
          )}
        </div>

        {/* Add to Cart Button */}
        <button
          onClick={handleAddToCart}
          disabled={!in_stock || addingToCart}
          className="w-full btn-primary py-2 text-sm disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {addingToCart ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Adding...</span>
            </>
          ) : (
            <>
              <HiOutlineShoppingCart className="w-4 h-4" />
              <span>{in_stock ? 'Add to Cart' : 'Out of Stock'}</span>
            </>
          )}
        </button>
      </div>
    </motion.div>
  );
};

export default WishlistItem;