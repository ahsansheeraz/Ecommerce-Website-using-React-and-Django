import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  HiOutlineStar, 
  HiOutlineHeart, 
  HiOutlineShoppingCart,
  HiOutlineTruck,
  HiOutlineRefresh,
  HiOutlineShieldCheck,
  HiOutlineMinus,
  HiOutlinePlus 
} from 'react-icons/hi';

const ProductDetails = ({ product }) => {
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);

  const {
    name,
    description,
    regular_price,
    sale_price,
    current_price,
    discount_percentage,
    images,
    brand,
    category,
    sku,
    stock_quantity,
    in_stock,
    average_rating,
    reviews_count,
    attributes
  } = product;

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 p-6 lg:p-10">
        {/* Product Images */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden mb-4">
            {images && images.length > 0 ? (
              <img
                src={images[selectedImage]?.image_url}
                alt={name}
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No Image Available
              </div>
            )}
          </div>

          {/* Thumbnails */}
          {images && images.length > 1 && (
            <div className="grid grid-cols-5 gap-2">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`aspect-square bg-gray-100 rounded-lg overflow-hidden border-2 transition-all ${
                    selectedImage === index 
                      ? 'border-primary-600 scale-105' 
                      : 'border-transparent hover:border-primary-300'
                  }`}
                >
                  <img
                    src={image.image_url}
                    alt={`${name} ${index + 1}`}
                    className="w-full h-full object-cover"
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div>
          {/* Brand & Category */}
          <div className="flex items-center space-x-2 text-sm text-gray-500 mb-2">
            {brand && (
              <>
                <span className="hover:text-primary-600 cursor-pointer">
                  {brand.name}
                </span>
                <span>•</span>
              </>
            )}
            <span className="hover:text-primary-600 cursor-pointer">
              {category?.name}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{name}</h1>

          {/* Rating */}
          <div className="flex items-center mb-4">
            <div className="flex items-center text-yellow-400">
              {[...Array(5)].map((_, i) => (
                <HiOutlineStar
                  key={i}
                  className={`w-5 h-5 ${i < Math.floor(average_rating) ? 'fill-current' : ''}`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-500 ml-2">
              {average_rating} out of 5 ({reviews_count} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="mb-6">
            {sale_price ? (
              <div className="flex items-center space-x-3">
                <span className="text-3xl font-bold text-primary-600">
                  ${current_price}
                </span>
                <span className="text-xl text-gray-400 line-through">
                  ${regular_price}
                </span>
                <span className="bg-red-500 text-white text-sm font-bold px-2 py-1 rounded">
                  Save {discount_percentage}%
                </span>
              </div>
            ) : (
              <span className="text-3xl font-bold text-primary-600">
                ${regular_price}
              </span>
            )}
          </div>

          {/* SKU & Stock */}
          <div className="space-y-2 mb-6">
            <p className="text-sm text-gray-600">
              <span className="font-medium">SKU:</span> {sku}
            </p>
            <p className="text-sm text-gray-600">
              <span className="font-medium">Availability:</span>{' '}
              {in_stock ? (
                <span className="text-green-600">
                  In Stock ({stock_quantity} available)
                </span>
              ) : (
                <span className="text-red-600">Out of Stock</span>
              )}
            </p>
          </div>

          {/* Short Description */}
          <p className="text-gray-600 mb-6">{description?.substring(0, 200)}...</p>

          {/* Attributes */}
          {attributes && Object.keys(attributes).length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Options</h3>
              {Object.entries(attributes).map(([key, value]) => (
                <div key={key} className="mb-3">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    {key}
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {value.values.map((option) => (
                      <button
                        key={option.id}
                        className="px-4 py-2 border rounded-lg hover:border-primary-600 hover:text-primary-600 transition-colors"
                      >
                        {option.value}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Quantity */}
          <div className="flex items-center space-x-4 mb-6">
            <span className="font-medium text-gray-700">Quantity:</span>
            <div className="flex items-center border rounded-lg">
              <button
                onClick={() => setQuantity(Math.max(1, quantity - 1))}
                className="p-2 hover:bg-gray-100"
              >
                <HiOutlineMinus className="w-4 h-4" />
              </button>
              <span className="w-12 text-center">{quantity}</span>
              <button
                onClick={() => setQuantity(quantity + 1)}
                className="p-2 hover:bg-gray-100"
              >
                <HiOutlinePlus className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <button 
              className="flex-1 btn-primary flex items-center justify-center space-x-2"
              disabled={!in_stock}
            >
              <HiOutlineShoppingCart className="w-5 h-5" />
              <span>Add to Cart</span>
            </button>
            <button className="flex-1 btn-secondary flex items-center justify-center space-x-2">
              <HiOutlineHeart className="w-5 h-5" />
              <span>Add to Wishlist</span>
            </button>
          </div>

          {/* Features */}
          <div className="grid grid-cols-2 gap-4 pt-6 border-t">
            <div className="flex items-center space-x-2">
              <HiOutlineTruck className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">Free Shipping</span>
            </div>
            <div className="flex items-center space-x-2">
              <HiOutlineRefresh className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">30 Day Returns</span>
            </div>
            <div className="flex items-center space-x-2">
              <HiOutlineShieldCheck className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">Secure Payment</span>
            </div>
            <div className="flex items-center space-x-2">
              <HiOutlineStar className="w-5 h-5 text-primary-600" />
              <span className="text-sm text-gray-600">1 Year Warranty</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetails;