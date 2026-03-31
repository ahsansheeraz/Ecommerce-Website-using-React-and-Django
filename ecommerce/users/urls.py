"""
URL patterns for User module.
"""

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegistrationView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Address management
    path('addresses/', views.AddressListCreateView.as_view(), name='address_list'),
    path('addresses/<uuid:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    
    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/<uuid:product_id>/', views.WishlistDeleteView.as_view(), name='wishlist_delete'),
    
    # Admin endpoints
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/users/<uuid:user_id>/', views.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/<uuid:user_id>/toggle-status/', views.AdminUserToggleStatusView.as_view(), name='admin_user_toggle'),
    path('admin/users/<uuid:user_id>/delete/', views.AdminUserDeleteView.as_view(), name='admin_user_delete'),
]