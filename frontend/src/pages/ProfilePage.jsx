import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { 
  HiOutlineUser, 
  HiOutlineMail, 
  HiOutlinePhone,
  HiOutlineLocationMarker,
  HiOutlineHeart,
  HiOutlineShoppingBag,
  HiOutlineLockClosed,
  HiOutlinePencil,
  HiOutlineTrash,
  HiOutlinePlus,
  HiOutlineCheck,
  HiOutlineX 
} from 'react-icons/hi';
import { updateProfile, addAddress, deleteAddress } from '../store/userSlice';
import { userService } from '../services/user';  // ✅ FIXED: Import userService instead of changePassword
import toast from 'react-hot-toast';

const profileSchema = yup.object({
  first_name: yup.string().required('First name is required'),
  last_name: yup.string().required('Last name is required'),
  phone: yup.string().required('Phone number is required'),
  gender: yup.string(),
  occupation: yup.string(),
  company: yup.string(),
});

const passwordSchema = yup.object({
  old_password: yup.string().required('Current password is required'),
  new_password: yup.string()
    .min(8, 'Password must be at least 8 characters')
    .matches(/[A-Z]/, 'Must contain at least one uppercase letter')
    .matches(/[0-9]/, 'Must contain at least one number')
    .required('New password is required'),
  confirm_password: yup.string()
    .oneOf([yup.ref('new_password'), null], 'Passwords must match')
    .required('Please confirm your password'),
});

const addressSchema = yup.object({
  address_type: yup.string().required('Address type is required'),
  name: yup.string().required('Recipient name is required'),
  phone: yup.string().required('Phone number is required'),
  address_line1: yup.string().required('Address line 1 is required'),
  address_line2: yup.string(),
  city: yup.string().required('City is required'),
  state: yup.string().required('State is required'),
  country: yup.string().required('Country is required'),
  postal_code: yup.string().required('Postal code is required'),
  is_default: yup.boolean(),
});

