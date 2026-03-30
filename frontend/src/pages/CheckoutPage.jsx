import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import CheckoutSteps from '../components/checkout/CheckoutSteps';
import ShippingForm from '../components/checkout/ShippingForm';
import PaymentForm from '../components/checkout/PaymentForm';
import OrderSummary from '../components/checkout/OrderSummary';
import OrderConfirmation from '../components/checkout/OrderConfirmation';
import { fetchCart } from '../store/cartSlice';
import { fetchAddresses } from '../store/userSlice';
import { fetchShippingMethods, fetchPaymentMethods } from '../store/checkoutSlice';

const CheckoutPage = () => {
  const dispatch = useDispatch();
  const { currentStep, orderComplete } = useSelector((state) => state.checkout);
  const { items, total } = useSelector((state) => state.cart);
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchCart());
      dispatch(fetchAddresses());
      dispatch(fetchShippingMethods());
      dispatch(fetchPaymentMethods());
    }
  }, [dispatch, isAuthenticated]);

  // Redirect to cart if cart is empty
  if (items?.length === 0 && !orderComplete) {
    return <Navigate to="/cart" />;
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: '/checkout' }} />;
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return <ShippingForm />;
      case 2:
        return <PaymentForm />;
      case 3:
        return <OrderConfirmation />;
      default:
        return <ShippingForm />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
          <p className="text-gray-600 mt-2">
            Complete your purchase by providing shipping and payment information
          </p>
        </motion.div>

        {/* Checkout Steps */}
        <CheckoutSteps currentStep={currentStep} />

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
          {/* Step Forms */}
          <div className="lg:col-span-2">
            {renderStep()}
          </div>

          {/* Order Summary (hide on confirmation step) */}
          {currentStep < 3 && (
            <div className="lg:col-span-1">
              <OrderSummary />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;