import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { 
  HiOutlineStar, 
  HiOutlineHeart, 
  HiOutlineShoppingCart,
  HiOutlineTruck,
  HiOutlineRefresh,
  HiOutlineShieldCheck,
  HiOutlineMinus,
  HiOutlinePlus,
  HiOutlineChevronLeft
} from 'react-icons/hi';
import { fetchProductBySlug } from '../store/productSlice';
import ProductGrid from '../components/products/ProductGrid';
import { productService } from '../services/product';

const ProductDetailPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { currentProduct, relatedProducts, loading } = useSelector((state) => state.products);
  const [quantity, setQuantity] = useState(1);
  const [selectedImage, setSelectedImage] = useState(0);
  const [activeTab, setActiveTab] = useState('description');

  useEffect(() => {
    dispatch(fetchProductBySlug(slug));
     
    
    // Scroll to top
    window.scrollTo(0, 0);
  }, [dispatch, slug]);

  if (loading || !currentProduct) {
    return (
      <div className="min-h-screen flex justify-center items-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-8 h-8 bg-primary-600 rounded-full animate-pulse"></div>
        </div>
      </div>
    );
  }

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
    reviews,
    attributes
  } = currentProduct;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="flex items-center space-x-2 text-sm text-gray-500 mb-6">
          <Link to="/" className="hover:text-primary-600">Home</Link>
          <span>/</span>
          <Link to="/shop" className="hover:text-primary-600">Shop</Link>
          <span>/</span>
          <Link to={`/category/${category?.slug}`} className="hover:text-primary-600">
            {category?.name}
          </Link>
          <span>/</span>
          <span className="text-gray-900">{name}</span>
        </nav>

        {/* Back Button - Mobile */}
        <Link
          to="/shop"
          className="lg:hidden flex items-center text-primary-600 mb-4"
        >
          <HiOutlineChevronLeft className="w-5 h-5" />
          <span>Back to Shop</span>
        </Link>

        {/* Product Main Section */}
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
                    <Link to={`/brand/${brand.slug}`} className="hover:text-primary-600">
                      {brand.name}
                    </Link>
                    <span>•</span>
                  </>
                )}
                <Link to={`/category/${category?.slug}`} className="hover:text-primary-600">
                  {category?.name}
                </Link>
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

        {/* Tabs Section */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg overflow-hidden">
          <div className="border-b">
            <div className="flex">
              <button
                onClick={() => setActiveTab('description')}
                className={`px-6 py-4 font-medium text-sm ${
                  activeTab === 'description'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Description
              </button>
              <button
                onClick={() => setActiveTab('reviews')}
                className={`px-6 py-4 font-medium text-sm ${
                  activeTab === 'reviews'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Reviews ({reviews_count})
              </button>
              <button
                onClick={() => setActiveTab('shipping')}
                className={`px-6 py-4 font-medium text-sm ${
                  activeTab === 'shipping'
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                Shipping Info
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'description' && (
              <div className="prose max-w-none">
                <p className="text-gray-600">{description}</p>
              </div>
            )}

            {activeTab === 'reviews' && (
              <div>
                {reviews && reviews.length > 0 ? (
                  <div className="space-y-6">
                    {reviews.map((review) => (
                      <div key={review.id} className="border-b last:border-0 pb-6">
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <p className="font-semibold">{review.user_name}</p>
                            <div className="flex items-center text-yellow-400">
                              {[...Array(5)].map((_, i) => (
                                <HiOutlineStar
                                  key={i}
                                  className={`w-4 h-4 ${i < review.rating ? 'fill-current' : ''}`}
                                />
                              ))}
                            </div>
                          </div>
                          <p className="text-sm text-gray-500">
                            {new Date(review.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <p className="text-gray-600">{review.content}</p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-center text-gray-500 py-8">No reviews yet.</p>
                )}
              </div>
            )}

            {activeTab === 'shipping' && (
              <div className="space-y-4">
                <h3 className="font-semibold">Delivery Information</h3>
                <ul className="list-disc list-inside text-gray-600 space-y-2">
                  <li>Free shipping on orders over $50</li>
                  <li>Standard delivery: 3-5 business days</li>
                  <li>Express delivery: 1-2 business days ($10 extra)</li>
                  <li>International shipping available to select countries</li>
                </ul>
              </div>
            )}
          </div>
        </div>

        {/* Related Products */}
        {relatedProducts && relatedProducts.length > 0 && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">You May Also Like</h2>
            <ProductGrid products={relatedProducts} />
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductDetailPage;