"""
Django admin configuration for Notifications module.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Notification, NotificationType, NotificationPreference,
    NotificationTemplate, Announcement, UserDevice,
    EmailLog, SMSLog, PushNotificationLog, NotificationStats
)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationType."""
    
    list_display = ['code', 'name', 'category', 'priority', 'is_active']
    list_filter = ['category', 'priority', 'is_active']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification."""
    
    list_display = ['title', 'user_email', 'notification_type', 'priority', 'status', 'created_at']
    list_filter = ['priority', 'status', 'channel', 'notification_type', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'sent_at', 'delivered_at', 'read_at']
    raw_id_fields = ['user', 'content_type']
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Get user email."""
        return obj.user.email if obj.user else obj.user_type
    user_email.short_description = 'Recipient'
    user_email.admin_order_field = 'user__email'
    
    actions = ['mark_as_read', 'resend']
    
    def mark_as_read(self, request, queryset):
        """Mark notifications as read."""
        queryset.update(status='read', read_at=timezone.now())
    mark_as_read.short_description = "Mark selected as read"
    
    def resend(self, request, queryset):
        """Resend notifications."""
        for notification in queryset:
            # TODO: Implement resend logic
            pass
    resend.short_description = "Resend selected"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationPreference."""
    
    list_display = ['user', 'email_frequency', 'email_opt_out', 'sms_opt_out', 'push_opt_out']
    list_filter = ['email_frequency', 'email_opt_out', 'sms_opt_out', 'push_opt_out']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationTemplate."""
    
    list_display = ['notification_type', 'language', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['notification_type__name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin configuration for Announcement."""
    
    list_display = ['title', 'priority', 'audience', 'is_active', 'show_from', 'show_until', 'views_count']
    list_filter = ['priority', 'audience', 'is_active', 'show_from']
    search_fields = ['title', 'message']
    readonly_fields = ['views_count', 'clicks_count', 'created_at', 'updated_at']
    filter_horizontal = ['specific_users']
    date_hierarchy = 'show_from'
    
    actions = ['activate', 'deactivate']
    
    def activate(self, request, queryset):
        """Activate announcements."""
        queryset.update(is_active=True)
    activate.short_description = "Activate selected"
    
    def deactivate(self, request, queryset):
        """Deactivate announcements."""
        queryset.update(is_active=False)
    deactivate.short_description = "Deactivate selected"


@admin.register(UserDevice)
class UserDeviceAdmin(admin.ModelAdmin):
    """Admin configuration for UserDevice."""
    
    list_display = ['user', 'device_name', 'device_type', 'is_active', 'last_active_at']
    list_filter = ['device_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'device_name', 'push_token']
    readonly_fields = ['created_at', 'last_active_at']


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """Admin configuration for EmailLog."""
    
    list_display = ['recipient_email', 'subject', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['recipient_email', 'subject', 'provider_message_id']
    readonly_fields = ['html_content', 'text_content', 'provider_response', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(SMSLog)
class SMSLogAdmin(admin.ModelAdmin):
    """Admin configuration for SMSLog."""
    
    list_display = ['phone_number', 'message_short', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['phone_number', 'provider_message_id']
    readonly_fields = ['message', 'provider_response', 'created_at']
    date_hierarchy = 'created_at'
    
    def message_short(self, obj):
        """Truncate message for display."""
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_short.short_description = 'Message'


@admin.register(PushNotificationLog)
class PushNotificationLogAdmin(admin.ModelAdmin):
    """Admin configuration for PushNotificationLog."""
    
    list_display = ['user', 'title', 'device_type', 'status', 'created_at']
    list_filter = ['device_type', 'status', 'created_at']
    search_fields = ['user__email', 'title']
    readonly_fields = ['body', 'data', 'provider_response', 'created_at']
    date_hierarchy = 'created_at'


@admin.register(NotificationStats)
class NotificationStatsAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationStats."""
    
    list_display = ['date', 'total_sent', 'total_delivered', 'total_read', 'total_failed']
    list_filter = ['date']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'