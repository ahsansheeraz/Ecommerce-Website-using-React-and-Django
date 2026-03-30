import React, { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlineChevronLeft } from 'react-icons/hi';
import { fetchProducts, setFilters } from '../store/productSlice';
import ProductGrid from '../components/products/ProductGrid';

const CategoryPage = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { products, loading, error } = useSelector((state) => state.products);

  useEffect(() => {
    // ✅ Category filter ke saath products fetch karo
    dispatch(setFilters({ category: slug }));
    dispatch(fetchProducts({ category: slug }));
  }, [dispatch, slug]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Back Button */}
        <Link
          to="/shop"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6"
        >
          <HiOutlineChevronLeft className="w-5 h-5 mr-1" />
          <span>Back to Shop</span>
        </Link>

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 capitalize">
            {slug.replace(/-/g, ' ')}
          </h1>
          <p className="text-gray-600 mt-2">
            Browse our collection of {slug.replace(/-/g, ' ')} products
          </p>
        </motion.div>

        {/* Products Grid */}
        <ProductGrid products={products} loading={loading} error={error} />
      </div>
    </div>
  );
};

export default CategoryPage;