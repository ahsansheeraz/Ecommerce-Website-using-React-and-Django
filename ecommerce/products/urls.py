"""
URL patterns for Product module.
Defines all API endpoints for products, categories, brands, and reviews.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'images', views.ProductImageViewSet, basename='product-image')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')
router.register(r'tags', views.ProductTagViewSet, basename='tag')
router.register(r'attributes', views.ProductAttributeViewSet, basename='attribute')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional search endpoint
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
]

# URL patterns for custom actions:
# Products:
# GET /api/products/ - List all products
# POST /api/products/ - Create product (seller/admin)
# GET /api/products/featured/ - Featured products
# GET /api/products/new-arrivals/ - New arrivals
# GET /api/products/best-sellers/ - Best sellers
# GET /api/products/{slug}/ - Product detail
# POST /api/products/{slug}/add_review/ - Add review
# GET /api/products/{slug}/related_products/ - Related products
# PUT/PATCH /api/products/{slug}/ - Update product
# DELETE /api/products/{slug}/ - Delete product

# Categories:
# GET /api/categories/ - List categories
# GET /api/categories/{slug}/ - Category detail
# GET /api/categories/{slug}/products/ - Products in category

# Brands:
# GET /api/brands/ - List brands
# GET /api/brands/{slug}/ - Brand detail
# GET /api/brands/{slug}/products/ - Products by brand

# Search:
# GET /api/products/search/?search=query&min_price=10&max_price=100&category=electronics