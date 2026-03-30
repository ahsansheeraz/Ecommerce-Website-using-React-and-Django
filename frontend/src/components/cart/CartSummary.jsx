import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineTag, HiOutlineX } from 'react-icons/hi';
import { applyCoupon, removeCoupon } from '../../store/cartSlice';
import toast from 'react-hot-toast';

const CartSummary = ({ subtotal, totalDiscount, total, appliedCoupons }) => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const [couponCode, setCouponCode] = useState('');
  const [applying, setApplying] = useState(false);

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    if (!couponCode.trim()) return;

    setApplying(true);
    try {
      await dispatch(applyCoupon(couponCode)).unwrap();
      toast.success('Coupon applied successfully!');
      setCouponCode('');
    } catch (error) {
      toast.error(error?.message || 'Invalid coupon code');
    } finally {
      setApplying(false);
    }
  };

  const handleRemoveCoupon = async () => {
    await dispatch(removeCoupon());
    toast.success('Coupon removed');
  };

  const handleCheckout = () => {
    navigate('/checkout');
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl shadow-lg p-6 sticky top-24"
    >
      <h2 className="text-xl font-bold text-gray-900 mb-6">Order Summary</h2>

      {/* Price Breakdown */}
      <div className="space-y-3 mb-6">
        <div className="flex justify-between text-gray-600">
          <span>Subtotal</span>
          <span>${subtotal.toFixed(2)}</span>
        </div>
        
        {totalDiscount > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Discount</span>
            <span>-${totalDiscount.toFixed(2)}</span>
          </div>
        )}

        <div className="flex justify-between text-gray-600">
          <span>Shipping</span>
          <span className="text-green-600">Free</span>
        </div>

        <div className="border-t pt-3 mt-3">
          <div className="flex justify-between text-lg font-bold">
            <span>Total</span>
            <span className="text-primary-600">${total.toFixed(2)}</span>
          </div>
        </div>
      </div>

      {/* Applied Coupons */}
      {appliedCoupons?.length > 0 && (
        <div className="mb-4">
          <p className="text-sm font-medium text-gray-700 mb-2">Applied Coupons:</p>
          {appliedCoupons.map((coupon, index) => (
            <div
              key={index}
              className="flex items-center justify-between bg-green-50 text-green-700 px-3 py-2 rounded-lg mb-2"
            >
              <span className="text-sm font-medium">{coupon.code}</span>
              <button
                onClick={handleRemoveCoupon}
                className="text-green-700 hover:text-green-800"
              >
                <HiOutlineX className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Coupon Form */}
      <form onSubmit={handleApplyCoupon} className="mb-6">
        <div className="flex space-x-2">
          <div className="relative flex-1">
            <HiOutlineTag className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={couponCode}
              onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
              placeholder="Coupon code"
              className="input-primary pl-10"
              disabled={applying}
            />
          </div>
          <button
            type="submit"
            disabled={!couponCode.trim() || applying}
            className="btn-secondary whitespace-nowrap"
          >
            {applying ? 'Applying...' : 'Apply'}
          </button>
        </div>
      </form>

      {/* Checkout Button */}
      <button
        onClick={handleCheckout}
        disabled={total === 0}
        className="btn-primary w-full py-3 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Proceed to Checkout
      </button>

      {/* Payment Methods */}
      <div className="mt-4 text-center">
        <p className="text-xs text-gray-500 mb-2">We accept:</p>
        <div className="flex justify-center space-x-2">
          <img src="/visa.svg" alt="Visa" className="h-6" />
          <img src="/mastercard.svg" alt="Mastercard" className="h-6" />
          <img src="/paypal.svg" alt="PayPal" className="h-6" />
        </div>
      </div>
    </motion.div>
  );
};

export default CartSummary;