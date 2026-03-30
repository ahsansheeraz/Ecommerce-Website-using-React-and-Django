import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  HiOutlineShoppingBag, 
  HiOutlineCalendar, 
  HiOutlineCreditCard,
  HiOutlineTruck,
  HiOutlineCheckCircle,
  HiOutlineXCircle,
  HiOutlineClock
} from 'react-icons/hi';

const OrderCard = ({ order }) => {
  const getStatusIcon = (status) => {
    switch(status) {
      case 'delivered':
        return <HiOutlineCheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <HiOutlineXCircle className="w-5 h-5 text-red-500" />;
      case 'shipped':
        return <HiOutlineTruck className="w-5 h-5 text-blue-500" />;
      default:
        return <HiOutlineClock className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'delivered':
        return 'bg-green-100 text-green-700';
      case 'cancelled':
        return 'bg-red-100 text-red-700';
      case 'shipped':
        return 'bg-blue-100 text-blue-700';
      default:
        return 'bg-yellow-100 text-yellow-700';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -2 }}
      className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all overflow-hidden"
    >
      <Link to={`/orders/${order.order_number}`}>
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-50 to-primary-100 p-4 border-b">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Order Number</p>
              <p className="font-mono font-bold text-primary-600">#{order.order_number}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Total Amount</p>
              <p className="font-bold text-gray-900">${order.total_amount}</p>
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="p-4">
          {/* Date & Status */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <HiOutlineCalendar className="w-4 h-4" />
              <span>{new Date(order.created_at).toLocaleDateString()}</span>
            </div>
            <div className={`flex items-center space-x-1 px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
              {getStatusIcon(order.status)}
              <span className="capitalize">{order.status}</span>
            </div>
          </div>

          {/* Items Preview */}
          <div className="space-y-2 mb-4">
            {order.items?.slice(0, 2).map((item) => (
              <div key={item.id} className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  {item.product_image ? (
                    <img src={item.product_image} alt={item.product_name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      <HiOutlineShoppingBag className="w-5 h-5" />
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900 line-clamp-1">
                    {item.product_name}
                  </p>
                  <p className="text-xs text-gray-500">
                    Qty: {item.quantity} × ${item.unit_price}
                  </p>
                </div>
              </div>
            ))}
            {order.items?.length > 2 && (
              <p className="text-xs text-gray-500 text-center">
                +{order.items.length - 2} more items
              </p>
            )}
          </div>

          {/* Payment Method */}
          <div className="flex items-center space-x-2 text-sm text-gray-600 border-t pt-3">
            <HiOutlineCreditCard className="w-4 h-4" />
            <span className="capitalize">{order.payment_method?.replace('_', ' ')}</span>
            <span className="mx-2">•</span>
            <span className={`${order.payment_status === 'paid' ? 'text-green-600' : 'text-yellow-600'}`}>
              {order.payment_status}
            </span>
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-4 py-3 flex justify-between items-center text-sm">
          <span className="text-primary-600 hover:text-primary-700 font-medium">
            View Details →
          </span>
          {order.status === 'delivered' && (
            <Link 
              to={`/orders/${order.order_number}/return`}
              onClick={(e) => e.stopPropagation()}
              className="text-gray-600 hover:text-primary-600"
            >
              Return
            </Link>
          )}
        </div>
      </Link>
    </motion.div>
  );
};

export default OrderCard;