import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { HiOutlineStar, HiOutlineUser } from 'react-icons/hi';

const ProductReviews = ({ reviews, averageRating, totalReviews, onAddReview }) => {
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [newReview, setNewReview] = useState({
    title: '',
    content: '',
    rating: 5,
    pros: '',
    cons: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAddReview(newReview);
    setShowReviewForm(false);
    setNewReview({
      title: '',
      content: '',
      rating: 5,
      pros: '',
      cons: ''
    });
  };

  const ratingDistribution = [5, 4, 3, 2, 1].map(stars => ({
    stars,
    count: reviews?.filter(r => r.rating === stars).length || 0,
    percentage: totalReviews ? ((reviews?.filter(r => r.rating === stars).length / totalReviews) * 100) : 0
  }));

  return (
    <div className="bg-white rounded-2xl shadow-lg overflow-hidden p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Customer Reviews</h2>
        <button
          onClick={() => setShowReviewForm(!showReviewForm)}
          className="btn-primary"
        >
          Write a Review
        </button>
      </div>

      {/* Rating Summary */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
        {/* Average Rating */}
        <div className="text-center">
          <div className="text-5xl font-bold text-primary-600 mb-2">
            {averageRating}
          </div>
          <div className="flex items-center justify-center text-yellow-400 mb-2">
            {[...Array(5)].map((_, i) => (
              <HiOutlineStar
                key={i}
                className={`w-6 h-6 ${i < Math.floor(averageRating) ? 'fill-current' : ''}`}
              />
            ))}
          </div>
          <p className="text-gray-600">Based on {totalReviews} reviews</p>
        </div>

        {/* Rating Bars */}
        <div className="md:col-span-2 space-y-2">
          {ratingDistribution.map(({ stars, count, percentage }) => (
            <div key={stars} className="flex items-center space-x-2">
              <span className="text-sm text-gray-600 w-12">{stars} stars</span>
              <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-yellow-400 rounded-full"
                  style={{ width: `${percentage}%` }}
                />
              </div>
              <span className="text-sm text-gray-600 w-12">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Review Form */}
      {showReviewForm && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 p-6 border-2 border-primary-200 rounded-xl"
        >
          <h3 className="text-lg font-semibold mb-4">Write Your Review</h3>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating
              </label>
              <div className="flex items-center space-x-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setNewReview({ ...newReview, rating: star })}
                    className="focus:outline-none"
                  >
                    <HiOutlineStar
                      className={`w-8 h-8 ${
                        star <= newReview.rating
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Title
              </label>
              <input
                type="text"
                value={newReview.title}
                onChange={(e) => setNewReview({ ...newReview, title: e.target.value })}
                className="input-primary"
                placeholder="Summarize your experience"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Review Content
              </label>
              <textarea
                value={newReview.content}
                onChange={(e) => setNewReview({ ...newReview, content: e.target.value })}
                className="input-primary min-h-[100px]"
                placeholder="Tell us about your experience with this product"
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pros (Optional)
                </label>
                <input
                  type="text"
                  value={newReview.pros}
                  onChange={(e) => setNewReview({ ...newReview, pros: e.target.value })}
                  className="input-primary"
                  placeholder="What did you like?"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cons (Optional)
                </label>
                <input
                  type="text"
                  value={newReview.cons}
                  onChange={(e) => setNewReview({ ...newReview, cons: e.target.value })}
                  className="input-primary"
                  placeholder="What could be better?"
                />
              </div>
            </div>

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button type="submit" className="btn-primary">
                Submit Review
              </button>
            </div>
          </form>
        </motion.div>
      )}

      {/* Reviews List */}
      <div className="space-y-6">
        {reviews && reviews.length > 0 ? (
          reviews.map((review) => (
            <motion.div
              key={review.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="border-b last:border-0 pb-6"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                    <HiOutlineUser className="w-5 h-5 text-primary-600" />
                  </div>
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
                </div>
                <p className="text-sm text-gray-500">
                  {new Date(review.created_at).toLocaleDateString()}
                </p>
              </div>
              
              <h4 className="font-semibold text-gray-900 mb-2">{review.title}</h4>
              <p className="text-gray-600 mb-3">{review.content}</p>
              
              {(review.pros || review.cons) && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                  {review.pros && (
                    <div className="bg-green-50 p-3 rounded-lg">
                      <p className="text-sm font-medium text-green-700 mb-1">Pros</p>
                      <p className="text-sm text-green-600">{review.pros}</p>
                    </div>
                  )}
                  {review.cons && (
                    <div className="bg-red-50 p-3 rounded-lg">
                      <p className="text-sm font-medium text-red-700 mb-1">Cons</p>
                      <p className="text-sm text-red-600">{review.cons}</p>
                    </div>
                  )}
                </div>
              )}

              {/* Helpful Buttons */}
              <div className="flex items-center space-x-4 mt-3">
                <button className="text-sm text-gray-500 hover:text-primary-600">
                  Helpful ({review.helpful_count || 0})
                </button>
                <button className="text-sm text-gray-500 hover:text-primary-600">
                  Report
                </button>
              </div>
            </motion.div>
          ))
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500">No reviews yet. Be the first to review this product!</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProductReviews;