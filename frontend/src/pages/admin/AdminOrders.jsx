import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineSearch,
  HiOutlineFilter,
  HiOutlineEye,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineRefresh
} from 'react-icons/hi';
import { fetchAdminOrders, updateOrderStatus } from '../../store/adminSlice';
import toast from 'react-hot-toast';

const AdminOrders = () => {
  const dispatch = useDispatch();
  const { orders, pagination, filters, loading } = useSelector((state) => state.admin);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [statusData, setStatusData] = useState({
    status: '',
    tracking_number: '',
    shipped_via: '',
    estimated_delivery: '',
    notes: ''
  });

  useEffect(() => {
    dispatch(fetchAdminOrders({ page: 1, search: searchTerm, status: statusFilter }));
  }, [dispatch, searchTerm, statusFilter]);

  const handleFilterChange = (newFilters) => {
    dispatch(setOrderFilters(newFilters));
    dispatch(fetchAdminOrders({ ...filters, ...newFilters }));
  };

  const handleStatusUpdate = async (e) => {
    e.preventDefault();
    try {
      await dispatch(updateOrderStatus({ 
        orderNumber: selectedOrder.order_number, 
        statusData 
      })).unwrap();
      toast.success('Order status updated successfully');
      setShowStatusModal(false);
      setSelectedOrder(null);
      setStatusData({
        status: '',
        tracking_number: '',
        shipped_via: '',
        estimated_delivery: '',
        notes: ''
      });
    } catch (error) {
      toast.error('Failed to update order status');
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'delivered': return 'bg-green-100 text-green-700';
      case 'shipped': return 'bg-blue-100 text-blue-700';
      case 'processing': return 'bg-purple-100 text-purple-700';
      case 'pending': return 'bg-yellow-100 text-yellow-700';
      case 'cancelled': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
          <p className="text-gray-600 mt-1">Manage and track customer orders</p>
        </div>
        
        <button
          onClick={() => dispatch(fetchAdminOrders())}
          className="btn-secondary flex items-center space-x-2"
        >
          <HiOutlineRefresh className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </motion.div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <div className="flex-1 relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search orders by number, customer, email..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="shipped">Shipped</option>
            <option value="delivered">Delivered</option>
            <option value="cancelled">Cancelled</option>
          </select>

          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`px-4 py-2 border rounded-lg flex items-center space-x-2 ${
              showFilters ? 'bg-primary-50 text-primary-600 border-primary-300' : ''
            }`}
          >
            <HiOutlineFilter className="w-4 h-4" />
            <span>More Filters</span>
          </button>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4"
          >
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date From
              </label>
              <input type="date" className="input-primary" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date To
              </label>
              <input type="date" className="input-primary" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Payment Method
              </label>
              <select className="input-primary">
                <option value="">All</option>
                <option value="card">Card</option>
                <option value="cash_on_delivery">Cash on Delivery</option>
              </select>
            </div>
          </motion.div>
        )}
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Order #</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Customer</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Date</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Total</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Payment</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Status</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan="7" className="text-center py-12">
                    <div className="flex justify-center">
                      <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                    </div>
                  </td>
                </tr>
              ) : orders?.length === 0 ? (
                <tr>
                  <td colSpan="7" className="text-center py-12 text-gray-500">
                    No orders found
                  </td>
                </tr>
              ) : (
                orders?.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <span className="font-mono font-medium text-primary-600">
                        #{order.order_number}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{order.customer_name}</p>
                        <p className="text-sm text-gray-500">{order.customer_email}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4">
                      <span className="font-medium text-primary-600">
                        ${order.total_amount}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        order.payment_status === 'paid' 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-yellow-100 text-yellow-700'
                      }`}>
                        {order.payment_status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setSelectedOrder(order);
                            setShowStatusModal(true);
                          }}
                          className="p-1 text-gray-500 hover:text-primary-600"
                          title="Update Status"
                        >
                          <HiOutlineRefresh className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => window.open(`/orders/${order.order_number}`, '_blank')}
                          className="p-1 text-gray-500 hover:text-primary-600"
                          title="View Details"
                        >
                          <HiOutlineEye className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination?.orders?.count > 0 && (
          <div className="px-6 py-4 border-t flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {((filters.orders.page - 1) * 10) + 1} to {Math.min(filters.orders.page * 10, pagination.orders.count)} of {pagination.orders.count} orders
            </p>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => handleFilterChange({ page: filters.orders.page - 1 })}
                disabled={!pagination.orders.previous}
                className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <HiOutlineChevronLeft className="w-4 h-4" />
              </button>
              
              <span className="px-3 py-1 bg-primary-50 text-primary-600 rounded-lg text-sm">
                Page {filters.orders.page}
              </span>
              
              <button
                onClick={() => handleFilterChange({ page: filters.orders.page + 1 })}
                disabled={!pagination.orders.next}
                className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <HiOutlineChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Update Status Modal */}
      {showStatusModal && selectedOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <motion.div
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            className="bg-white rounded-xl shadow-2xl w-full max-w-md"
          >
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Update Order Status
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                Order #{selectedOrder.order_number}
              </p>
              
              <form onSubmit={handleStatusUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Status *
                  </label>
                  <select
                    value={statusData.status}
                    onChange={(e) => setStatusData({ ...statusData, status: e.target.value })}
                    required
                    className="input-primary"
                  >
                    <option value="">Select Status</option>
                    <option value="pending">Pending</option>
                    <option value="processing">Processing</option>
                    <option value="shipped">Shipped</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                {statusData.status === 'shipped' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Tracking Number
                      </label>
                      <input
                        type="text"
                        value={statusData.tracking_number}
                        onChange={(e) => setStatusData({ ...statusData, tracking_number: e.target.value })}
                        className="input-primary"
                        placeholder="e.g., TRK123456789"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Shipping Carrier
                      </label>
                      <input
                        type="text"
                        value={statusData.shipped_via}
                        onChange={(e) => setStatusData({ ...statusData, shipped_via: e.target.value })}
                        className="input-primary"
                        placeholder="e.g., FedEx, UPS, DHL"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Estimated Delivery
                      </label>
                      <input
                        type="date"
                        value={statusData.estimated_delivery}
                        onChange={(e) => setStatusData({ ...statusData, estimated_delivery: e.target.value })}
                        className="input-primary"
                      />
                    </div>
                  </>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Notes (Optional)
                  </label>
                  <textarea
                    value={statusData.notes}
                    onChange={(e) => setStatusData({ ...statusData, notes: e.target.value })}
                    rows="3"
                    className="input-primary"
                    placeholder="Additional notes about this order..."
                  />
                </div>

                <div className="flex justify-end space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowStatusModal(false);
                      setSelectedOrder(null);
                      setStatusData({
                        status: '',
                        tracking_number: '',
                        shipped_via: '',
                        estimated_delivery: '',
                        notes: ''
                      });
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Update Status
                  </button>
                </div>
              </form>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
};

// ✅ DEFAULT EXPORT
export default AdminOrders;