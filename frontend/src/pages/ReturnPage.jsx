import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineArrowLeft } from 'react-icons/hi';
import { fetchOrderByNumber } from '../store/orderSlice';
import ReturnForm from '../components/orders/ReturnForm';

const ReturnPage = () => {
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

  if (!currentOrder) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Order Not Found</h2>
          <Link to="/orders" className="btn-primary">
            Back to Orders
          </Link>
        </div>
      </div>
    );
  }

  if (!currentOrder.is_returnable) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="text-center max-w-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Cannot Return Order</h2>
          <p className="text-gray-600 mb-6">
            This order is not eligible for return. Orders can only be returned within 30 days of delivery.
          </p>
          <Link to={`/orders/${orderNumber}`} className="btn-primary">
            Back to Order Details
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-3xl mx-auto px-4">
        {/* Back Button */}
        <Link
          to={`/orders/${orderNumber}`}
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          <HiOutlineArrowLeft className="w-4 h-4 mr-2" />
          <span>Back to Order Details</span>
        </Link>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">Return Items</h1>
          <p className="text-gray-600 mt-2">
            Order #{currentOrder.order_number}
          </p>
        </motion.div>

        {/* Return Form */}
        <ReturnForm order={currentOrder} />
      </div>
    </div>
  );
};

export default ReturnPage;