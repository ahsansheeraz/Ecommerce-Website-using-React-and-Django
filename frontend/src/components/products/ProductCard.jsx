import React from 'react';
import { Link } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineHeart, HiOutlineShoppingCart, HiOutlineStar } from 'react-icons/hi';
import WishlistButton from '../wishlist/WishlistButton';
import { addToCart } from '../../store/cartSlice';
import toast from 'react-hot-toast';

const ProductCard = ({ product }) => {
  const dispatch = useDispatch();
  
  const {
    id,
    name,
    slug,
    primary_image,
    current_price,
    regular_price,
    sale_price,
    discount_percentage,
    average_rating,
    reviews_count,
    in_stock
  } = product;

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    dispatch(addToCart({ productId: id, quantity: 1 }));
    toast.success('Added to cart!');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5 }}
      className="group bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden"
    >
      {/* Image Container */}
      <Link to={`/product/${slug}`} className="block relative overflow-hidden">
        <div className="aspect-square bg-gray-100">
          {primary_image ? (
            <img
              src={primary_image}
              alt={name}
              className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-400">
              No Image
            </div>
          )}
        </div>

        {/* Discount Badge */}
        {discount_percentage > 0 && (
          <div className="absolute top-2 left-2 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded">
            -{discount_percentage}%
          </div>
        )}

        {/* Out of Stock Overlay */}
        {!in_stock && (
          <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
            <span className="bg-red-500 text-white px-4 py-2 rounded-lg font-semibold transform -rotate-12">
              Out of Stock
            </span>
          </div>
        )}

        {/* Quick Action Buttons */}
        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* 🔥 UPDATED: WishlistButton component with proper props */}
          <WishlistButton 
            productId={id} 
            className="bg-white p-2 rounded-full shadow-lg hover:bg-pink-50 transition-colors mb-2 block"
          />
          
          {/* 🔥 UPDATED: Cart button with functionality */}
          <button 
            onClick={handleAddToCart}
            disabled={!in_stock}
            className="bg-white p-2 rounded-full shadow-lg hover:bg-primary-50 transition-colors block disabled:opacity-50 disabled:cursor-not-allowed"
            title={in_stock ? 'Add to cart' : 'Out of stock'}
          >
            <HiOutlineShoppingCart className="w-5 h-5 text-gray-600 hover:text-primary-600" />
          </button>
        </div>
      </Link>

      {/* Product Info */}
      <div className="p-4">
        <Link to={`/product/${slug}`}>
          <h3 className="text-lg font-semibold text-gray-800 hover:text-primary-600 transition-colors line-clamp-2 mb-2">
            {name}
          </h3>
        </Link>

        {/* Rating */}
        <div className="flex items-center mb-2">
          <div className="flex items-center text-yellow-400">
            {[...Array(5)].map((_, i) => (
              <HiOutlineStar
                key={i}
                className={`w-4 h-4 ${i < Math.floor(average_rating) ? 'fill-current' : ''}`}
              />
            ))}
          </div>
          <span className="text-sm text-gray-500 ml-2">({reviews_count || 0})</span>
        </div>

        {/* Price */}
        <div className="flex items-center space-x-2">
          <span className="text-xl font-bold text-primary-600">
            ${current_price}
          </span>
          {sale_price && (
            <span className="text-sm text-gray-400 line-through">
              ${regular_price}
            </span>
          )}
        </div>

        {/* Stock Status */}
        <div className="mt-2">
          {in_stock ? (
            <span className="text-xs text-green-600">✓ In Stock</span>
          ) : (
            <span className="text-xs text-red-600">✗ Out of Stock</span>
          )}
        </div>

        {/* 🔥 NEW: Mobile Add to Cart Button (visible only on mobile) */}
        <button
          onClick={handleAddToCart}
          disabled={!in_stock}
          className="mt-3 w-full btn-primary py-2 text-sm md:hidden flex items-center justify-center space-x-2 disabled:opacity-50"
        >
          <HiOutlineShoppingCart className="w-4 h-4" />
          <span>{in_stock ? 'Add to Cart' : 'Out of Stock'}</span>
        </button>
      </div>
    </motion.div>
  );
};

export default ProductCard;