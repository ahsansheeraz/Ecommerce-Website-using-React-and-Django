import React from 'react';
import { motion } from 'framer-motion';
import { 
  HiOutlineUsers,
  HiOutlineShoppingBag,
  HiOutlineCurrencyDollar,
  HiOutlineShoppingCart,
  HiOutlineTrendingUp,
  HiOutlineClock
} from 'react-icons/hi';

const DashboardStats = ({ stats }) => {
  // ✅ Add default values to prevent undefined errors
  const safeStats = stats || {
    totalUsers: 0,
    newUsersToday: 0,
    totalOrders: 0,
    ordersToday: 0,
    totalRevenue: 0,
    revenueToday: 0,
    totalProducts: 0,
    lowStockProducts: 0
  };

  const statCards = [
    {
      title: 'Total Users',
      value: safeStats.totalUsers || 0,
      change: `+${safeStats.newUsersToday || 0} today`,
      icon: HiOutlineUsers,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-100',
      textColor: 'text-blue-600'
    },
    {
      title: 'Total Orders',
      value: safeStats.totalOrders || 0,
      change: `+${safeStats.ordersToday || 0} today`,
      icon: HiOutlineShoppingBag,
      color: 'bg-green-500',
      bgColor: 'bg-green-100',
      textColor: 'text-green-600'
    },
    {
      title: 'Total Revenue',
      value: `$${safeStats.totalRevenue?.toLocaleString() || 0}`,
      change: `$${safeStats.revenueToday?.toLocaleString() || 0} today`,
      icon: HiOutlineCurrencyDollar,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-100',
      textColor: 'text-purple-600'
    },
    {
      title: 'Total Products',
      value: safeStats.totalProducts || 0,
      change: `${safeStats.lowStockProducts || 0} low in stock`,
      icon: HiOutlineShoppingCart,
      color: 'bg-orange-500',
      bgColor: 'bg-orange-100',
      textColor: 'text-orange-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((stat, index) => {
        const Icon = stat.icon;
        
        return (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-4">
              <div className={`${stat.bgColor} p-3 rounded-lg`}>
                <Icon className={`w-6 h-6 ${stat.textColor}`} />
              </div>
              <span className="text-xs font-medium text-gray-400 flex items-center">
                <HiOutlineClock className="w-3 h-3 mr-1" />
                Live
              </span>
            </div>
            
            <h3 className="text-2xl font-bold text-gray-900 mb-1">
              {stat.value}
            </h3>
            
            <p className="text-sm text-gray-600">{stat.title}</p>
            
            <div className="mt-3 flex items-center text-xs">
              <HiOutlineTrendingUp className="w-3 h-3 text-green-500 mr-1" />
              <span className="text-green-600 font-medium">{stat.change}</span>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
};

export default DashboardStats;