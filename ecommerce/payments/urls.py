"""
URL patterns for Payments module.
Defines all API endpoints for payment processing.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for viewsets
router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'methods', views.SavedPaymentMethodViewSet, basename='payment-method')
router.register(r'refund-requests', views.RefundRequestViewSet, basename='refund-request')
router.register(r'payouts', views.PayoutViewSet, basename='payout')
router.register(r'gateways', views.PaymentGatewayViewSet, basename='gateway')

urlpatterns = [
    # Payment processing endpoints
    path('create-payment-intent/', views.CreatePaymentIntentView.as_view(), name='create-payment-intent'),
    path('confirm-payment/', views.ConfirmPaymentView.as_view(), name='confirm-payment'),
    
    # Webhook endpoint (public)
    path('webhook/<str:gateway_name>/', views.PaymentWebhookView.as_view(), name='payment-webhook'),
    
    # Available payment methods
    path('available-methods/', views.PaymentMethodListView.as_view(), name='available-methods'),
    
    # Statistics (admin only)
    path('stats/', views.TransactionStatsView.as_view(), name='payment-stats'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# URL patterns summary:
# Payment Processing:
# POST   /api/payments/create-payment-intent/           - Create payment intent
# POST   /api/payments/confirm-payment/                 - Confirm payment
# POST   /api/payments/webhook/{gateway}/               - Payment webhook

# Transactions:
# GET    /api/payments/transactions/                     - List transactions
# GET    /api/payments/transactions/{id}/                - Transaction details

# Payment Methods:
# GET    /api/payments/methods/                          - List saved methods
# POST   /api/payments/methods/                          - Save new method
# DELETE /api/payments/methods/{id}/                     - Delete method
# POST   /api/payments/methods/{id}/set_default/         - Set default method

# Refunds:
# GET    /api/payments/refund-requests/                  - List refund requests
# POST   /api/payments/refund-requests/                  - Create refund request
# POST   /api/payments/refund-requests/{id}/approve/     - Approve refund
# POST   /api/payments/refund-requests/{id}/reject/      - Reject refund

# Admin:
# GET    /api/payments/stats/                             - Payment statistics
# GET    /api/payments/gateways/                          - List gateways
# POST   /api/payments/gateways/                          - Add gateway
# GET    /api/payments/payouts/                           - List payouts