import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlineShoppingCart, 
  HiOutlineHeart, 
  HiOutlineUser, 
  HiOutlineMenu, 
  HiOutlineX,
  HiOutlineLogout 
} from 'react-icons/hi';
import { logout } from '../../store/authSlice';
import { openCart } from '../../store/cartSlice';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const { totalItems } = useSelector((state) => state.cart); // 🔥 NEW: Get cart total items
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await dispatch(logout());
    navigate('/');
  };

  const navLinks = [
    { name: 'Home', path: '/' },
    { name: 'Shop', path: '/shop' },
    { name: 'About', path: '/about' },
    { name: 'Contact', path: '/contact' },
  ];

  return (
    <nav className="bg-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-700 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">E</span>
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-primary-800 bg-clip-text text-transparent">
              Mart
            </span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.name}
                to={link.path}
                className="text-gray-700 hover:text-primary-600 font-medium transition-colors relative group"
              >
                {link.name}
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-primary-600 transition-all group-hover:w-full"></span>
              </Link>
            ))}
          </div>

          {/* Desktop Icons */}
          <div className="hidden md:flex items-center space-x-6">
            {/* 🔥 UPDATED: Cart button with openCart function and dynamic counter */}
            <button
              onClick={() => dispatch(openCart())}
              className="relative group"
            >
              <HiOutlineShoppingCart className="w-6 h-6 text-gray-700 group-hover:text-primary-600 transition-colors" />
              {totalItems > 0 && (
                <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
                  {totalItems}
                </span>
              )}
            </button>
            
            {/* Wishlist link - keep as is */}
            <Link to="/wishlist" className="relative group">
              <HiOutlineHeart className="w-6 h-6 text-gray-700 group-hover:text-primary-600 transition-colors" />
            </Link>

            {isAuthenticated ? (
              <div className="relative group">
                <button className="flex items-center space-x-2 focus:outline-none">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <span className="text-primary-600 font-semibold">
                      {user?.first_name?.charAt(0) || 'U'}
                    </span>
                  </div>
                </button>
                
                {/* Dropdown */}
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-xl py-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link to="/profile" className="block px-4 py-2 text-gray-700 hover:bg-primary-50 hover:text-primary-600">
                    Profile
                  </Link>
                  <Link to="/orders" className="block px-4 py-2 text-gray-700 hover:bg-primary-50 hover:text-primary-600">
                    Orders
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-red-600 hover:bg-red-50 flex items-center space-x-2"
                  >
                    <HiOutlineLogout className="w-4 h-4" />
                    <span>Logout</span>
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center space-x-4">
                <Link to="/login" className="btn-secondary text-sm px-4 py-2">
                  Login
                </Link>
                <Link to="/register" className="btn-primary text-sm px-4 py-2">
                  Register
                </Link>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            {isOpen ? (
              <HiOutlineX className="w-6 h-6" />
            ) : (
              <HiOutlineMenu className="w-6 h-6" />
            )}
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden bg-white border-t"
          >
            <div className="px-4 py-4 space-y-3">
              {navLinks.map((link) => (
                <Link
                  key={link.name}
                  to={link.path}
                  className="block py-2 text-gray-700 hover:text-primary-600"
                  onClick={() => setIsOpen(false)}
                >
                  {link.name}
                </Link>
              ))}
              
              {/* 🔥 NEW: Mobile cart and wishlist links */}
              <div className="flex items-center space-x-4 py-2 border-t border-gray-200">
                <Link
                  to="/cart"
                  className="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
                  onClick={() => setIsOpen(false)}
                >
                  <div className="relative">
                    <HiOutlineShoppingCart className="w-5 h-5" />
                    {totalItems > 0 && (
                      <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
                        {totalItems}
                      </span>
                    )}
                  </div>
                  <span>Cart</span>
                </Link>
                
                <Link
                  to="/wishlist"
                  className="flex items-center space-x-2 text-gray-700 hover:text-primary-600"
                  onClick={() => setIsOpen(false)}
                >
                  <HiOutlineHeart className="w-5 h-5" />
                  <span>Wishlist</span>
                </Link>
              </div>

              <div className="border-t pt-4">
                {isAuthenticated ? (
                  <>
                    <div className="flex items-center space-x-3 mb-4">
                      <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-primary-600 font-semibold text-xl">
                          {user?.first_name?.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold">{user?.first_name} {user?.last_name}</p>
                        <p className="text-sm text-gray-500">{user?.email}</p>
                      </div>
                    </div>
                    <Link
                      to="/profile"
                      className="block py-2 text-gray-700 hover:text-primary-600"
                      onClick={() => setIsOpen(false)}
                    >
                      Profile
                    </Link>
                    <Link
                      to="/orders"
                      className="block py-2 text-gray-700 hover:text-primary-600"
                      onClick={() => setIsOpen(false)}
                    >
                      Orders
                    </Link>
                    <button
                      onClick={() => {
                        handleLogout();
                        setIsOpen(false);
                      }}
                      className="w-full text-left py-2 text-red-600 hover:text-red-700 flex items-center space-x-2"
                    >
                      <HiOutlineLogout className="w-4 h-4" />
                      <span>Logout</span>
                    </button>
                  </>
                ) : (
                  <div className="space-y-3">
                    <Link
                      to="/login"
                      className="block w-full btn-secondary text-center"
                      onClick={() => setIsOpen(false)}
                    >
                      Login
                    </Link>
                    <Link
                      to="/register"
                      className="block w-full btn-primary text-center"
                      onClick={() => setIsOpen(false)}
                    >
                      Register
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;