import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { motion } from 'framer-motion';
import { HiOutlinePlus } from 'react-icons/hi';
import ProductTable from '../../components/admin/ProductTable';
import ProductForm from '../../components/admin/ProductForm';
import { fetchAdminProducts, setProductFilters } from '../../store/adminSlice';

const AdminProducts = () => {
  const dispatch = useDispatch();
  const { products, pagination, filters, loading } = useSelector((state) => state.admin);
  const [showForm, setShowForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    dispatch(fetchAdminProducts(filters));
  }, [dispatch, filters]);

  const handleFilterChange = (newFilters) => {
    dispatch(setProductFilters(newFilters));
  };

  const handleEdit = (product) => {
    setEditingProduct(product);
    setShowForm(true);
  };

  const handleCloseForm = () => {
    setShowForm(false);
    setEditingProduct(null);
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
          <h1 className="text-2xl font-bold text-gray-900">Products</h1>
          <p className="text-gray-600 mt-1">Manage your product inventory</p>
        </div>
        
        <button
          onClick={() => setShowForm(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <HiOutlinePlus className="w-5 h-5" />
          <span>Add Product</span>
        </button>
      </motion.div>

      {/* Product Table */}
      <ProductTable
        products={products}
        pagination={pagination.products}
        filters={filters.products}
        onFilterChange={handleFilterChange}
        onEdit={handleEdit}
        loading={loading}
      />

      {/* Product Form Modal */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onClose={handleCloseForm}
        />
      )}
    </div>
  );
};

export default AdminProducts;