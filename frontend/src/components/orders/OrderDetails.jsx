import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineLocationMarker,
  HiOutlineCreditCard,
  HiOutlineUser,
  HiOutlinePhone,
  HiOutlineMail,
  HiOutlineRefresh,
  HiOutlineXCircle
} from 'react-icons/hi';
import { cancelOrder } from '../../store/orderSlice';
import toast from 'react-hot-toast';

const OrderDetails = ({ order }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [cancelling, setCancelling] = useState(false);

  const handleCancelOrder = async () => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return;
    }

    setCancelling(true);
    try {
      await dispatch(cancelOrder(order.order_number)).unwrap();
      toast.success('Order cancelled successfully');
    } catch (error) {
      toast.error('Failed to cancel order');
    } finally {
      setCancelling(false);
    }
  };

  const handleReturnOrder = () => {
    navigate(`/orders/${order.order_number}/return`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden"
    >
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 px-6 py-4">
        <h2 className="text-xl font-bold text-white">Order Details</h2>
      </div>

      <div className="p-6 space-y-6">
        {/* Customer Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <HiOutlineUser className="w-5 h-5 mr-2 text-primary-600" />
            Customer Information
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <p className="font-medium">{order.customer?.first_name} {order.customer?.last_name}</p>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <HiOutlineMail className="w-4 h-4" />
              <span>{order.customer?.email}</span>
            </div>
            {order.customer?.phone && (
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <HiOutlinePhone className="w-4 h-4" />
                <span>{order.customer?.phone}</span>
              </div>
            )}
          </div>
        </div>

        {/* Shipping Address */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <HiOutlineLocationMarker className="w-5 h-5 mr-2 text-primary-600" />
            Shipping Address
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="font-medium">{order.shipping_address?.name}</p>
            <p className="text-sm text-gray-600">{order.shipping_address?.address_line1}</p>
            {order.shipping_address?.address_line2 && (
              <p className="text-sm text-gray-600">{order.shipping_address?.address_line2}</p>
            )}
            <p className="text-sm text-gray-600">
              {order.shipping_address?.city}, {order.shipping_address?.state} {order.shipping_address?.postal_code}
            </p>
            <p className="text-sm text-gray-600">{order.shipping_address?.country}</p>
            <p className="text-sm text-gray-600 mt-2">Phone: {order.shipping_address?.phone}</p>
          </div>
        </div>

        {/* Payment Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <HiOutlineCreditCard className="w-5 h-5 mr-2 text-primary-600" />
            Payment Information
          </h3>
          <div className="bg-gray-50 p-4 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Method</span>
              <span className="font-medium capitalize">{order.payment_method?.replace('_', ' ')}</span>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-600">Status</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                order.payment_status === 'paid' 
                  ? 'bg-green-100 text-green-700' 
                  : 'bg-yellow-100 text-yellow-700'
              }`}>
                {order.payment_status}
              </span>
            </div>
            {order.coupon && (
              <div className="flex justify-between items-center text-green-600">
                <span className="text-sm">Coupon Applied</span>
                <span className="font-medium">{order.coupon.code}</span>
              </div>
            )}
          </div>
        </div>

        {/* Order Items */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Items</h3>
          <div className="space-y-4">
            {order.items?.map((item) => (
              <div key={item.id} className="flex items-start space-x-4 border-b pb-4 last:border-0">
                <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                  {item.product_image ? (
                    <img src={item.product_image} alt={item.product_name} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      📦
                    </div>
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{item.product_name}</p>
                  <p className="text-sm text-gray-500">SKU: {item.product_sku}</p>
                  {item.variant_details && (
                    <p className="text-xs text-gray-500">
                      {Object.entries(item.variant_details.attributes || {}).map(([key, value]) => (
                        <span key={key} className="mr-2">{key}: {value}</span>
                      ))}
                    </p>
                  )}
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm text-gray-600">Qty: {item.quantity}</span>
                    <span className="font-medium text-primary-600">
                      ${item.total_price}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Order Summary */}
        <div className="border-t pt-4">
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Subtotal</span>
              <span className="font-medium">${order.subtotal}</span>
            </div>
            {order.discount_amount > 0 && (
              <div className="flex justify-between text-sm text-green-600">
                <span>Discount</span>
                <span>-${order.discount_amount}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Shipping</span>
              <span className="text-green-600">${order.shipping_cost}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-600">Tax</span>
              <span>${order.tax_amount}</span>
            </div>
            <div className="flex justify-between font-bold pt-2 border-t">
              <span>Total</span>
              <span className="text-primary-600">${order.total_amount}</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {order.is_cancellable && (
          <div className="flex space-x-4 pt-4">
            <button
              onClick={handleCancelOrder}
              disabled={cancelling}
              className="flex-1 btn-secondary flex items-center justify-center space-x-2"
            >
              {cancelling ? (
                <>
                  <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin"></div>
                  <span>Cancelling...</span>
                </>
              ) : (
                <>
                  <HiOutlineXCircle className="w-4 h-4" />
                  <span>Cancel Order</span>
                </>
              )}
            </button>
          </div>
        )}

        {order.is_returnable && (
          <div className="flex space-x-4 pt-4">
            <button
              onClick={handleReturnOrder}
              className="flex-1 btn-secondary flex items-center justify-center space-x-2"
            >
              <HiOutlineRefresh className="w-4 h-4" />
              <span>Return Items</span>
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default OrderDetails;