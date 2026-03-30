"""
URL patterns for Admin Panel module.
Defines all API endpoints for admin panel.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router for viewsets
router = DefaultRouter()
router.register(r'widgets', views.DashboardWidgetViewSet, basename='widget')
router.register(r'dashboards', views.AdminDashboardViewSet, basename='dashboard')
router.register(r'logs', views.AdminActivityLogViewSet, basename='log')
router.register(r'settings', views.SystemSettingViewSet, basename='setting')
router.register(r'report-templates', views.ReportTemplateViewSet, basename='report-template')
router.register(r'generated-reports', views.GeneratedReportViewSet, basename='generated-report')
router.register(r'notes', views.AdminNoteViewSet, basename='note')
router.register(r'backups', views.BackupViewSet, basename='backup')
router.register(r'notifications', views.AdminNotificationViewSet, basename='admin-notification')

urlpatterns = [
    # Dashboard
    path('dashboard/summary/', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    
    # Maintenance
    path('maintenance/', views.MaintenanceModeView.as_view(), name='maintenance'),
    
    # System Health
    path('health/', views.SystemHealthView.as_view(), name='system-health'),
    
    # Actions
    path('quick-action/', views.QuickActionView.as_view(), name='quick-action'),
    path('bulk-action/', views.BulkActionView.as_view(), name='bulk-action'),
    
    # Search
    path('search/', views.SearchAllView.as_view(), name='global-search'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# URL patterns summary:
# Dashboard:
# GET    /api/admin/dashboard/summary/                    - Dashboard summary
# GET    /api/admin/dashboards/                            - List dashboards
# GET    /api/admin/dashboards/default/                    - Get default dashboard
# POST   /api/admin/dashboards/                            - Create dashboard
# POST   /api/admin/dashboards/{id}/add_widget/            - Add widget
# POST   /api/admin/dashboards/{id}/remove_widget/         - Remove widget
# POST   /api/admin/dashboards/{id}/reorder_widgets/       - Reorder widgets

# Widgets:
# GET    /api/admin/widgets/                                - List widgets
# POST   /api/admin/widgets/                                - Create widget
# PUT    /api/admin/widgets/{id}/                           - Update widget

# Settings:
# GET    /api/admin/settings/                               - List settings
# GET    /api/admin/settings/by_category/                   - Settings by category
# POST   /api/admin/settings/bulk_update/                   - Bulk update settings
# PUT    /api/admin/settings/{key}/                          - Update setting

# Reports:
# GET    /api/admin/report-templates/                       - List report templates
# POST   /api/admin/report-templates/{id}/generate/         - Generate report
# GET    /api/admin/generated-reports/                      - List generated reports
# POST   /api/admin/generated-reports/{id}/download/        - Download report

# Logs:
# GET    /api/admin/logs/                                    - List activity logs
# GET    /api/admin/logs/?from_date=&to_date=&user_id=      - Filtered logs

# Notes:
# GET    /api/admin/notes/                                   - List notes
# POST   /api/admin/notes/                                   - Create note
# POST   /api/admin/notes/{id}/toggle_pin/                   - Toggle pin
# POST   /api/admin/notes/{id}/share/                        - Share note

# Backups:
# GET    /api/admin/backups/                                 - List backups
# POST   /api/admin/backups/create_backup/                   - Create backup
# POST   /api/admin/backups/{id}/restore/                    - Restore backup
# POST   /api/admin/backups/{id}/download/                   - Download backup

# Maintenance:
# GET    /api/admin/maintenance/                             - Get status
# POST   /api/admin/maintenance/                             - Update maintenance
# DELETE /api/admin/maintenance/                              - Disable maintenance

# Notifications:
# GET    /api/admin/notifications/                           - List notifications
# POST   /api/admin/notifications/                           - Create notification
# POST   /api/admin/notifications/{id}/dismiss/              - Dismiss notification

# System Health:
# GET    /api/admin/health/                                   - Get health status
# POST   /api/admin/health/                                   - Run health check

# Actions:
# POST   /api/admin/quick-action/                             - Quick actions
# POST   /api/admin/bulk-action/                              - Bulk actions

# Search:
# GET    /api/admin/search/?q=query                           - Global search