import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

const CategoryList = ({ categories }) => {
  const categoryIcons = {
    'Electronics': '📱',
    'Fashion': '👕',
    'Home & Living': '🏠',
    'Books': '📚',
    'Sports': '⚽',
    'Toys': '🧸',
    'Beauty': '💄',
    'Automotive': '🚗',
  };

  const categoryColors = [
    'bg-blue-500',
    'bg-pink-500',
    'bg-green-500',
    'bg-yellow-500',
    'bg-orange-500',
    'bg-purple-500',
    'bg-red-500',
    'bg-indigo-500',
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
      {categories.map((category, index) => (
        <motion.div
          key={category.id}
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: index * 0.05 }}
          whileHover={{ scale: 1.05, y: -5 }}
        >
          <Link
            to={`/category/${category.slug}`}
            className={`block ${categoryColors[index % categoryColors.length]} rounded-2xl p-6 text-center text-white shadow-lg hover:shadow-xl transition-all`}
          >
            <div className="text-5xl mb-3">
              {categoryIcons[category.name] || '📦'}
            </div>
            <h3 className="font-semibold text-lg mb-1">{category.name}</h3>
            <p className="text-sm opacity-90">{category.product_count || 0} Products</p>
          </Link>
        </motion.div>
      ))}
    </div>
  );
};

export default CategoryList;