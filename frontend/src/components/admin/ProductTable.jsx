import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  HiOutlinePencil,
  HiOutlineTrash,
  HiOutlineEye,
  HiOutlineChevronLeft,
  HiOutlineChevronRight,
  HiOutlineSearch,
  HiOutlineFilter
} from 'react-icons/hi';
import { deleteProduct } from '../../store/adminSlice';
import toast from 'react-hot-toast';

const ProductTable = ({ products, pagination, filters, onFilterChange, onEdit, loading }) => {
  const dispatch = useDispatch();
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedProducts(products.map(p => p.id));
    } else {
      setSelectedProducts([]);
    }
  };

  const handleSelectProduct = (productId) => {
    setSelectedProducts(prev => {
      if (prev.includes(productId)) {
        return prev.filter(id => id !== productId);
      } else {
        return [...prev, productId];
      }
    });
  };

  const handleDelete = async (productId) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await dispatch(deleteProduct(productId)).unwrap();
        toast.success('Product deleted successfully');
      } catch (error) {
        toast.error('Failed to delete product');
      }
    }
  };

  const handleBulkDelete = async () => {
    if (selectedProducts.length === 0) return;
    
    if (window.confirm(`Delete ${selectedProducts.length} products?`)) {
      try {
        await Promise.all(selectedProducts.map(id => dispatch(deleteProduct(id)).unwrap()));
        setSelectedProducts([]);
        toast.success('Products deleted successfully');
      } catch (error) {
        toast.error('Failed to delete some products');
      }
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md overflow-hidden">
      {/* Table Header */}
      <div className="p-4 border-b flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h3 className="text-lg font-semibold text-gray-900">Products</h3>
          {selectedProducts.length > 0 && (
            <button
              onClick={handleBulkDelete}
              className="text-sm text-red-600 hover:text-red-700 font-medium"
            >
              Delete Selected ({selectedProducts.length})
            </button>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          {/* Search */}
          <div className="relative">
            <HiOutlineSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              value={filters.search || ''}
              onChange={(e) => onFilterChange({ search: e.target.value, page: 1 })}
              placeholder="Search products..."
              className="pl-10 pr-4 py-2 border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          
          {/* Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`p-2 border rounded-lg hover:bg-gray-50 transition-colors ${
              showFilters ? 'bg-primary-50 text-primary-600 border-primary-300' : ''
            }`}
          >
            <HiOutlineFilter className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="border-b bg-gray-50 overflow-hidden"
          >
            <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <select
                value={filters.category || ''}
                onChange={(e) => onFilterChange({ category: e.target.value, page: 1 })}
                className="input-primary text-sm"
              >
                <option value="">All Categories</option>
                <option value="electronics">Electronics</option>
                <option value="fashion">Fashion</option>
                <option value="home">Home & Living</option>
              </select>
              
              <select
                value={filters.status || ''}
                onChange={(e) => onFilterChange({ status: e.target.value, page: 1 })}
                className="input-primary text-sm"
              >
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="inactive">Inactive</option>
                <option value="draft">Draft</option>
              </select>
              
              <select
                value={filters.stock || ''}
                onChange={(e) => onFilterChange({ stock: e.target.value, page: 1 })}
                className="input-primary text-sm"
              >
                <option value="">All Stock</option>
                <option value="in">In Stock</option>
                <option value="low">Low Stock</option>
                <option value="out">Out of Stock</option>
              </select>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="w-10 px-4 py-3">
                <input
                  type="checkbox"
                  checked={selectedProducts.length === products?.length}
                  onChange={handleSelectAll}
                  className="h-4 w-4 text-primary-600 rounded"
                />
              </th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Product</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">SKU</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Category</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Price</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Stock</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 text-sm font-medium text-gray-600">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {loading ? (
              <tr>
                <td colSpan="8" className="text-center py-8">
                  <div className="flex justify-center">
                    <div className="w-8 h-8 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
                  </div>
                </td>
              </tr>
            ) : products?.length === 0 ? (
              <tr>
                <td colSpan="8" className="text-center py-8 text-gray-500">
                  No products found
                </td>
              </tr>
            ) : (
              products?.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedProducts.includes(product.id)}
                      onChange={() => handleSelectProduct(product.id)}
                      className="h-4 w-4 text-primary-600 rounded"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg overflow-hidden flex-shrink-0">
                        {product.primary_image ? (
                          <img src={product.primary_image} alt={product.name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-gray-400">
                            📦
                          </div>
                        )}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{product.name}</p>
                        <p className="text-xs text-gray-500">ID: {product.id}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{product.sku}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{product.category?.name}</td>
                  <td className="px-4 py-3">
                    <span className="font-medium text-primary-600">${product.current_price}</span>
                    {product.sale_price && (
                      <span className="text-xs text-gray-400 line-through ml-2">${product.regular_price}</span>
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`text-sm ${
                      product.stock_quantity > 10 ? 'text-green-600' :
                      product.stock_quantity > 0 ? 'text-yellow-600' : 'text-red-600'
                    }`}>
                      {product.stock_quantity} units
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      product.status === 'active' ? 'bg-green-100 text-green-700' :
                      product.status === 'inactive' ? 'bg-gray-100 text-gray-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {product.status}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => window.open(`/product/${product.slug}`, '_blank')}
                        className="p-1 text-gray-500 hover:text-primary-600"
                      >
                        <HiOutlineEye className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => onEdit(product)}
                        className="p-1 text-gray-500 hover:text-blue-600"
                      >
                        <HiOutlinePencil className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="p-1 text-gray-500 hover:text-red-600"
                      >
                        <HiOutlineTrash className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination?.count > 0 && (
        <div className="px-4 py-3 border-t flex items-center justify-between">
          <p className="text-sm text-gray-600">
            Showing {((filters.page - 1) * 10) + 1} to {Math.min(filters.page * 10, pagination.count)} of {pagination.count} products
          </p>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={() => onFilterChange({ page: filters.page - 1 })}
              disabled={!pagination.previous}
              className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <HiOutlineChevronLeft className="w-4 h-4" />
            </button>
            
            <span className="px-3 py-1 bg-primary-50 text-primary-600 rounded-lg text-sm">
              Page {filters.page}
            </span>
            
            <button
              onClick={() => onFilterChange({ page: filters.page + 1 })}
              disabled={!pagination.next}
              className="p-2 border rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <HiOutlineChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductTable;