"""
URL patterns for Notifications module.
Defines all API endpoints for notifications.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for viewsets
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'announcements', views.AnnouncementViewSet, basename='announcement')
router.register(r'devices', views.UserDeviceViewSet, basename='device')
router.register(r'templates', views.NotificationTemplateViewSet, basename='template')
router.register(r'logs/(?P<log_type>email|sms|push)', views.NotificationLogViewSet, basename='logs')

urlpatterns = [
    # Notification preferences
    path('preferences/', views.NotificationPreferenceView.as_view(), name='preferences'),
    
    # Notification types
    path('types/', views.NotificationTypeListView.as_view(), name='notification-types'),
    
    # Bulk notifications (admin only)
    path('bulk/', views.BulkNotificationView.as_view(), name='bulk-notification'),
    
    # Test notifications (admin only)
    path('test/', views.TestNotificationView.as_view(), name='test-notification'),
    
    # Statistics (admin only)
    path('stats/', views.NotificationStatsView.as_view(), name='notification-stats'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# URL patterns summary:
# User endpoints:
# GET    /api/notifications/                          - List notifications
# GET    /api/notifications/{id}/                     - Notification detail
# POST   /api/notifications/mark_read/                - Mark notifications as read
# GET    /api/notifications/unread_count/             - Get unread count
# GET    /api/notifications/types/                     - List notification types
# GET    /api/notifications/preferences/               - Get preferences
# PUT    /api/notifications/preferences/               - Update preferences
# GET    /api/notifications/announcements/             - List announcements
# GET    /api/notifications/announcements/{id}/        - Announcement detail
# POST   /api/notifications/devices/                    - Register device
# DELETE /api/notifications/devices/unregister/         - Unregister device

# Admin endpoints:
# POST   /api/notifications/bulk/                       - Bulk notifications
# POST   /api/notifications/test/                       - Test notification
# GET    /api/notifications/stats/                       - Notification stats
# GET    /api/notifications/templates/                   - List templates
# POST   /api/notifications/templates/                   - Create template
# GET    /api/notifications/logs/email/                   - Email logs
# GET    /api/notifications/logs/sms/                     - SMS logs
# GET    /api/notifications/logs/push/                    - Push logs