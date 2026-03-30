"""
Django admin configuration for Admin Panel module.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    DashboardWidget, AdminDashboard, DashboardWidgetPlacement,
    AdminActivityLog, SystemSetting, ReportTemplate, GeneratedReport,
    AdminNote, BackupLog, MaintenanceMode, AdminNotification, SystemHealth
)


@admin.register(DashboardWidget)
class DashboardWidgetAdmin(admin.ModelAdmin):
    """Admin configuration for DashboardWidget."""
    
    list_display = ['name', 'widget_type', 'size', 'order', 'is_active', 'is_default']
    list_filter = ['widget_type', 'size', 'is_active', 'is_default']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminDashboard)
class AdminDashboardAdmin(admin.ModelAdmin):
    """Admin configuration for AdminDashboard."""
    
    list_display = ['name', 'user', 'is_default', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    """Admin configuration for AdminActivityLog."""
    
    list_display = ['admin', 'action', 'object_repr', 'status', 'created_at']
    list_filter = ['action', 'status', 'created_at']
    search_fields = ['admin__email', 'object_repr', 'details']
    readonly_fields = ['created_at', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    """Admin configuration for SystemSetting."""
    
    list_display = ['key', 'label', 'category', 'value_type', 'is_editable']
    list_filter = ['category', 'value_type', 'is_editable']
    search_fields = ['key', 'label', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for ReportTemplate."""
    
    list_display = ['name', 'report_type', 'is_active', 'is_system', 'created_at']
    list_filter = ['report_type', 'is_active', 'is_system']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    """Admin configuration for GeneratedReport."""
    
    list_display = ['name', 'template', 'status', 'row_count', 'created_at', 'download_link']
    list_filter = ['status', 'file_format', 'created_at']
    search_fields = ['name', 'template__name']
    readonly_fields = ['created_at', 'completed_at', 'file_size']
    
    def download_link(self, obj):
        """Link to download report."""
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return '-'
    download_link.short_description = 'Download'


@admin.register(AdminNote)
class AdminNoteAdmin(admin.ModelAdmin):
    """Admin configuration for AdminNote."""
    
    list_display = ['title', 'admin', 'color', 'is_private', 'is_pinned', 'created_at']
    list_filter = ['color', 'is_private', 'is_pinned', 'created_at']
    search_fields = ['title', 'content', 'admin__email']
    readonly_fields = ['created_at', 'updated_at']
    filter_horizontal = ['shared_with']


@admin.register(BackupLog)
class BackupLogAdmin(admin.ModelAdmin):
    """Admin configuration for BackupLog."""
    
    list_display = ['name', 'backup_type', 'status', 'file_size', 'created_at', 'download_link']
    list_filter = ['backup_type', 'status', 'created_at']
    search_fields = ['name', 'notes']
    readonly_fields = ['created_at', 'completed_at', 'file_size']
    
    def download_link(self, obj):
        """Link to download backup."""
        if obj.file:
            return format_html('<a href="{}" target="_blank">Download</a>', obj.file.url)
        return '-'
    download_link.short_description = 'Download'


@admin.register(MaintenanceMode)
class MaintenanceModeAdmin(admin.ModelAdmin):
    """Admin configuration for MaintenanceMode."""
    
    list_display = ['is_active', 'title', 'start_time', 'end_time', 'enabled_by']
    list_filter = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AdminNotification)
class AdminNotificationAdmin(admin.ModelAdmin):
    """Admin configuration for AdminNotification."""
    
    list_display = ['title', 'priority', 'for_all_admins', 'expires_at', 'created_at']
    list_filter = ['priority', 'for_all_admins', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at']
    filter_horizontal = ['specific_admins', 'dismissed_by']


@admin.register(SystemHealth)
class SystemHealthAdmin(admin.ModelAdmin):
    """Admin configuration for SystemHealth."""
    
    list_display = ['component', 'status', 'response_time', 'error_rate', 'checked_at']
    list_filter = ['component', 'status']
    readonly_fields = ['checked_at']