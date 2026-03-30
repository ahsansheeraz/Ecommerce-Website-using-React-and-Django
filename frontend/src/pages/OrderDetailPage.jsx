import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineArrowLeft } from 'react-icons/hi';
import { fetchOrderByNumber } from '../store/orderSlice';
import OrderDetails from '../components/orders/OrderDetails';
import OrderTimeline from '../components/orders/OrderTimeline';
import OrderTracking from '../components/orders/OrderTracking';

const OrderDetailPage = () => {
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Link
          to="/orders"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          <HiOutlineArrowLeft className="w-4 h-4 mr-2" />
          <span>Back to Orders</span>
        </Link>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">
            Order #{currentOrder.order_number}
          </h1>
          <p className="text-gray-600 mt-2">
            Placed on {new Date(currentOrder.created_at).toLocaleDateString()}
          </p>
        </motion.div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Order Details */}
          <div className="lg:col-span-2">
            <OrderDetails order={currentOrder} />
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Order Timeline */}
            <OrderTimeline statusHistory={currentOrder.status_history} />

            {/* Tracking Information */}
            {currentOrder.tracking_number && (
              <OrderTracking trackingInfo={{
                tracking_number: currentOrder.tracking_number,
                shipped_via: currentOrder.shipped_via,
                estimated_delivery: currentOrder.estimated_delivery,
                delivered_at: currentOrder.delivered_at
              }} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderDetailPage;