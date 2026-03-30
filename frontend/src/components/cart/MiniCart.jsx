import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineX, HiOutlineShoppingBag } from 'react-icons/hi';
import { closeCart, removeFromCart } from '../../store/cartSlice';

const MiniCart = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { isOpen, items, totalItems, total } = useSelector((state) => state.cart);

  const handleViewCart = () => {
    dispatch(closeCart());
    navigate('/cart');
  };

  const handleCheckout = () => {
    dispatch(closeCart());
    navigate('/checkout');
  };

  const handleRemove = (itemId) => {
    dispatch(removeFromCart(itemId));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.5 }}
            exit={{ opacity: 0 }}
            onClick={() => dispatch(closeCart())}
            className="fixed inset-0 bg-black z-40"
          />

          {/* Cart Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'tween' }}
            className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 overflow-y-auto"
          >
            {/* Header */}
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <HiOutlineShoppingBag className="w-5 h-5 text-primary-600" />
                <h2 className="text-lg font-semibold">Your Cart ({totalItems})</h2>
              </div>
              <button
                onClick={() => dispatch(closeCart())}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <HiOutlineX className="w-5 h-5" />
              </button>
            </div>

            {/* Cart Items */}
            <div className="p-4 space-y-4">
              {items?.length === 0 ? (
                <p className="text-center text-gray-500 py-8">Your cart is empty</p>
              ) : (
                items.map((item) => (
                  <div key={item.id} className="flex space-x-3 border-b pb-4">
                    <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                      {item.product_details?.primary_image ? (
                        <img
                          src={item.product_details.primary_image}
                          alt={item.product_details.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          📦
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-sm">{item.product_details?.name}</h3>
                      <p className="text-sm text-gray-500">Qty: {item.quantity}</p>
                      <p className="text-sm font-medium text-primary-600 mt-1">
                        ${item.total}
                      </p>
                    </div>
                    <button
                      onClick={() => handleRemove(item.id)}
                      className="text-red-500 hover:text-red-600"
                    >
                      <HiOutlineX className="w-4 h-4" />
                    </button>
                  </div>
                ))
              )}
            </div>

            {/* Footer */}
            {items?.length > 0 && (
              <div className="sticky bottom-0 bg-white border-t p-4">
                <div className="flex justify-between mb-4">
                  <span className="font-semibold">Subtotal:</span>
                  <span className="font-bold text-primary-600">${total}</span>
                </div>
                <div className="space-y-2">
                  <button
                    onClick={handleViewCart}
                    className="w-full btn-secondary"
                  >
                    View Cart
                  </button>
                  <button
                    onClick={handleCheckout}
                    className="w-full btn-primary"
                  >
                    Checkout
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default MiniCart;