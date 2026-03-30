import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  fetchProducts, 
  fetchCategories, 

  setFilters 
} from '../store/productSlice';
import ProductGrid from '../components/products/ProductGrid';
import ProductFilters from '../components/products/ProductFilters';
import { HiOutlineAdjustments } from 'react-icons/hi';

const ShopPage = () => {
  const dispatch = useDispatch();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const { 
    products, 
    categories, 
    loading, 
    error, 
    filters,
    pagination 
  } = useSelector((state) => state.products);

  // Load categories on mount
  useEffect(() => {
    dispatch(fetchCategories());
    dispatch(fetchBrands());
  }, [dispatch]);

  // Sync URL params with filters
  useEffect(() => {
    const params = {};
    if (filters.category) params.category = filters.category;
    if (filters.brand) params.brand = filters.brand;
    if (filters.minPrice) params.minPrice = filters.minPrice;
    if (filters.maxPrice) params.maxPrice = filters.maxPrice;
    if (filters.sort) params.sort = filters.sort;
    if (filters.page > 1) params.page = filters.page;
    
    setSearchParams(params);
  }, [filters, setSearchParams]);

  // Load products when filters change
  useEffect(() => {
    dispatch(fetchProducts(filters));
  }, [dispatch, filters]);

  const handleFilterChange = (newFilters) => {
    dispatch(setFilters({ ...filters, ...newFilters, page: 1 }));
  };

  const handlePageChange = (newPage) => {
    dispatch(setFilters({ ...filters, page: newPage }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900">Shop All Products</h1>
          <p className="text-gray-600 mt-2">
            {pagination.count} products available
          </p>
        </motion.div>

        {/* Main Content */}
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Filters Sidebar */}
          <div className="lg:w-80">
            <ProductFilters
              filters={filters}
              setFilters={handleFilterChange}
              categories={categories}
            />
          </div>

          {/* Products Grid */}
          <div className="flex-1">
            <ProductGrid 
              products={products} 
              loading={loading} 
              error={error} 
            />

            {/* Pagination */}
            {pagination.count > 0 && (
              <div className="mt-8 flex justify-center">
                <nav className="flex items-center space-x-2">
                  <button
                    onClick={() => handlePageChange(filters.page - 1)}
                    disabled={!pagination.previous}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Previous
                  </button>
                  <span className="px-4 py-2 bg-primary-600 text-white rounded-lg">
                    Page {filters.page}
                  </span>
                  <button
                    onClick={() => handlePageChange(filters.page + 1)}
                    disabled={!pagination.next}
                    className="px-4 py-2 border rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShopPage;