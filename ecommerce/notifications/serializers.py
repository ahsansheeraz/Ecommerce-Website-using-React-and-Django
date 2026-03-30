"""
Serializers for Notifications module.
Handles data transformation for notifications, preferences, etc.
"""

from rest_framework import serializers
from .models import (
    Notification, NotificationType, NotificationPreference,
    NotificationTemplate, Announcement, UserDevice,
    EmailLog, SMSLog, PushNotificationLog
)
from users.serializers import UserProfileSerializer


class NotificationTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationType.
    """
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'code', 'name', 'category', 'priority',
            'enable_email', 'enable_sms', 'enable_push', 'enable_in_app',
            'requires_action', 'icon', 'description'
        ]


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for in-app notifications.
    """
    
    notification_type_details = NotificationTypeSerializer(
        source='notification_type',
        read_only=True
    )
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'short_message', 'image',
            'action_url', 'action_text', 'data', 'notification_type',
            'notification_type_details', 'priority', 'status',
            'created_at', 'read_at', 'time_ago'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']
    
    def get_time_ago(self, obj):
        """
        Get human readable time difference.
        """
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for notification lists.
    """
    
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'image', 'action_url',
            'priority', 'status', 'created_at', 'time_ago'
        ]
    
    def get_time_ago(self, obj):
        from django.utils.timesince import timesince
        return timesince(obj.created_at)


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for notification preferences.
    """
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'preferences', 'email_opt_out', 'sms_opt_out',
            'push_opt_out', 'quiet_hours_enabled', 'quiet_hours_start',
            'quiet_hours_end', 'quiet_hours_timezone', 'email_frequency'
        ]
        read_only_fields = ['id']
    
    def validate_quiet_hours(self, data):
        """Validate quiet hours."""
        if data.get('quiet_hours_enabled'):
            start = data.get('quiet_hours_start')
            end = data.get('quiet_hours_end')
            if not start or not end:
                raise serializers.ValidationError(
                    "Quiet hours start and end times are required"
                )
        return data


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for notification templates (admin only).
    """
    
    notification_type_code = serializers.CharField(
        source='notification_type.code',
        read_only=True
    )
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id', 'notification_type', 'notification_type_code',
            'available_variables', 'language',
            'email_subject_template', 'email_html_template',
            'email_text_template', 'sms_template',
            'push_title_template', 'push_body_template',
            'in_app_template', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AnnouncementSerializer(serializers.ModelSerializer):
    """
    Serializer for announcements.
    """
    
    created_by_name = serializers.CharField(
        source='created_by.get_full_name',
        read_only=True
    )
    
    class Meta:
        model = Announcement
        fields = [
            'id', 'title', 'message', 'priority', 'audience',
            'specific_users', 'show_from', 'show_until',
            'is_dismissible', 'action_url', 'action_text',
            'image', 'is_active', 'views_count', 'clicks_count',
            'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'views_count', 'clicks_count',
            'created_by', 'created_at'
        ]
    
    def validate(self, data):
        """Validate announcement dates."""
        if data.get('show_until') and data.get('show_from'):
            if data['show_until'] <= data['show_from']:
                raise serializers.ValidationError({
                    'show_until': 'End date must be after start date'
                })
        return data


class UserDeviceSerializer(serializers.ModelSerializer):
    """
    Serializer for user devices.
    """
    
    class Meta:
        model = UserDevice
        fields = [
            'id', 'device_id', 'device_type', 'device_name',
            'device_model', 'device_os', 'device_os_version',
            'push_token', 'app_version', 'is_active',
            'last_active_at', 'created_at'
        ]
        read_only_fields = ['id', 'last_active_at', 'created_at']
    
    def validate_push_token(self, value):
        """Validate push token."""
        if not value or len(value) < 10:
            raise serializers.ValidationError("Invalid push token")
        return value


class EmailLogSerializer(serializers.ModelSerializer):
    """
    Serializer for email logs (admin only).
    """
    
    class Meta:
        model = EmailLog
        fields = [
            'id', 'recipient_email', 'recipient_name', 'subject',
            'from_email', 'status', 'provider_message_id',
            'opened_at', 'clicked_at', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SMSLogSerializer(serializers.ModelSerializer):
    """
    Serializer for SMS logs (admin only).
    """
    
    class Meta:
        model = SMSLog
        fields = [
            'id', 'phone_number', 'message', 'status',
            'provider_message_id', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PushNotificationLogSerializer(serializers.ModelSerializer):
    """
    Serializer for push notification logs (admin only).
    """
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = PushNotificationLog
        fields = [
            'id', 'user', 'user_email', 'device_type',
            'title', 'body', 'status', 'opened_at',
            'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class MarkNotificationReadSerializer(serializers.Serializer):
    """
    Serializer for marking notifications as read.
    """
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    mark_all = serializers.BooleanField(default=False)


class BulkNotificationSerializer(serializers.Serializer):
    """
    Serializer for sending bulk notifications (admin only).
    """
    
    user_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False
    )
    user_type = serializers.ChoiceField(
        choices=['all', 'customers', 'sellers', 'admins'],
        required=False
    )
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    notification_type_code = serializers.CharField()
    action_url = serializers.URLField(required=False, allow_blank=True)
    action_text = serializers.CharField(required=False, allow_blank=True)
    data = serializers.JSONField(default=dict, required=False)
    
    def validate(self, data):
        """Validate either user_ids or user_type is provided."""
        if not data.get('user_ids') and not data.get('user_type'):
            raise serializers.ValidationError(
                "Either user_ids or user_type must be provided"
            )
        
        # Validate notification type exists
        try:
            notification_type = NotificationType.objects.get(
                code=data['notification_type_code'],
                is_active=True
            )
            data['notification_type'] = notification_type
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError({
                'notification_type_code': 'Invalid notification type'
            })
        
        return data


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer for notification statistics (admin only).
    """
    
    date = serializers.DateField()
    total_sent = serializers.IntegerField()
    total_delivered = serializers.IntegerField()
    total_read = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    by_channel = serializers.DictField()
    by_type = serializers.DictField()
    by_priority = serializers.DictField()


class TestNotificationSerializer(serializers.Serializer):
    """
    Serializer for testing notifications.
    """
    
    channel = serializers.ChoiceField(choices=['email', 'sms', 'push', 'in_app'])
    recipient = serializers.CharField()  # email, phone, or user_id
    notification_type_code = serializers.CharField()