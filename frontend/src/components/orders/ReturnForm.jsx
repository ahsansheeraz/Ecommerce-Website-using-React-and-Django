import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { useForm } from 'react-hook-form';
import { motion } from 'framer-motion';
import { HiOutlineRefresh, HiOutlineCamera } from 'react-icons/hi';
import { returnOrder } from '../../store/orderSlice';
import toast from 'react-hot-toast';

const ReturnForm = ({ order }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const [selectedItems, setSelectedItems] = useState([]);
  const [images, setImages] = useState([]);
  const [submitting, setSubmitting] = useState(false);

  const { register, handleSubmit, formState: { errors } } = useForm();

  const handleItemSelect = (itemId) => {
    setSelectedItems(prev => {
      if (prev.includes(itemId)) {
        return prev.filter(id => id !== itemId);
      } else {
        return [...prev, itemId];
      }
    });
  };

  const handleImageUpload = (e) => {
    const files = Array.from(e.target.files);
    // In a real app, you'd upload these to a server
    // For now, we'll just create object URLs
    const newImages = files.map(file => URL.createObjectURL(file));
    setImages(prev => [...prev, ...newImages]);
  };

  const onSubmit = async (data) => {
    if (selectedItems.length === 0) {
      toast.error('Please select at least one item to return');
      return;
    }

    setSubmitting(true);
    try {
      await dispatch(returnOrder({
        orderNumber: order.order_number,
        returnData: {
          order_item_id: selectedItems[0], // For single item returns
          reason: data.reason,
          reason_details: data.reason_details,
          images: [], // Would be URLs from uploaded images
          is_exchange: data.is_exchange || false
        }
      })).unwrap();
      
      toast.success('Return request submitted successfully');
      navigate(`/orders/${order.order_number}`);
    } catch (error) {
      toast.error('Failed to submit return request');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-lg overflow-hidden"
    >
      <div className="bg-gradient-to-r from-primary-600 to-primary-800 px-6 py-4">
        <h2 className="text-xl font-bold text-white flex items-center">
          <HiOutlineRefresh className="w-5 h-5 mr-2" />
          Return Request
        </h2>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="p-6 space-y-6">
        {/* Select Items */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Select Items to Return
          </label>
          <div className="space-y-3">
            {order.items?.map((item) => (
              <label
                key={item.id}
                className={`flex items-start space-x-3 p-4 border rounded-lg cursor-pointer transition-all ${
                  selectedItems.includes(item.id)
                    ? 'border-primary-600 bg-primary-50'
                    : 'hover:border-primary-300'
                }`}
              >
                <input
                  type="checkbox"
                  checked={selectedItems.includes(item.id)}
                  onChange={() => handleItemSelect(item.id)}
                  className="h-4 w-4 mt-1 text-primary-600 rounded"
                />
                <div className="flex-1">
                  <div className="flex items-start space-x-3">
                    <div className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                      {item.product_image ? (
                        <img src={item.product_image} alt={item.product_name} className="w-full h-full object-cover" />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-gray-400">
                          📦
                        </div>
                      )}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{item.product_name}</p>
                      <p className="text-sm text-gray-500">SKU: {item.product_sku}</p>
                      <p className="text-sm text-gray-600 mt-1">Quantity: {item.quantity}</p>
                      <p className="text-sm font-medium text-primary-600 mt-1">
                        ${item.unit_price} each
                      </p>
                    </div>
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Return Reason */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Return Reason
          </label>
          <select
            {...register('reason', { required: 'Please select a reason' })}
            className={`input-primary ${errors.reason ? 'border-red-500' : ''}`}
          >
            <option value="">Select a reason</option>
            <option value="defective">Defective Product</option>
            <option value="wrong_item">Wrong Item Shipped</option>
            <option value="size_issue">Size Issue</option>
            <option value="changed_mind">Changed Mind</option>
            <option value="quality_issue">Quality Issue</option>
            <option value="damaged">Damaged in Transit</option>
            <option value="other">Other</option>
          </select>
          {errors.reason && (
            <p className="mt-1 text-sm text-red-600">{errors.reason.message}</p>
          )}
        </div>

        {/* Reason Details */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Additional Details
          </label>
          <textarea
            {...register('reason_details')}
            rows="4"
            className="input-primary"
            placeholder="Please provide more information about the issue..."
          />
        </div>

        {/* Upload Images */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Upload Images (Optional)
          </label>
          <div className="flex items-center space-x-4">
            <label className="cursor-pointer">
              <input
                type="file"
                multiple
                accept="image/*"
                onChange={handleImageUpload}
                className="hidden"
              />
              <div className="flex items-center space-x-2 px-4 py-2 border rounded-lg hover:bg-gray-50">
                <HiOutlineCamera className="w-5 h-5 text-gray-500" />
                <span className="text-sm text-gray-600">Add Photos</span>
              </div>
            </label>
            <span className="text-xs text-gray-500">
              You can upload up to 5 images
            </span>
          </div>

          {/* Image Preview */}
          {images.length > 0 && (
            <div className="flex space-x-2 mt-3">
              {images.map((image, index) => (
                <div key={index} className="relative">
                  <img
                    src={image}
                    alt={`Preview ${index + 1}`}
                    className="w-16 h-16 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => setImages(images.filter((_, i) => i !== index))}
                    className="absolute -top-1 -right-1 bg-red-500 text-white rounded-full w-5 h-5 flex items-center justify-center text-xs"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Exchange Option */}
        <div className="flex items-center">
          <input
            type="checkbox"
            {...register('is_exchange')}
            className="h-4 w-4 text-primary-600 rounded"
          />
          <label className="ml-2 text-sm text-gray-700">
            I want to exchange this item instead of refund
          </label>
        </div>

        {/* Submit Button */}
        <div className="flex space-x-4 pt-4">
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="flex-1 btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={submitting || selectedItems.length === 0}
            className="flex-1 btn-primary disabled:opacity-50"
          >
            {submitting ? 'Submitting...' : 'Submit Return Request'}
          </button>
        </div>

        {/* Return Policy */}
        <p className="text-xs text-center text-gray-500 mt-4">
          By submitting this request, you agree to our{' '}
          <a href="/return-policy" className="text-primary-600 hover:underline">
            Return Policy
          </a>
        </p>
      </form>
    </motion.div>
  );
};

export default ReturnForm;