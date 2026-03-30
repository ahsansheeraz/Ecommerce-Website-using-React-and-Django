import React from 'react';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineLocationMarker, HiOutlineTruck, HiOutlineCreditCard } from 'react-icons/hi';

const OrderSummary = () => {
  const { shippingAddress, paymentMethod, shippingMethod } = 
    useSelector((state) => state.checkout);
  const { items, subtotal, totalDiscount, total } = useSelector((state) => state.cart);
  const { user } = useSelector((state) => state.auth);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6 space-y-6"
    >
      <h2 className="text-lg font-bold text-gray-900">Order Summary</h2>

      {/* Customer Info */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="font-medium text-gray-900">{user?.first_name} {user?.last_name}</p>
        <p className="text-sm text-gray-600">{user?.email}</p>
        <p className="text-sm text-gray-600">{user?.phone}</p>
      </div>

      {/* Shipping Address */}
      {shippingAddress && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <HiOutlineLocationMarker className="w-4 h-4 mr-1 text-primary-600" />
            Shipping Address
          </h3>
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            <p className="font-medium">{shippingAddress.name}</p>
            <p>{shippingAddress.address_line1}</p>
            {shippingAddress.address_line2 && <p>{shippingAddress.address_line2}</p>}
            <p>{shippingAddress.city}, {shippingAddress.state} {shippingAddress.postal_code}</p>
            <p>{shippingAddress.country}</p>
            <p className="mt-1">Phone: {shippingAddress.phone}</p>
          </div>
        </div>
      )}

      {/* Payment Method */}
      {paymentMethod && (
        <div>
          <h3 className="text-sm font-medium text-gray-700 mb-2 flex items-center">
            <HiOutlineCreditCard className="w-4 h-4 mr-1 text-primary-600" />
            Payment Method
          </h3>
          <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded-lg">
            <p className="capitalize">{paymentMethod.replace('_', ' ')}</p>
          </div>
        </div>
      )}

      {/* Items List */}
      <div>
        <h3 className="text-sm font-medium text-gray-700 mb-2">Items</h3>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {items.map((item) => (
            <div key={item.id} className="flex justify-between text-sm">
              <span className="text-gray-600">
                {item.product_details?.name} x {item.quantity}
              </span>
              <span className="font-medium">${item.total}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Price Breakdown */}
      <div className="border-t pt-4 space-y-2">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Subtotal</span>
          <span className="font-medium">${subtotal.toFixed(2)}</span>
        </div>
        {totalDiscount > 0 && (
          <div className="flex justify-between text-sm text-green-600">
            <span>Discount</span>
            <span>-${totalDiscount.toFixed(2)}</span>
          </div>
        )}
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">Shipping</span>
          <span className="text-green-600">Free</span>
        </div>
        <div className="flex justify-between font-bold pt-2 border-t">
          <span>Total</span>
          <span className="text-primary-600">${total.toFixed(2)}</span>
        </div>
      </div>
    </motion.div>
  );
};

export default OrderSummary;