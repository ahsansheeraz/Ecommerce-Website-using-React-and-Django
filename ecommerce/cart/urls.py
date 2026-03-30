"""
URL patterns for Cart module.
Defines all API endpoints for cart operations.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for admin viewsets
router = DefaultRouter()
router.register(r'admin/coupons', views.CouponAdminViewSet, basename='admin-coupon')

urlpatterns = [
    # Cart endpoints
    path('', views.CartView.as_view(), name='cart-detail'),
    path('summary/', views.CartSummaryView.as_view(), name='cart-summary'),
    path('merge/', views.CartMergeView.as_view(), name='cart-merge'),
    
    # Cart items endpoints
    path('items/add/', views.CartItemAddView.as_view(), name='cart-item-add'),
    path('items/<uuid:item_id>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    path('items/<uuid:item_id>/move-to-saved/', views.CartItemMoveToSavedView.as_view(), name='cart-item-move-to-saved'),
    
    # Saved for later endpoints
    path('saved/', views.SavedForLaterView.as_view(), name='saved-list'),
    path('saved/<uuid:pk>/', views.SavedForLaterDetailView.as_view(), name='saved-detail'),
    path('saved/<uuid:item_id>/move-to-cart/', views.SavedForLaterMoveToCartView.as_view(), name='saved-move-to-cart'),
    
    # Coupon endpoints
    path('coupons/apply/', views.CouponApplyView.as_view(), name='coupon-apply'),
    path('coupons/remove/', views.CouponRemoveView.as_view(), name='coupon-remove'),
    path('coupons/available/', views.CouponListView.as_view(), name='coupon-list'),
    
    # Admin endpoints
    path('admin/carts/', views.CartAdminView.as_view(), name='admin-carts'),
    path('admin/', include(router.urls)),
]

# URL patterns summary:
# GET /api/cart/ - Get current cart
# DELETE /api/cart/ - Clear cart
# GET /api/cart/summary/ - Get cart summary
# POST /api/cart/merge/ - Merge guest cart after login
# POST /api/cart/items/add/ - Add item to cart
# PUT /api/cart/items/{item_id}/ - Update item quantity
# DELETE /api/cart/items/{item_id}/ - Remove item
# POST /api/cart/items/{item_id}/move-to-saved/ - Move item to saved
# GET /api/cart/saved/ - List saved items
# POST /api/cart/saved/ - Add to saved
# DELETE /api/cart/saved/{id}/ - Remove saved
# POST /api/cart/saved/{item_id}/move-to-cart/ - Move saved to cart
# POST /api/cart/coupons/apply/ - Apply coupon
# DELETE /api/cart/coupons/remove/?code=CODE - Remove coupon
# GET /api/cart/coupons/available/ - List available coupons