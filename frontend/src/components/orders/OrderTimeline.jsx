import React from 'react';
import { motion } from 'framer-motion';
import { 
  HiOutlineShoppingBag,
  HiOutlineCreditCard,
  HiOutlineCheckCircle,
  HiOutlineTruck,
  HiOutlineHome,
  HiOutlineXCircle
} from 'react-icons/hi';

const OrderTimeline = ({ statusHistory }) => {
  const getStatusIcon = (status) => {
    switch(status) {
      case 'pending':
        return HiOutlineShoppingBag;
      case 'processing':
      case 'confirmed':
        return HiOutlineCheckCircle;
      case 'shipped':
      case 'out_for_delivery':
        return HiOutlineTruck;
      case 'delivered':
        return HiOutlineHome;
      case 'cancelled':
        return HiOutlineXCircle;
      default:
        return HiOutlineShoppingBag;
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'pending':
        return 'bg-yellow-500';
      case 'processing':
      case 'confirmed':
        return 'bg-blue-500';
      case 'shipped':
      case 'out_for_delivery':
        return 'bg-purple-500';
      case 'delivered':
        return 'bg-green-500';
      case 'cancelled':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  if (!statusHistory || statusHistory.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No status history available</p>
      </div>
    );
  }

  return (
    <div className="flow-root">
      <ul className="-mb-8">
        {statusHistory.map((event, eventIdx) => {
          const Icon = getStatusIcon(event.status);
          
          return (
            <li key={event.id}>
              <div className="relative pb-8">
                {eventIdx !== statusHistory.length - 1 ? (
                  <span
                    className="absolute left-4 top-4 -ml-px h-full w-0.5 bg-gray-200"
                    aria-hidden="true"
                  />
                ) : null}
                
                <div className="relative flex space-x-3">
                  <div>
                    <span className={`h-8 w-8 rounded-full flex items-center justify-center ring-8 ring-white ${getStatusColor(event.status)}`}>
                      <Icon className="h-4 w-4 text-white" />
                    </span>
                  </div>
                  
                  <div className="flex min-w-0 flex-1 justify-between space-x-4 pt-1.5">
                    <div>
                      <p className="text-sm text-gray-900">
                        {event.status.replace('_', ' ').toUpperCase()}
                      </p>
                      {event.notes && (
                        <p className="mt-1 text-xs text-gray-500">{event.notes}</p>
                      )}
                    </div>
                    <div className="whitespace-nowrap text-right text-xs text-gray-500">
                      <time dateTime={event.created_at}>
                        {new Date(event.created_at).toLocaleString()}
                      </time>
                    </div>
                  </div>
                </div>
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
};

export default OrderTimeline;