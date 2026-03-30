"""
URL patterns for Orders module.
Defines all API endpoints for orders, checkout, returns, etc.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for admin viewsets
router = DefaultRouter()
router.register(r'admin/orders', views.AdminOrderViewSet, basename='admin-order')
router.register(r'admin/returns', views.AdminReturnViewSet, basename='admin-return')

urlpatterns = [
    # Checkout and order creation
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    
    # User order endpoints
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<str:order_number>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('<str:order_number>/track/', views.OrderTrackingView.as_view(), name='order-track'),
    path('<str:order_number>/cancel/', views.OrderCancelView.as_view(), name='order-cancel'),
    path('<str:order_number>/return/', views.OrderReturnView.as_view(), name='order-return'),
    path('<str:order_number>/payment/', views.OrderPaymentView.as_view(), name='order-payment'),
    path('<str:order_number>/invoice/', views.OrderInvoiceView.as_view(), name='order-invoice'),
    
    # Admin endpoints
    path('admin/analytics/', views.OrderAnalyticsView.as_view(), name='order-analytics'),
    path('admin/status/<str:order_number>/', views.OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('admin/', include(router.urls)),
]

# URL patterns summary:
# User endpoints:
# POST   /api/orders/checkout/              - Create order from cart
# GET    /api/orders/                        - List user orders
# GET    /api/orders/{order_number}/         - Order details
# GET    /api/orders/{order_number}/track/   - Track order
# POST   /api/orders/{order_number}/cancel/  - Cancel order
# POST   /api/orders/{order_number}/return/  - Return items
# POST   /api/orders/{order_number}/payment/ - Process payment
# GET    /api/orders/{order_number}/invoice/ - Get invoice

# Admin endpoints:
# GET    /api/orders/admin/analytics/        - Order analytics
# POST   /api/orders/admin/status/{order_number}/ - Update status
# GET    /api/orders/admin/orders/           - List all orders (admin)
# GET    /api/orders/admin/orders/{id}/      - Order detail (admin)
# GET    /api/orders/admin/returns/          - List returns
# POST   /api/orders/admin/returns/{id}/approve/ - Approve return
# POST   /api/orders/admin/returns/{id}/reject/   - Reject return