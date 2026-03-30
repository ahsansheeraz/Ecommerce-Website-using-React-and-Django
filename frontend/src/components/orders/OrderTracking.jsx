import React from 'react';
import { motion } from 'framer-motion';
import { 
  HiOutlineTruck,
  HiOutlineLocationMarker,
  HiOutlineCalendar,
  HiOutlineCube  // ✅ Fixed: Changed from HiOutlinePackage to HiOutlineCube
} from 'react-icons/hi';

const OrderTracking = ({ trackingInfo }) => {
  if (!trackingInfo || !trackingInfo.tracking_number) {
    return (
      <div className="text-center py-8 bg-gray-50 rounded-lg">
        <HiOutlineCube className="w-12 h-12 text-gray-400 mx-auto mb-3" /> {/* ✅ Fixed */}
        <p className="text-gray-500">No tracking information available</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <HiOutlineTruck className="w-5 h-5 mr-2 text-primary-600" />
        Tracking Information
      </h3>

      {/* Tracking Number */}
      <div className="bg-primary-50 p-4 rounded-lg mb-4">
        <p className="text-xs text-gray-600 mb-1">Tracking Number</p>
        <p className="font-mono font-bold text-primary-600 text-lg">
          {trackingInfo.tracking_number}
        </p>
      </div>

      {/* Shipping Details */}
      <div className="space-y-3">
        {trackingInfo.shipped_via && (
          <div className="flex items-center space-x-3">
            <HiOutlineCube className="w-5 h-5 text-gray-400" /> {/* ✅ Fixed */}
            <div>
              <p className="text-xs text-gray-500">Carrier</p>
              <p className="text-sm font-medium">{trackingInfo.shipped_via}</p>
            </div>
          </div>
        )}

        {trackingInfo.estimated_delivery && (
          <div className="flex items-center space-x-3">
            <HiOutlineCalendar className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Estimated Delivery</p>
              <p className="text-sm font-medium">
                {new Date(trackingInfo.estimated_delivery).toLocaleDateString()}
              </p>
            </div>
          </div>
        )}

        {trackingInfo.delivered_at && (
          <div className="flex items-center space-x-3">
            <HiOutlineLocationMarker className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-xs text-gray-500">Delivered On</p>
              <p className="text-sm font-medium">
                {new Date(trackingInfo.delivered_at).toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Track Button */}
      <button className="w-full btn-primary mt-4">
        Track Package
      </button>
    </motion.div>
  );
};

export default OrderTracking;