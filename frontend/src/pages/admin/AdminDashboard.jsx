import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import DashboardStats from '../../components/admin/DashboardStats';
import DashboardCharts from '../../components/admin/DashboardCharts';
import RecentActivities from '../../components/admin/RecentActivities';
import { fetchDashboardStats, fetchActivityLogs } from '../../store/adminSlice';

const AdminDashboard = () => {
  const dispatch = useDispatch();
  const { stats, loading, error } = useSelector((state) => state.admin);

  useEffect(() => {
    dispatch(fetchDashboardStats());
    dispatch(fetchActivityLogs());
  }, [dispatch]);

  // ✅ Show loading state while fetching data
  if (loading && !stats) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>
    );
  }

  // ✅ Show error state if API fails
  if (error) {
    return (
      <div className="text-center py-12">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md mx-auto">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Dashboard</h3>
          <p className="text-red-600 text-sm">{error}</p>
          <button
            onClick={() => dispatch(fetchDashboardStats())}
            className="mt-4 btn-primary text-sm"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Welcome back! Here's what's happening with your store.</p>
      </motion.div>

      {/* Stats - Pass stats object (will be empty object if undefined) */}
      <DashboardStats stats={stats} />

      {/* Charts */}
      <DashboardCharts />

      {/* Recent Activities */}
      <RecentActivities />
    </div>
  );
};

export default AdminDashboard;