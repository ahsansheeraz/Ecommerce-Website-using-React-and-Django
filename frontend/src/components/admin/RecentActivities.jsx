import React from 'react';
import { motion } from 'framer-motion';
import { 
  HiOutlineUserAdd,
  HiOutlineShoppingBag,
  HiOutlineCurrencyDollar,
  HiOutlineTag,
  HiOutlineRefresh
} from 'react-icons/hi';

const RecentActivities = ({ activities }) => {
  const getActivityIcon = (action) => {
    switch(action) {
      case 'create':
        return <HiOutlineUserAdd className="w-5 h-5 text-green-500" />;
      case 'update':
        return <HiOutlineRefresh className="w-5 h-5 text-blue-500" />;
      case 'order':
        return <HiOutlineShoppingBag className="w-5 h-5 text-purple-500" />;
      case 'payment':
        return <HiOutlineCurrencyDollar className="w-5 h-5 text-yellow-500" />;
      case 'product':
        return <HiOutlineTag className="w-5 h-5 text-orange-500" />;
      default:
        return <HiOutlineRefresh className="w-5 h-5 text-gray-500" />;
    }
  };

  const sampleActivities = activities || [
    {
      id: 1,
      action: 'create',
      user: 'John Doe',
      target: 'New user registered',
      time: '5 minutes ago',
      avatar: 'JD'
    },
    {
      id: 2,
      action: 'order',
      user: 'Sarah Smith',
      target: 'Placed order #12345',
      time: '15 minutes ago',
      avatar: 'SS'
    },
    {
      id: 3,
      action: 'payment',
      user: 'Mike Johnson',
      target: 'Payment received $299.99',
      time: '25 minutes ago',
      avatar: 'MJ'
    },
    {
      id: 4,
      action: 'product',
      user: 'Admin',
      target: 'Added new product "iPhone 15"',
      time: '1 hour ago',
      avatar: 'AD'
    },
    {
      id: 5,
      action: 'update',
      user: 'Moderator',
      target: 'Updated order status to shipped',
      time: '2 hours ago',
      avatar: 'MO'
    }
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-md p-6"
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activities</h3>
      
      <div className="space-y-4">
        {sampleActivities.map((activity) => (
          <div key={activity.id} className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center">
                {getActivityIcon(activity.action)}
              </div>
            </div>
            
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900">
                {activity.user}
              </p>
              <p className="text-sm text-gray-500">
                {activity.target}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                {activity.time}
              </p>
            </div>
            
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-xs font-medium text-primary-600">
                  {activity.avatar}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <button className="w-full mt-4 text-center text-sm text-primary-600 hover:text-primary-700 font-medium">
        View All Activities →
      </button>
    </motion.div>
  );
};

export default RecentActivities;