const ProfilePage = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const [isAddingAddress, setIsAddingAddress] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  const { profile, addresses } = useSelector((state) => state.user);
  const dispatch = useDispatch();

  // Profile form
  const {
    register: registerProfile,
    handleSubmit: handleProfileSubmit,
    formState: { errors: profileErrors },
    reset: resetProfile,
  } = useForm({
    resolver: yupResolver(profileSchema),
    defaultValues: profile || {},
  });

  // Password form
  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    reset: resetPassword,
  } = useForm({
    resolver: yupResolver(passwordSchema),
  });

  // Address form
  const {
    register: registerAddress,
    handleSubmit: handleAddressSubmit,
    formState: { errors: addressErrors },
    reset: resetAddress,
  } = useForm({
    resolver: yupResolver(addressSchema),
    defaultValues: {
      address_type: 'shipping',
      is_default: false,
    },
  });

  const onProfileSubmit = async (data) => {
    try {
      await dispatch(updateProfile(data)).unwrap();
      setIsEditingProfile(false);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  // ✅ FIXED: Using userService.changePassword instead of direct changePassword import
  const onPasswordSubmit = async (data) => {
    try {
      await userService.changePassword({
        old_password: data.old_password,
        new_password: data.new_password,
        confirm_password: data.confirm_password,
      });
      setIsChangingPassword(false);
      resetPassword();
      toast.success('Password changed successfully');
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  const onAddressSubmit = async (data) => {
    try {
      await dispatch(addAddress(data)).unwrap();
      setIsAddingAddress(false);
      resetAddress();
      toast.success('Address added successfully');
    } catch (error) {
      toast.error('Failed to add address');
    }
  };

  const handleDeleteAddress = async (id) => {
    if (window.confirm('Are you sure you want to delete this address?')) {
      try {
        await dispatch(deleteAddress(id)).unwrap();
        toast.success('Address deleted successfully');
      } catch (error) {
        toast.error('Failed to delete address');
      }
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: HiOutlineUser },
    { id: 'addresses', name: 'Addresses', icon: HiOutlineLocationMarker },
    { id: 'orders', name: 'Orders', icon: HiOutlineShoppingBag },
    { id: 'wishlist', name: 'Wishlist', icon: HiOutlineHeart },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">My Account</h1>
          <p className="text-gray-600">Manage your profile, addresses, and orders</p>
        </div>

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-64">
            <div className="bg-white rounded-xl shadow-md overflow-hidden">
              {/* User Info */}
              <div className="bg-gradient-to-r from-primary-600 to-primary-800 p-6 text-center">
                <div className="w-20 h-20 bg-white rounded-full mx-auto mb-4 flex items-center justify-center">
                  <span className="text-3xl font-bold text-primary-600">
                    {profile?.first_name?.charAt(0)}
                  </span>
                </div>
                <h3 className="text-white font-semibold">
                  {profile?.first_name} {profile?.last_name}
                </h3>
                <p className="text-primary-100 text-sm">{profile?.email}</p>
              </div>

              {/* Tabs */}
              <nav className="p-4">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg mb-1 transition-colors ${
                      activeTab === tab.id
                        ? 'bg-primary-50 text-primary-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <tab.icon className="w-5 h-5" />
                    <span className="font-medium">{tab.name}</span>
                  </button>
                ))}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="flex-1">
            <AnimatePresence mode="wait">
              {/* Profile Tab */}
              {activeTab === 'profile' && (
                <motion.div
                  key="profile"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-white rounded-xl shadow-md p-6"
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Profile Information</h2>
                    {!isEditingProfile && (
                      <button
                        onClick={() => setIsEditingProfile(true)}
                        className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                      >
                        <HiOutlinePencil className="w-5 h-5" />
                        <span>Edit</span>
                      </button>
                    )}
                  </div>

                  {isEditingProfile ? (
                    <form onSubmit={handleProfileSubmit(onProfileSubmit)} className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            First Name
                          </label>
                          <input
                            type="text"
                            {...registerProfile('first_name')}
                            className={`input-primary ${profileErrors.first_name ? 'border-red-500' : ''}`}
                          />
                          {profileErrors.first_name && (
                            <p className="mt-1 text-sm text-red-600">{profileErrors.first_name.message}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Last Name
                          </label>
                          <input
                            type="text"
                            {...registerProfile('last_name')}
                            className={`input-primary ${profileErrors.last_name ? 'border-red-500' : ''}`}
                          />
                          {profileErrors.last_name && (
                            <p className="mt-1 text-sm text-red-600">{profileErrors.last_name.message}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Phone
                          </label>
                          <input
                            type="tel"
                            {...registerProfile('phone')}
                            className={`input-primary ${profileErrors.phone ? 'border-red-500' : ''}`}
                          />
                          {profileErrors.phone && (
                            <p className="mt-1 text-sm text-red-600">{profileErrors.phone.message}</p>
                          )}
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Gender
                          </label>
                          <select
                            {...registerProfile('gender')}
                            className="input-primary"
                          >
                            <option value="">Select gender</option>
                            <option value="M">Male</option>
                            <option value="F">Female</option>
                            <option value="O">Other</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Occupation
                          </label>
                          <input
                            type="text"
                            {...registerProfile('occupation')}
                            className="input-primary"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Company
                          </label>
                          <input
                            type="text"
                            {...registerProfile('company')}
                            className="input-primary"
                          />
                        </div>
                      </div>

                      <div className="flex justify-end space-x-4">
                        <button
                          type="button"
                          onClick={() => {
                            setIsEditingProfile(false);
                            resetProfile();
                          }}
                          className="btn-secondary"
                        >
                          Cancel
                        </button>
                        <button type="submit" className="btn-primary">
                          Save Changes
                        </button>
                      </div>
                    </form>
                  ) : (
                    <div className="space-y-6">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <p className="text-sm text-gray-500">First Name</p>
                          <p className="font-medium">{profile?.first_name}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Last Name</p>
                          <p className="font-medium">{profile?.last_name}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Email</p>
                          <p className="font-medium">{profile?.email}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Phone</p>
                          <p className="font-medium">{profile?.phone || 'Not provided'}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Gender</p>
                          <p className="font-medium">
                            {profile?.gender === 'M' ? 'Male' : 
                             profile?.gender === 'F' ? 'Female' : 
                             profile?.gender === 'O' ? 'Other' : 'Not specified'}
                          </p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-500">Occupation</p>
                          <p className="font-medium">{profile?.occupation || 'Not provided'}</p>
                        </div>
                      </div>

                      {/* Password Change Section */}
                      <div className="border-t pt-6">
                        <h3 className="text-lg font-semibold text-gray-900 mb-4">Security</h3>
                        {isChangingPassword ? (
                          <form onSubmit={handlePasswordSubmit(onPasswordSubmit)} className="space-y-4">
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Current Password
                              </label>
                              <input
                                type="password"
                                {...registerPassword('old_password')}
                                className={`input-primary ${passwordErrors.old_password ? 'border-red-500' : ''}`}
                              />
                              {passwordErrors.old_password && (
                                <p className="mt-1 text-sm text-red-600">{passwordErrors.old_password.message}</p>
                              )}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                New Password
                              </label>
                              <input
                                type="password"
                                {...registerPassword('new_password')}
                                className={`input-primary ${passwordErrors.new_password ? 'border-red-500' : ''}`}
                              />
                              {passwordErrors.new_password && (
                                <p className="mt-1 text-sm text-red-600">{passwordErrors.new_password.message}</p>
                              )}
                            </div>
                            <div>
                              <label className="block text-sm font-medium text-gray-700 mb-2">
                                Confirm New Password
                              </label>
                              <input
                                type="password"
                                {...registerPassword('confirm_password')}
                                className={`input-primary ${passwordErrors.confirm_password ? 'border-red-500' : ''}`}
                              />
                              {passwordErrors.confirm_password && (
                                <p className="mt-1 text-sm text-red-600">{passwordErrors.confirm_password.message}</p>
                              )}
                            </div>
                            <div className="flex justify-end space-x-4">
                              <button
                                type="button"
                                onClick={() => {
                                  setIsChangingPassword(false);
                                  resetPassword();
                                }}
                                className="btn-secondary"
                              >
                                Cancel
                              </button>
                              <button type="submit" className="btn-primary">
                                Change Password
                              </button>
                            </div>
                          </form>
                        ) : (
                          <button
                            onClick={() => setIsChangingPassword(true)}
                            className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                          >
                            <HiOutlineLockClosed className="w-5 h-5" />
                            <span>Change Password</span>
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {/* Addresses Tab */}
              {activeTab === 'addresses' && (
                <motion.div
                  key="addresses"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-white rounded-xl shadow-md p-6"
                >
                  <div className="flex justify-between items-center mb-6">
                    <h2 className="text-xl font-semibold text-gray-900">Saved Addresses</h2>
                    {!isAddingAddress && (
                      <button
                        onClick={() => setIsAddingAddress(true)}
                        className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
                      >
                        <HiOutlinePlus className="w-5 h-5" />
                        <span>Add New Address</span>
                      </button>
                    )}
                  </div>

                  {isAddingAddress && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mb-6 p-6 border-2 border-dashed border-primary-200 rounded-lg"
                    >
                      <h3 className="text-lg font-medium text-gray-900 mb-4">Add New Address</h3>
                      <form onSubmit={handleAddressSubmit(onAddressSubmit)} className="space-y-4">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Address Type
                            </label>
                            <select
                              {...registerAddress('address_type')}
                              className={`input-primary ${addressErrors.address_type ? 'border-red-500' : ''}`}
                            >
                              <option value="shipping">Shipping Address</option>
                              <option value="billing">Billing Address</option>
                              <option value="both">Both</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Recipient Name
                            </label>
                            <input
                              type="text"
                              {...registerAddress('name')}
                              className={`input-primary ${addressErrors.name ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Phone Number
                            </label>
                            <input
                              type="tel"
                              {...registerAddress('phone')}
                              className={`input-primary ${addressErrors.phone ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Address Line 1
                            </label>
                            <input
                              type="text"
                              {...registerAddress('address_line1')}
                              className={`input-primary ${addressErrors.address_line1 ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Address Line 2 (Optional)
                            </label>
                            <input
                              type="text"
                              {...registerAddress('address_line2')}
                              className="input-primary"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              City
                            </label>
                            <input
                              type="text"
                              {...registerAddress('city')}
                              className={`input-primary ${addressErrors.city ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              State
                            </label>
                            <input
                              type="text"
                              {...registerAddress('state')}
                              className={`input-primary ${addressErrors.state ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Country
                            </label>
                            <input
                              type="text"
                              {...registerAddress('country')}
                              className={`input-primary ${addressErrors.country ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                              Postal Code
                            </label>
                            <input
                              type="text"
                              {...registerAddress('postal_code')}
                              className={`input-primary ${addressErrors.postal_code ? 'border-red-500' : ''}`}
                            />
                          </div>
                          <div className="flex items-center">
                            <input
                              type="checkbox"
                              {...registerAddress('is_default')}
                              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                            />
                            <label className="ml-2 block text-sm text-gray-700">
                              Set as default address
                            </label>
                          </div>
                        </div>

                        <div className="flex justify-end space-x-4 mt-4">
                          <button
                            type="button"
                            onClick={() => {
                              setIsAddingAddress(false);
                              resetAddress();
                            }}
                            className="btn-secondary"
                          >
                            Cancel
                          </button>
                          <button type="submit" className="btn-primary">
                            Save Address
                          </button>
                        </div>
                      </form>
                    </motion.div>
                  )}

                  <div className="space-y-4">
                    {addresses?.map((address) => (
                      <motion.div
                        key={address.id}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className={`p-4 border rounded-lg ${
                          address.is_default ? 'border-primary-500 bg-primary-50' : 'border-gray-200'
                        }`}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1">
                            <div className="flex items-center space-x-3 mb-2">
                              <span className="px-2 py-1 bg-gray-100 text-xs font-medium rounded">
                                {address.address_type === 'shipping' ? 'Shipping' :
                                 address.address_type === 'billing' ? 'Billing' : 'Both'}
                              </span>
                              {address.is_default && (
                                <span className="px-2 py-1 bg-primary-100 text-primary-600 text-xs font-medium rounded">
                                  Default
                                </span>
                              )}
                              <span className="font-medium">{address.name}</span>
                            </div>
                            <p className="text-gray-600 text-sm mb-1">
                              {address.address_line1}
                              {address.address_line2 && `, ${address.address_line2}`}
                            </p>
                            <p className="text-gray-600 text-sm mb-1">
                              {address.city}, {address.state} {address.postal_code}
                            </p>
                            <p className="text-gray-600 text-sm mb-1">{address.country}</p>
                            <p className="text-gray-600 text-sm">Phone: {address.phone}</p>
                          </div>
                          <div className="flex space-x-2">
                            <button
                              onClick={() => handleDeleteAddress(address.id)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <HiOutlineTrash className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      </motion.div>
                    ))}

                    {addresses?.length === 0 && !isAddingAddress && (
                      <div className="text-center py-12">
                        <HiOutlineLocationMarker className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-medium text-gray-900 mb-2">No addresses saved</h3>
                        <p className="text-gray-600 mb-4">Add your first address to start shopping</p>
                        <button
                          onClick={() => setIsAddingAddress(true)}
                          className="btn-primary inline-flex items-center space-x-2"
                        >
                          <HiOutlinePlus className="w-5 h-5" />
                          <span>Add Address</span>
                        </button>
                      </div>
                    )}
                  </div>
                </motion.div>
              )}

              {/* Orders Tab */}
              {activeTab === 'orders' && (
                <motion.div
                  key="orders"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-white rounded-xl shadow-md p-6"
                >
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">Order History</h2>
                  
                  <div className="text-center py-12">
                    <HiOutlineShoppingBag className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No orders yet</h3>
                    <p className="text-gray-600 mb-4">Start shopping to see your orders here</p>
                    <button className="btn-primary">Start Shopping</button>
                  </div>
                </motion.div>
              )}

              {/* Wishlist Tab */}
              {activeTab === 'wishlist' && (
                <motion.div
                  key="wishlist"
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  className="bg-white rounded-xl shadow-md p-6"
                >
                  <h2 className="text-xl font-semibold text-gray-900 mb-6">My Wishlist</h2>
                  
                  <div className="text-center py-12">
                    <HiOutlineHeart className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Your wishlist is empty</h3>
                    <p className="text-gray-600 mb-4">Save items you love to your wishlist</p>
                    <button className="btn-primary">Browse Products</button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;