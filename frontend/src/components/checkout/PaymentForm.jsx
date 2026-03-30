import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { 
  HiOutlineCreditCard, 
  HiOutlineCash,
  HiOutlineShieldCheck,
  HiOutlineLockClosed
} from 'react-icons/hi';
import { setPaymentMethod, createOrder, nextStep } from '../../store/checkoutSlice';
import { clearCart } from '../../store/cartSlice';
import toast from 'react-hot-toast';

const PaymentForm = () => {
  const dispatch = useDispatch();
  const { shippingAddress, billingAddress, couponCode, discountAmount } = 
    useSelector((state) => state.checkout);
  const { total } = useSelector((state) => state.cart);
  const { user } = useSelector((state) => state.auth);
  
  const [processing, setProcessing] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState('card');

  const { register, handleSubmit, formState: { errors } } = useForm();

  const paymentMethods = [
    {
      id: 'card',
      name: 'Credit / Debit Card',
      icon: HiOutlineCreditCard,
      description: 'Pay securely with your card'
    },
    {
      id: 'cash_on_delivery',
      name: 'Cash on Delivery',
      icon: HiOutlineCash,
      description: 'Pay when you receive your order'
    }
  ];

  const onSubmit = async (data) => {
    setProcessing(true);
    
    try {
      // Create order
      const orderData = {
        shipping_address_id: shippingAddress.id,
        billing_address_id: billingAddress.id || shippingAddress.id,
        payment_method: selectedMethod,
        customer_notes: data.notes || '',
        coupon_code: couponCode
      };

      const orderResult = await dispatch(createOrder(orderData)).unwrap();
      
      if (selectedMethod === 'card') {
        // Handle card payment (would integrate with Stripe/PayPal here)
        toast.success('Order placed successfully!');
      } else {
        // Cash on delivery
        toast.success('Order placed successfully! You\'ll pay on delivery.');
      }

      // Clear cart and move to success page
      dispatch(clearCart());
      dispatch(nextStep());
      
    } catch (error) {
      toast.error(error.message || 'Failed to place order');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
        <HiOutlineCreditCard className="w-6 h-6 mr-2 text-primary-600" />
        Payment Method
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Payment Methods */}
        <div className="space-y-3">
          {paymentMethods.map((method) => {
            const Icon = method.icon;
            return (
              <label
                key={method.id}
                className={`flex items-start space-x-4 p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedMethod === method.id
                    ? 'border-primary-600 bg-primary-50'
                    : 'hover:border-primary-300'
                }`}
              >
                <input
                  type="radio"
                  name="paymentMethod"
                  value={method.id}
                  checked={selectedMethod === method.id}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="h-4 w-4 mt-1 text-primary-600"
                />
                <div className="flex-1">
                  <div className="flex items-center">
                    <Icon className={`w-5 h-5 mr-2 ${
                      selectedMethod === method.id ? 'text-primary-600' : 'text-gray-400'
                    }`} />
                    <span className="font-medium">{method.name}</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{method.description}</p>
                </div>
              </label>
            );
          })}
        </div>

        {/* Order Notes */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Order Notes (Optional)
          </label>
          <textarea
            {...register('notes')}
            rows="3"
            className="input-primary"
            placeholder="Any special instructions for delivery?"
          />
        </div>

        {/* Security Notice */}
        <div className="bg-blue-50 p-4 rounded-lg flex items-start space-x-3">
          <HiOutlineShieldCheck className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-blue-800">Secure Payment</p>
            <p className="text-xs text-blue-600 mt-1">
              Your payment information is encrypted and secure. We never store your card details.
            </p>
          </div>
        </div>

        {/* Order Summary */}
        <div className="border-t pt-4">
          <h3 className="font-semibold text-gray-900 mb-3">Order Summary</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">${total.toFixed(2)}</span>
            </div>
            {discountAmount > 0 && (
              <div className="flex justify-between text-green-600">
                <span>Discount</span>
                <span>-${discountAmount.toFixed(2)}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-600">Shipping</span>
              <span className="text-green-600">Free</span>
            </div>
            <div className="flex justify-between text-base font-bold pt-2 border-t">
              <span>Total</span>
              <span className="text-primary-600">${(total - discountAmount).toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={processing}
          className="w-full btn-primary py-3 text-lg disabled:opacity-50 flex items-center justify-center space-x-2"
        >
          {processing ? (
            <>
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              <span>Processing...</span>
            </>
          ) : (
            <>
              <HiOutlineLockClosed className="w-5 h-5" />
              <span>Place Order • ${(total - discountAmount).toFixed(2)}</span>
            </>
          )}
        </button>

        {/* Terms Notice */}
        <p className="text-xs text-center text-gray-500">
          By placing your order, you agree to our{' '}
          <a href="/terms" className="text-primary-600 hover:underline">Terms of Service</a>{' '}
          and{' '}
          <a href="/privacy" className="text-primary-600 hover:underline">Privacy Policy</a>
        </p>
      </form>
    </motion.div>
  );
};

export default PaymentForm;