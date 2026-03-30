import React from 'react';
import { NavLink } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlineMenu,
  HiOutlineHome,
  HiOutlineShoppingBag,
  HiOutlineShoppingCart,
  HiOutlineUsers,
  HiOutlineTag,
  HiOutlineChartBar,
  HiOutlineCog,
  HiOutlineLogout,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineBell,
  HiOutlineDocumentReport
} from 'react-icons/hi';
import { toggleSidebar } from '../../store/adminSlice';
import { logout } from '../../store/authSlice';

const AdminSidebar = () => {
  const dispatch = useDispatch();
  const { sidebarOpen } = useSelector((state) => state.admin);
  const { user } = useSelector((state) => state.auth);

  const menuItems = [
    { path: '/admin', icon: HiOutlineHome, label: 'Dashboard', exact: true },
    { path: '/admin/products', icon: HiOutlineShoppingBag, label: 'Products' },
    { path: '/admin/orders', icon: HiOutlineShoppingCart, label: 'Orders' },
    { path: '/admin/users', icon: HiOutlineUsers, label: 'Users' },
    { path: '/admin/categories', icon: HiOutlineTag, label: 'Categories' },
    { path: '/admin/reports', icon: HiOutlineDocumentReport, label: 'Reports' },
    { path: '/admin/analytics', icon: HiOutlineChartBar, label: 'Analytics' },
    { path: '/admin/settings', icon: HiOutlineCog, label: 'Settings' },
  ];

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <motion.aside
      initial={{ width: sidebarOpen ? 256 : 80 }}
      animate={{ width: sidebarOpen ? 256 : 80 }}
      transition={{ duration: 0.3 }}
      className="fixed left-0 top-0 h-full bg-gradient-to-b from-primary-800 to-primary-900 text-white shadow-2xl z-50 overflow-hidden"
    >
      {/* Logo */}
      <div className="h-20 flex items-center justify-between px-4 border-b border-primary-700">
        <AnimatePresence mode="wait">
          {sidebarOpen ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="flex items-center space-x-2"
            >
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-primary-800 font-bold text-xl">A</span>
              </div>
              <span className="font-bold text-lg">Admin Panel</span>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="w-full flex justify-center"
            >
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                <span className="text-primary-800 font-bold text-xl">A</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <button
          onClick={() => dispatch(toggleSidebar())}
          className="p-1 rounded-lg hover:bg-primary-700 transition-colors"
        >
          {sidebarOpen ? (
            <HiOutlineChevronLeft className="w-5 h-5" />
          ) : (
            <HiOutlineChevronRight className="w-5 h-5" />
          )}
        </button>
      </div>

      {/* User Info */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="p-4 border-b border-primary-700"
          >
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center">
                <span className="text-lg font-semibold">
                  {user?.first_name?.charAt(0)}
                </span>
              </div>
              <div>
                <p className="font-medium">{user?.first_name} {user?.last_name}</p>
                <p className="text-xs text-primary-300 capitalize">{user?.user_type}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Navigation */}
      <nav className="p-4 space-y-2">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.exact}
            className={({ isActive }) => `
              flex items-center space-x-3 px-4 py-3 rounded-lg transition-all
              ${isActive 
                ? 'bg-primary-600 text-white shadow-lg' 
                : 'text-primary-100 hover:bg-primary-700 hover:text-white'
              }
            `}
          >
            <item.icon className="w-5 h-5 flex-shrink-0" />
            <AnimatePresence mode="wait">
              {sidebarOpen && (
                <motion.span
                  initial={{ opacity: 0, width: 0 }}
                  animate={{ opacity: 1, width: 'auto' }}
                  exit={{ opacity: 0, width: 0 }}
                  className="text-sm font-medium whitespace-nowrap"
                >
                  {item.label}
                </motion.span>
              )}
            </AnimatePresence>
          </NavLink>
        ))}
      </nav>

      {/* Logout Button */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-primary-700">
        <button
          onClick={handleLogout}
          className="flex items-center space-x-3 px-4 py-3 rounded-lg text-primary-100 hover:bg-red-600 hover:text-white transition-all w-full"
        >
          <HiOutlineLogout className="w-5 h-5 flex-shrink-0" />
          <AnimatePresence mode="wait">
            {sidebarOpen && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                className="text-sm font-medium"
              >
                Logout
              </motion.span>
            )}
          </AnimatePresence>
        </button>
      </div>
    </motion.aside>
  );
};

export default AdminSidebar;