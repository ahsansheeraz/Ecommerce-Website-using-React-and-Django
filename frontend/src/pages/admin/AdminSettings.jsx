import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineSave,
  HiOutlineRefresh,
  HiOutlineEye,
  HiOutlineEyeOff,
  HiOutlineGlobe,
  HiOutlineMail,
  HiOutlineCurrencyDollar,
  HiOutlineShieldCheck,
  HiOutlineTruck,
  HiOutlineCog
} from 'react-icons/hi';
import { fetchSettings, updateSettings } from '../../store/adminSlice';
import toast from 'react-hot-toast';

const AdminSettings = () => {
  const dispatch = useDispatch();
  const { settings, loading } = useSelector((state) => state.admin);
  const [activeTab, setActiveTab] = useState('general');
  const [formData, setFormData] = useState({});
  const [showSensitive, setShowSensitive] = useState({});

  useEffect(() => {
    dispatch(fetchSettings());
  }, [dispatch]);

  useEffect(() => {
    if (settings) {
      // Convert settings array to object
      const settingsObj = {};
      settings.forEach(setting => {
        settingsObj[setting.key] = setting.value;
      });
      setFormData(settingsObj);
    }
  }, [settings]);

  const handleChange = (key, value) => {
    setFormData(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Convert form data back to array format for API
    const settingsArray = Object.entries(formData).map(([key, value]) => ({
      key,
      value
    }));

    try {
      await dispatch(updateSettings(settingsArray)).unwrap();
      toast.success('Settings updated successfully');
    } catch (error) {
      toast.error('Failed to update settings');
    }
  };

  const toggleSensitive = (key) => {
    setShowSensitive(prev => ({
      ...prev,
      [key]: !prev[key]
    }));
  };

  const tabs = [
    { id: 'general', name: 'General', icon: HiOutlineCog },
    { id: 'store', name: 'Store', icon: HiOutlineGlobe },
    { id: 'email', name: 'Email', icon: HiOutlineMail },
    { id: 'payment', name: 'Payment', icon: HiOutlineCurrencyDollar },
    { id: 'shipping', name: 'Shipping', icon: HiOutlineTruck },
    { id: 'security', name: 'Security', icon: HiOutlineShieldCheck }
  ];

  const renderSettings = () => {
    switch(activeTab) {
      case 'general':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Site Name
                </label>
                <input
                  type="text"
                  value={formData.SITE_NAME || ''}
                  onChange={(e) => handleChange('SITE_NAME', e.target.value)}
                  className="input-primary"
                  placeholder="My Store"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Site URL
                </label>
                <input
                  type="url"
                  value={formData.SITE_URL || ''}
                  onChange={(e) => handleChange('SITE_URL', e.target.value)}
                  className="input-primary"
                  placeholder="https://example.com"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Site Description
              </label>
              <textarea
                value={formData.SITE_DESCRIPTION || ''}
                onChange={(e) => handleChange('SITE_DESCRIPTION', e.target.value)}
                rows="4"
                className="input-primary"
                placeholder="Describe your store..."
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Timezone
                </label>
                <select
                  value={formData.TIME_ZONE || 'UTC'}
                  onChange={(e) => handleChange('TIME_ZONE', e.target.value)}
                  className="input-primary"
                >
                  <option value="UTC">UTC</option>
                  <option value="America/New_York">Eastern Time</option>
                  <option value="America/Chicago">Central Time</option>
                  <option value="America/Denver">Mountain Time</option>
                  <option value="America/Los_Angeles">Pacific Time</option>
                  <option value="Europe/London">London</option>
                  <option value="Asia/Dubai">Dubai</option>
                  <option value="Asia/Karachi">Karachi</option>
                  <option value="Asia/Kolkata">Kolkata</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default Language
                </label>
                <select
                  value={formData.LANGUAGE_CODE || 'en'}
                  onChange={(e) => handleChange('LANGUAGE_CODE', e.target.value)}
                  className="input-primary"
                >
                  <option value="en">English</option>
                  <option value="es">Spanish</option>
                  <option value="fr">French</option>
                  <option value="de">German</option>
                  <option value="ur">Urdu</option>
                </select>
              </div>
            </div>
          </div>
        );

      case 'email':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Host
                </label>
                <input
                  type="text"
                  value={formData.EMAIL_HOST || ''}
                  onChange={(e) => handleChange('EMAIL_HOST', e.target.value)}
                  className="input-primary"
                  placeholder="smtp.gmail.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Port
                </label>
                <input
                  type="number"
                  value={formData.EMAIL_PORT || ''}
                  onChange={(e) => handleChange('EMAIL_PORT', e.target.value)}
                  className="input-primary"
                  placeholder="587"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Username
                </label>
                <input
                  type="text"
                  value={formData.EMAIL_HOST_USER || ''}
                  onChange={(e) => handleChange('EMAIL_HOST_USER', e.target.value)}
                  className="input-primary"
                  placeholder="user@example.com"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Password
                </label>
                <div className="relative">
                  <input
                    type={showSensitive.EMAIL_HOST_PASSWORD ? 'text' : 'password'}
                    value={formData.EMAIL_HOST_PASSWORD || ''}
                    onChange={(e) => handleChange('EMAIL_HOST_PASSWORD', e.target.value)}
                    className="input-primary pr-10"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => toggleSensitive('EMAIL_HOST_PASSWORD')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSensitive.EMAIL_HOST_PASSWORD ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Default From Email
              </label>
              <input
                type="email"
                value={formData.DEFAULT_FROM_EMAIL || ''}
                onChange={(e) => handleChange('DEFAULT_FROM_EMAIL', e.target.value)}
                className="input-primary"
                placeholder="noreply@example.com"
              />
            </div>
          </div>
        );

      case 'payment':
        return (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stripe Public Key
                </label>
                <div className="relative">
                  <input
                    type={showSensitive.STRIPE_PUBLIC_KEY ? 'text' : 'password'}
                    value={formData.STRIPE_PUBLIC_KEY || ''}
                    onChange={(e) => handleChange('STRIPE_PUBLIC_KEY', e.target.value)}
                    className="input-primary pr-10"
                    placeholder="pk_test_..."
                  />
                  <button
                    type="button"
                    onClick={() => toggleSensitive('STRIPE_PUBLIC_KEY')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSensitive.STRIPE_PUBLIC_KEY ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stripe Secret Key
                </label>
                <div className="relative">
                  <input
                    type={showSensitive.STRIPE_SECRET_KEY ? 'text' : 'password'}
                    value={formData.STRIPE_SECRET_KEY || ''}
                    onChange={(e) => handleChange('STRIPE_SECRET_KEY', e.target.value)}
                    className="input-primary pr-10"
                    placeholder="sk_test_..."
                  />
                  <button
                    type="button"
                    onClick={() => toggleSensitive('STRIPE_SECRET_KEY')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSensitive.STRIPE_SECRET_KEY ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  PayPal Client ID
                </label>
                <div className="relative">
                  <input
                    type={showSensitive.PAYPAL_CLIENT_ID ? 'text' : 'password'}
                    value={formData.PAYPAL_CLIENT_ID || ''}
                    onChange={(e) => handleChange('PAYPAL_CLIENT_ID', e.target.value)}
                    className="input-primary pr-10"
                    placeholder="client-id"
                  />
                  <button
                    type="button"
                    onClick={() => toggleSensitive('PAYPAL_CLIENT_ID')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSensitive.PAYPAL_CLIENT_ID ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  PayPal Client Secret
                </label>
                <div className="relative">
                  <input
                    type={showSensitive.PAYPAL_CLIENT_SECRET ? 'text' : 'password'}
                    value={formData.PAYPAL_CLIENT_SECRET || ''}
                    onChange={(e) => handleChange('PAYPAL_CLIENT_SECRET', e.target.value)}
                    className="input-primary pr-10"
                    placeholder="client-secret"
                  />
                  <button
                    type="button"
                    onClick={() => toggleSensitive('PAYPAL_CLIENT_SECRET')}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showSensitive.PAYPAL_CLIENT_SECRET ? <HiOutlineEyeOff /> : <HiOutlineEye />}
                  </button>
                </div>
              </div>
            </div>
          </div>
        );

      default:
        return (
          <div className="text-center py-12 text-gray-500">
            Settings for {activeTab} tab coming soon...
          </div>
        );
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
          <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Configure your store settings</p>
        </div>
        
        <button
          onClick={() => dispatch(fetchSettings())}
          className="btn-secondary flex items-center space-x-2"
        >
          <HiOutlineRefresh className="w-4 h-4" />
          <span>Refresh</span>
        </button>
      </motion.div>

      {/* Settings Form */}
      <form onSubmit={handleSubmit}>
        <div className="bg-white rounded-xl shadow-md overflow-hidden">
          {/* Tabs */}
          <div className="border-b overflow-x-auto">
            <div className="flex">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                      activeTab === tab.id
                        ? 'border-primary-600 text-primary-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{tab.name}</span>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Settings Content */}
          <div className="p-6">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
              </div>
            ) : (
              renderSettings()
            )}
          </div>

          {/* Form Actions */}
          <div className="border-t px-6 py-4 bg-gray-50 flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex items-center space-x-2"
            >
              <HiOutlineSave className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </form>

      {/* Info Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-700">
          <strong>Note:</strong> Some settings may require a server restart to take effect.
          Changes to payment and email settings should be tested before going live.
        </p>
      </div>
    </div>
  );
};

// ✅ DEFAULT EXPORT
export default AdminSettings;