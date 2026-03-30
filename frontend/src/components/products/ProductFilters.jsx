import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HiOutlineFilter, HiOutlineX, HiOutlineSearch } from 'react-icons/hi';

const ProductFilters = ({ filters, setFilters, categories, brands }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [priceRange, setPriceRange] = useState({
    min: filters.minPrice || '',
    max: filters.maxPrice || '',
  });

  const sortOptions = [
    { value: '-created_at', label: 'Newest First' },
    { value: 'created_at', label: 'Oldest First' },
    { value: '-regular_price', label: 'Price: High to Low' },
    { value: 'regular_price', label: 'Price: Low to High' },
    { value: '-sold_count', label: 'Best Selling' },
    { value: '-average_rating', label: 'Top Rated' },
  ];

  const handleFilterChange = (key, value) => {
    setFilters({ [key]: value });
  };

  const handlePriceChange = (type, value) => {
    const newRange = { ...priceRange, [type]: value };
    setPriceRange(newRange);
    
    if (newRange.min && newRange.max) {
      setFilters({ minPrice: newRange.min, maxPrice: newRange.max });
    }
  };

  const clearFilters = () => {
    setPriceRange({ min: '', max: '' });
    setFilters({
      category: '',
      brand: '',
      minPrice: '',
      maxPrice: '',
      sort: '-created_at',
    });
  };

  return (
    <>
      {/* Mobile Filter Button */}
      <button
        onClick={() => setIsOpen(true)}
        className="lg:hidden fixed bottom-4 right-4 z-40 bg-primary-600 text-white p-4 rounded-full shadow-lg"
      >
        <HiOutlineFilter className="w-6 h-6" />
      </button>

      {/* Filter Sidebar */}
      <AnimatePresence>
        {(isOpen || window.innerWidth >= 1024) && (
          <motion.div
            initial={{ x: -300 }}
            animate={{ x: 0 }}
            exit={{ x: -300 }}
            className={`fixed lg:static inset-y-0 left-0 z-50 w-80 bg-white shadow-lg lg:shadow-none p-6 overflow-y-auto ${isOpen ? 'block' : 'hidden lg:block'}`}
          >
            {/* Header */}
            <div className="flex justify-between items-center mb-6">
              <h3 className="text-lg font-semibold flex items-center">
                <HiOutlineFilter className="mr-2" /> Filters
              </h3>
              <button
                onClick={() => setIsOpen(false)}
                className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
              >
                <HiOutlineX className="w-5 h-5" />
              </button>
            </div>

            {/* Sort By */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Sort By
              </label>
              <select
                value={filters.sort || '-created_at'}
                onChange={(e) => handleFilterChange('sort', e.target.value)}
                className="input-primary"
              >
                {sortOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Categories */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Category
              </label>
              <select
                value={filters.category || ''}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="input-primary"
              >
                <option value="">All Categories</option>
                {categories?.map((category) => (
                  <option key={category.id} value={category.slug}>
                    {category.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Brands */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Brand
              </label>
              <select
                value={filters.brand || ''}
                onChange={(e) => handleFilterChange('brand', e.target.value)}
                className="input-primary"
              >
                <option value="">All Brands</option>
                {brands?.map((brand) => (
                  <option key={brand.id} value={brand.slug}>
                    {brand.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Price Range */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price Range
              </label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  placeholder="Min"
                  value={priceRange.min}
                  onChange={(e) => handlePriceChange('min', e.target.value)}
                  className="input-primary"
                />
                <span>-</span>
                <input
                  type="number"
                  placeholder="Max"
                  value={priceRange.max}
                  onChange={(e) => handlePriceChange('max', e.target.value)}
                  className="input-primary"
                />
              </div>
            </div>

            {/* In Stock Only */}
            <div className="mb-6">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={filters.inStock || false}
                  onChange={(e) => handleFilterChange('inStock', e.target.checked)}
                  className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                />
                <span className="ml-2 text-sm text-gray-700">In Stock Only</span>
              </label>
            </div>

            {/* Clear Filters */}
            <button
              onClick={clearFilters}
              className="w-full btn-secondary"
            >
              Clear All Filters
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default ProductFilters;