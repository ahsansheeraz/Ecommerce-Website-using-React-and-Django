import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link, useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { HiOutlineCheckCircle, HiOutlineDownload, HiOutlinePrinter } from 'react-icons/hi';
import { fetchOrderByNumber } from '../store/orderSlice';

const OrderSuccessPage = () => {
  const { orderNumber } = useParams();
  const dispatch = useDispatch();
  const { currentOrder, loading } = useSelector((state) => state.orders);

  useEffect(() => {
    if (orderNumber) {
      dispatch(fetchOrderByNumber(orderNumber));
    }
  }, [dispatch, orderNumber]);

  if (loading) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl shadow-xl p-8 text-center"
        >
          {/* Success Icon */}
          <div className="inline-flex items-center justify-center w-24 h-24 bg-green-100 rounded-full mb-6">
            <HiOutlineCheckCircle className="w-12 h-12 text-green-600" />
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            Order Placed Successfully!
          </h1>
          
          <p className="text-gray-600 mb-6">
            Thank you for your purchase. Your order has been confirmed.
          </p>

          {/* Order Number */}
          <div className="bg-primary-50 p-6 rounded-xl mb-8">
            <p className="text-sm text-gray-600 mb-2">Order Number</p>
            <p className="text-3xl font-bold text-primary-600">#{orderNumber}</p>
          </div>

          {/* Order Details Preview */}
          {currentOrder && (
            <div className="border rounded-lg p-6 mb-8 text-left">
              <h2 className="font-semibold text-gray-900 mb-4">Order Details</h2>
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Date</span>
                  <span className="font-medium">
                    {new Date(currentOrder.created_at).toLocaleDateString()}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Total Amount</span>
                  <span className="font-bold text-primary-600">
                    ${currentOrder.total_amount}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Payment Method</span>
                  <span className="font-medium capitalize">
                    {currentOrder.payment_method?.replace('_', ' ')}
                  </span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Status</span>
                  <span className="inline-flex items-center px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                    {currentOrder.status}
                  </span>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to={`/orders/${orderNumber}`}
              className="btn-primary inline-flex items-center justify-center space-x-2"
            >
              <span>View Order Details</span>
            </Link>
            
            <button className="btn-secondary inline-flex items-center justify-center space-x-2">
              <HiOutlineDownload className="w-4 h-4" />
              <span>Download Invoice</span>
            </button>
            
            <button className="btn-secondary inline-flex items-center justify-center space-x-2">
              <HiOutlinePrinter className="w-4 h-4" />
              <span>Print</span>
            </button>
          </div>

          <div className="border-t pt-6">
            <p className="text-sm text-gray-600 mb-4">
              We've sent a confirmation email with all the details.
            </p>
            <Link to="/shop" className="text-primary-600 hover:text-primary-700 font-medium">
              Continue Shopping →
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default OrderSuccessPage;