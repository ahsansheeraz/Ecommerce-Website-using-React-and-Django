import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineSearch,
  HiOutlineFilter,
  HiOutlineUser,
  HiOutlineMail,
  HiOutlinePhone,
  HiOutlineCalendar,
  HiOutlineShieldCheck,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineRefresh,
  HiOutlinePencil,
  HiOutlineTrash,
  HiOutlinePlus
} from 'react-icons/hi';
import { fetchAdminUsers, updateUserRole } from '../../store/adminSlice';
import toast from 'react-hot-toast';

const AdminUsers = () => {
  const dispatch = useDispatch();
  const { users, pagination, filters, loading } = useSelector((state) => state.admin);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [roleData, setRoleData] = useState({
    user_type: '',
    is_active: true,
    is_staff: false,
    is_superuser: false
  });

  useEffect(() => {
    dispatch(fetchAdminUsers({ 
      page: 1, 
      search: searchTerm, 
      role: roleFilter,
      status: statusFilter 
    }));
  }, [dispatch, searchTerm, roleFilter, statusFilter]);

  const handleRoleUpdate = async (e) => {
    e.preventDefault();
    try {
      await dispatch(updateUserRole({ 
        userId: selectedUser.id, 
        roleData 
      })).unwrap();
      toast.success('User role updated successfully');
      setShowRoleModal(false);
      setSelectedUser(null);
    } catch (error) {
      toast.error('Failed to update user role');
    }
  };

  const getRoleBadgeColor = (role) => {
    switch(role) {
      case 'admin': return 'bg-purple-100 text-purple-700';
      case 'moderator': return 'bg-blue-100 text-blue-700';
      case 'seller': return 'bg-green-100 text-green-700';
      case 'customer': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  // ✅ FIX: Add safety check for users array
  const userList = Array.isArray(users) ? users : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex justify-between items-center"
      >
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Users</h1>
          <p className="text-gray-600 mt-1">Manage customers and staff accounts</p>
        </div>
        
        {/* ✅ Issue 8: Add User Button */}
        <button
          onClick={() => setShowAddUserModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <HiOutlinePlus className="w-5 h-5" />
          <span>Add User</span>
        </button>
      </motion.div>

      {/* Search and Filter Bar */}
      <div className="bg-white rounded-xl shadow-md p-4">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search users by name, email, phone..."
              className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>

          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Roles</option>
            <option value="admin">Admin</option>
            <option value="moderator">Moderator</option>
            <option value="seller">Seller</option>
            <option value="customer">Customer</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>

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

        {showFilters && (
          <div className="mt-4 pt-4 border-t grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Registered From
              </label>
              <input type="date" className="input-primary" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Registered To
              </label>
              <input type="date" className="input-primary" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Last Login
              </label>
              <input type="date" className="input-primary" />
            </div>
          </div>
        )}
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl shadow-md overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">User</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Contact</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Role</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Status</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Joined</th>
                <th className="text-left px-6 py-3 text-sm font-medium text-gray-600">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {loading ? (
                <tr>
                  <td colSpan="6" className="text-center py-12">
                    <div className="flex justify-center">
                      <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                    </div>
                  </td>
                </tr>
              ) : userList.length === 0 ? (
                <tr>
                  <td colSpan="6" className="text-center py-12 text-gray-500">
                    No users found
                  </td>
                </tr>
              ) : (
                userList.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                          <span className="text-primary-600 font-semibold">
                            {user.first_name?.charAt(0) || user.email?.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {user.first_name} {user.last_name}
                          </p>
                          <p className="text-sm text-gray-500">@{user.email?.split('@')[0]}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="space-y-1">
                        <div className="flex items-center text-sm text-gray-600">
                          <HiOutlineMail className="w-4 h-4 mr-2" />
                          <span>{user.email}</span>
                        </div>
                        {user.phone && (
                          <div className="flex items-center text-sm text-gray-600">
                            <HiOutlinePhone className="w-4 h-4 mr-2" />
                            <span>{user.phone}</span>
                          </div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRoleBadgeColor(user.user_type)}`}>
                        {user.user_type}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        user.is_active 
                          ? 'bg-green-100 text-green-700' 
                          : 'bg-red-100 text-red-700'
                      }`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center text-sm text-gray-600">
                        <HiOutlineCalendar className="w-4 h-4 mr-2" />
                        <span>{new Date(user.date_joined).toLocaleDateString()}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => {
                            setSelectedUser(user);
                            setRoleData({
                              user_type: user.user_type,
                              is_active: user.is_active,
                              is_staff: user.is_staff || false,
                              is_superuser: user.is_superuser || false
                            });
                            setShowRoleModal(true);
                          }}
                          className="p-1 text-gray-500 hover:text-primary-600"
                          title="Edit Role"
                        >
                          <HiOutlinePencil className="w-4 h-4" />
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
        {pagination?.users?.count > 0 && (
          <div className="px-6 py-4 border-t flex items-center justify-between">
            <p className="text-sm text-gray-600">
              Showing {((filters.users.page - 1) * 10) + 1} to {Math.min(filters.users.page * 10, pagination.users.count)} of {pagination.users.count} users
            </p>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => dispatch(setUserFilters({ page: filters.users.page - 1 }))}
                disabled={!pagination.users.previous}
                className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <HiOutlineChevronLeft className="w-4 h-4" />
              </button>
              
              <span className="px-3 py-1 bg-primary-50 text-primary-600 rounded-lg text-sm">
                Page {filters.users.page}
              </span>
              
              <button
                onClick={() => dispatch(setUserFilters({ page: filters.users.page + 1 }))}
                disabled={!pagination.users.next}
                className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50"
              >
                <HiOutlineChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Edit Role Modal */}
      {showRoleModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Edit User Role
              </h2>
              <p className="text-sm text-gray-600 mb-4">
                User: {selectedUser.first_name} {selectedUser.last_name} ({selectedUser.email})
              </p>
              
              <form onSubmit={handleRoleUpdate} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    User Role *
                  </label>
                  <select
                    value={roleData.user_type}
                    onChange={(e) => setRoleData({ ...roleData, user_type: e.target.value })}
                    required
                    className="input-primary"
                  >
                    <option value="customer">Customer</option>
                    <option value="seller">Seller</option>
                    <option value="moderator">Moderator</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="space-y-2">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={roleData.is_active}
                      onChange={(e) => setRoleData({ ...roleData, is_active: e.target.checked })}
                      className="h-4 w-4 text-primary-600 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Account Active</span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={roleData.is_staff}
                      onChange={(e) => setRoleData({ ...roleData, is_staff: e.target.checked })}
                      className="h-4 w-4 text-primary-600 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Staff Status</span>
                  </label>

                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={roleData.is_superuser}
                      onChange={(e) => setRoleData({ ...roleData, is_superuser: e.target.checked })}
                      className="h-4 w-4 text-primary-600 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">Superuser (Full Access)</span>
                  </label>
                </div>

                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                  <p className="text-xs text-yellow-700">
                    <HiOutlineShieldCheck className="w-4 h-4 inline mr-1" />
                    <strong>Warning:</strong> Changing roles affects user permissions.
                  </p>
                </div>

                <div className="flex justify-end space-x-4 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowRoleModal(false);
                      setSelectedUser(null);
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button type="submit" className="btn-primary">
                    Update Role
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Add User Modal (Simple version) */}
      {showAddUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
            <div className="p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Add New User</h2>
              <p className="text-sm text-gray-600 mb-4">Coming soon...</p>
              <button
                onClick={() => setShowAddUserModal(false)}
                className="btn-primary w-full"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminUsers;