import React, { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlineCheckCircle, 
  HiOutlineExclamationCircle, 
  HiOutlineInformationCircle,
  HiOutlineXCircle,
  HiOutlineX 
} from 'react-icons/hi';

const Alert = ({ type, message, onClose, duration = 5000 }) => {
  useEffect(() => {
    if (duration && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  const icons = {
    success: HiOutlineCheckCircle,
    error: HiOutlineXCircle,
    warning: HiOutlineExclamationCircle,
    info: HiOutlineInformationCircle,
  };

  const colors = {
    success: 'bg-green-50 text-green-800 border-green-200',
    error: 'bg-red-50 text-red-800 border-red-200',
    warning: 'bg-yellow-50 text-yellow-800 border-yellow-200',
    info: 'bg-blue-50 text-blue-800 border-blue-200',
  };

  const Icon = icons[type] || HiOutlineInformationCircle;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`fixed top-24 right-4 z-50 max-w-md ${colors[type]} border rounded-lg shadow-lg`}
    >
      <div className="flex items-center p-4">
        <Icon className="w-5 h-5 mr-3 flex-shrink-0" />
        <p className="text-sm font-medium flex-1">{message}</p>
        {onClose && (
          <button onClick={onClose} className="ml-4">
            <HiOutlineX className="w-4 h-4" />
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default Alert;