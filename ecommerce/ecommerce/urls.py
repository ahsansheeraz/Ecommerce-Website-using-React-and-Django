"""
Main URL configuration for the project.
Includes all app URLs and API documentation.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI documentation setup
schema_view = get_schema_view(
    openapi.Info(
        title="E-Commerce API Documentation",
        default_version='v1',
        description="Complete API documentation for E-Commerce platform",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@ecommerce.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin panel (custom React admin will be used, Django admin kept for backup)
    path('django-admin/', admin.site.urls),
    
    # API documentation
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/auth/', include('users.urls')),  # Authentication and user management
    path('api/products/', include('products.urls')),  # Product management
    path('api/cart/', include('cart.urls')),  # Shopping cart
    path('api/orders/', include('orders.urls')),  # Orders and checkout
    path('api/payments/', include('payments.urls')),  # Payment processing
    path('api/notifications/', include('notifications.urls')),  # Notifications
    path('api/admin/', include('admin_panel.urls')),  # Custom admin panel APIs
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)