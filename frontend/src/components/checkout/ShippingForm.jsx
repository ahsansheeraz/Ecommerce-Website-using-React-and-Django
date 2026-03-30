import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import { motion } from 'framer-motion';
import { HiOutlineLocationMarker, HiOutlineUser, HiOutlinePhone, HiOutlineMail } from 'react-icons/hi';
import { fetchAddresses } from '../../store/userSlice';
import { setShippingAddress, setBillingAddress, nextStep } from '../../store/checkoutSlice';

const schema = yup.object({
  saveAddress: yup.boolean(),
  useExistingAddress: yup.boolean(),
  selectedAddressId: yup.string().when('useExistingAddress', {
    is: true,
    then: (schema) => schema.required('Please select an address')
  }),
  name: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('Recipient name is required')
  }),
  phone: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('Phone number is required')
  }),
  address_line1: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('Address line 1 is required')
  }),
  city: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('City is required')
  }),
  state: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('State is required')
  }),
  country: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('Country is required')
  }),
  postal_code: yup.string().when('useExistingAddress', {
    is: false,
    then: (schema) => schema.required('Postal code is required')
  })
});

const ShippingForm = () => {
  const dispatch = useDispatch();
  const { addresses } = useSelector((state) => state.user);
  const { shippingAddress } = useSelector((state) => state.checkout);
  
  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors }
  } = useForm({
    resolver: yupResolver(schema),
    defaultValues: {
      useExistingAddress: false,
      saveAddress: true,
      ...shippingAddress
    }
  });

  const useExistingAddress = watch('useExistingAddress');

  useEffect(() => {
    dispatch(fetchAddresses());
  }, [dispatch]);

  const onSubmit = (data) => {
    let addressData;
    
    if (data.useExistingAddress) {
      const selectedAddress = addresses.find(addr => addr.id === data.selectedAddressId);
      addressData = selectedAddress;
    } else {
      addressData = {
        name: data.name,
        phone: data.phone,
        address_line1: data.address_line1,
        address_line2: data.address_line2 || '',
        city: data.city,
        state: data.state,
        country: data.country,
        postal_code: data.postal_code
      };
    }

    dispatch(setShippingAddress(addressData));
    dispatch(setBillingAddress(addressData)); // Same as shipping for now
    dispatch(nextStep());
  };

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      className="bg-white rounded-xl shadow-lg p-6"
    >
      <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
        <HiOutlineLocationMarker className="w-6 h-6 mr-2 text-primary-600" />
        Shipping Information
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Address Selection Option */}
        {addresses?.length > 0 && (
          <div className="space-y-4">
            <label className="flex items-center space-x-3">
              <input
                type="radio"
                {...register('useExistingAddress')}
                value={false}
                className="h-4 w-4 text-primary-600"
              />
              <span className="text-gray-700">Use new address</span>
            </label>
            
            <label className="flex items-center space-x-3">
              <input
                type="radio"
                {...register('useExistingAddress')}
                value={true}
                className="h-4 w-4 text-primary-600"
              />
              <span className="text-gray-700">Use saved address</span>
            </label>
          </div>
        )}

        {/* Saved Address Selection */}
        {useExistingAddress && addresses?.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-3"
          >
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Address
            </label>
            {addresses.map((address) => (
              <label
                key={address.id}
                className="flex items-start space-x-3 p-4 border rounded-lg cursor-pointer hover:border-primary-300"
              >
                <input
                  type="radio"
                  {...register('selectedAddressId')}
                  value={address.id}
                  className="h-4 w-4 mt-1 text-primary-600"
                />
                <div className="flex-1">
                  <p className="font-medium">{address.name}</p>
                  <p className="text-sm text-gray-600">
                    {address.address_line1}
                    {address.address_line2 && `, ${address.address_line2}`}
                  </p>
                  <p className="text-sm text-gray-600">
                    {address.city}, {address.state} {address.postal_code}
                  </p>
                  <p className="text-sm text-gray-600">{address.country}</p>
                  <p className="text-sm text-gray-600">Phone: {address.phone}</p>
                </div>
              </label>
            ))}
            {errors.selectedAddressId && (
              <p className="text-sm text-red-600">{errors.selectedAddressId.message}</p>
            )}
          </motion.div>
        )}

        {/* New Address Form */}
        {!useExistingAddress && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Recipient Name
                </label>
                <div className="relative">
                  <HiOutlineUser className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    {...register('name')}
                    className={`input-primary pl-10 ${errors.name ? 'border-red-500' : ''}`}
                    placeholder="John Doe"
                  />
                </div>
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Phone Number
                </label>
                <div className="relative">
                  <HiOutlinePhone className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="tel"
                    {...register('phone')}
                    className={`input-primary pl-10 ${errors.phone ? 'border-red-500' : ''}`}
                    placeholder="+1 234 567 8900"
                  />
                </div>
                {errors.phone && (
                  <p className="mt-1 text-sm text-red-600">{errors.phone.message}</p>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address Line 1
              </label>
              <input
                type="text"
                {...register('address_line1')}
                className={`input-primary ${errors.address_line1 ? 'border-red-500' : ''}`}
                placeholder="Street address, P.O. box"
              />
              {errors.address_line1 && (
                <p className="mt-1 text-sm text-red-600">{errors.address_line1.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Address Line 2 (Optional)
              </label>
              <input
                type="text"
                {...register('address_line2')}
                className="input-primary"
                placeholder="Apartment, suite, unit, building"
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  City
                </label>
                <input
                  type="text"
                  {...register('city')}
                  className={`input-primary ${errors.city ? 'border-red-500' : ''}`}
                />
                {errors.city && (
                  <p className="mt-1 text-sm text-red-600">{errors.city.message}</p>
                )}
              </div>

              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  State
                </label>
                <input
                  type="text"
                  {...register('state')}
                  className={`input-primary ${errors.state ? 'border-red-500' : ''}`}
                />
                {errors.state && (
                  <p className="mt-1 text-sm text-red-600">{errors.state.message}</p>
                )}
              </div>

              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Country
                </label>
                <input
                  type="text"
                  {...register('country')}
                  className={`input-primary ${errors.country ? 'border-red-500' : ''}`}
                />
                {errors.country && (
                  <p className="mt-1 text-sm text-red-600">{errors.country.message}</p>
                )}
              </div>

              <div className="col-span-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Postal Code
                </label>
                <input
                  type="text"
                  {...register('postal_code')}
                  className={`input-primary ${errors.postal_code ? 'border-red-500' : ''}`}
                />
                {errors.postal_code && (
                  <p className="mt-1 text-sm text-red-600">{errors.postal_code.message}</p>
                )}
              </div>
            </div>

            {/* Save Address Checkbox */}
            <div className="flex items-center">
              <input
                type="checkbox"
                {...register('saveAddress')}
                className="h-4 w-4 text-primary-600 rounded"
              />
              <label className="ml-2 text-sm text-gray-700">
                Save this address for future orders
              </label>
            </div>
          </motion.div>
        )}

        {/* Form Actions */}
        <div className="flex justify-end space-x-4 pt-4">
          <button type="submit" className="btn-primary">
            Continue to Payment
          </button>
        </div>
      </form>
    </motion.div>
  );
};

export default ShippingForm;