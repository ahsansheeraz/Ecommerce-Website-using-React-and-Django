from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'brands', views.BrandViewSet, basename='brand')
router.register(r'products', views.ProductViewSet, basename='product')  # ✅ This is correct
router.register(r'images', views.ProductImageViewSet, basename='product-image')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')
router.register(r'tags', views.ProductTagViewSet, basename='tag')
router.register(r'attributes', views.ProductAttributeViewSet, basename='attribute')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', views.ProductSearchView.as_view(), name='product-search'),
]