import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineTrash, HiOutlineMinus, HiOutlinePlus } from 'react-icons/hi';
import { updateCartItem, removeFromCart } from '../../store/cartSlice';

const CartItem = ({ item }) => {
  const dispatch = useDispatch();
  const [quantity, setQuantity] = useState(item.quantity);
  const [updating, setUpdating] = useState(false);

  const {
    id,
    product_details,
    variant_details,
    unit_price,
    total,
    quantity: maxQuantity
  } = item;

  const handleQuantityChange = async (newQuantity) => {
    if (newQuantity < 1) return;
    
    setUpdating(true);
    setQuantity(newQuantity);
    await dispatch(updateCartItem({ itemId: id, quantity: newQuantity }));
    setUpdating(false);
  };

  const handleRemove = async () => {
    if (window.confirm('Remove this item from cart?')) {
      await dispatch(removeFromCart(id));
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, x: -100 }}
      className="flex items-start space-x-4 py-4 border-b"
    >
      {/* Product Image */}
      <div className="w-20 h-20 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
        {product_details?.primary_image ? (
          <img
            src={product_details.primary_image}
            alt={product_details.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400">
            📦
          </div>
        )}
      </div>

      {/* Product Info */}
      <div className="flex-1">
        <h3 className="font-semibold text-gray-900">{product_details?.name}</h3>
        
        {/* Variant Info */}
        {variant_details && (
          <p className="text-sm text-gray-500">
            {Object.entries(variant_details.attributes || {}).map(([key, value]) => (
              <span key={key} className="mr-2">
                {key}: {value}
              </span>
            ))}
          </p>
        )}

        {/* Price */}
        <div className="flex items-center space-x-2 mt-1">
          <span className="font-medium text-primary-600">
            ${unit_price}
          </span>
          <span className="text-sm text-gray-500">each</span>
        </div>
      </div>

      {/* Quantity Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={() => handleQuantityChange(quantity - 1)}
          disabled={quantity <= 1 || updating}
          className="p-1 rounded-md hover:bg-gray-100 disabled:opacity-50"
        >
          <HiOutlineMinus className="w-4 h-4" />
        </button>
        <span className="w-8 text-center">{quantity}</span>
        <button
          onClick={() => handleQuantityChange(quantity + 1)}
          disabled={updating}
          className="p-1 rounded-md hover:bg-gray-100"
        >
          <HiOutlinePlus className="w-4 h-4" />
        </button>
      </div>

      {/* Item Total */}
      <div className="text-right min-w-[80px]">
        <p className="font-bold text-gray-900">${total}</p>
        <button
          onClick={handleRemove}
          className="text-red-500 hover:text-red-600 mt-1"
        >
          <HiOutlineTrash className="w-5 h-5" />
        </button>
      </div>

      {/* Updating Overlay */}
      {updating && (
        <div className="absolute inset-0 bg-white bg-opacity-50 flex items-center justify-center">
          <div className="w-6 h-6 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
    </motion.div>
  );
};

export default CartItem;