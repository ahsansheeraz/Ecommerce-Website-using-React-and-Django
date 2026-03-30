"""
Serializers for Admin Panel module.
Handles data transformation for admin dashboard, settings, reports, etc.
"""

from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from .models import (
    DashboardWidget, AdminDashboard, DashboardWidgetPlacement,
    AdminActivityLog, SystemSetting, ReportTemplate, GeneratedReport,
    AdminNote, BackupLog, MaintenanceMode, AdminNotification, SystemHealth
)
from users.serializers import UserProfileSerializer
from users.models import User


class DashboardWidgetSerializer(serializers.ModelSerializer):
    """
    Serializer for DashboardWidget.
    """
    
    class Meta:
        model = DashboardWidget
        fields = [
            'id', 'name', 'widget_type', 'chart_type', 'config',
            'data_source', 'size', 'order', 'roles', 'is_active',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DashboardWidgetPlacementSerializer(serializers.ModelSerializer):
    """
    Serializer for widget placement.
    """
    
    widget_details = DashboardWidgetSerializer(source='widget', read_only=True)
    
    class Meta:
        model = DashboardWidgetPlacement
        fields = ['id', 'widget', 'widget_details', 'row', 'column', 'custom_config']


class AdminDashboardSerializer(serializers.ModelSerializer):
    """
    Serializer for AdminDashboard.
    """
    
    placements = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminDashboard
        fields = [
            'id', 'name', 'placements', 'layout', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_placements(self, obj):
        """Get widget placements for this dashboard."""
        placements = DashboardWidgetPlacement.objects.filter(dashboard=obj)
        return DashboardWidgetPlacementSerializer(placements, many=True).data


class AdminDashboardCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating admin dashboards.
    """
    
    class Meta:
        model = AdminDashboard
        fields = ['name', 'layout', 'is_default']
    
    def validate(self, data):
        """Validate dashboard creation."""
        user = self.context['request'].user
        
        # If setting as default, unset existing default
        if data.get('is_default'):
            AdminDashboard.objects.filter(user=user, is_default=True).update(is_default=False)
        
        return data


class AdminActivityLogSerializer(serializers.ModelSerializer):
    """
    Serializer for admin activity logs.
    """
    
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    object_type = serializers.CharField(source='content_type.model', read_only=True)
    
    class Meta:
        model = AdminActivityLog
        fields = [
            'id', 'admin', 'admin_email', 'admin_name', 'action',
            'object_type', 'object_id', 'object_repr', 'details',
            'ip_address', 'user_agent', 'status', 'error_message',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemSettingSerializer(serializers.ModelSerializer):
    """
    Serializer for system settings.
    """
    
    typed_value = serializers.SerializerMethodField()
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True)
    
    class Meta:
        model = SystemSetting
        fields = [
            'id', 'key', 'value', 'typed_value', 'value_type',
            'category', 'label', 'description', 'validation_rules',
            'options', 'is_editable', 'is_encrypted', 'updated_by',
            'updated_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'updated_by']
    
    def get_typed_value(self, obj):
        """Get typed value."""
        return obj.get_typed_value()
    
    def validate(self, data):
        """Validate setting value based on type and rules."""
        value = data.get('value')
        value_type = data.get('value_type', self.instance.value_type if self.instance else None)
        
        if value_type == 'integer':
            try:
                int(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({'value': 'Must be an integer'})
        elif value_type == 'float':
            try:
                float(value)
            except (ValueError, TypeError):
                raise serializers.ValidationError({'value': 'Must be a number'})
        elif value_type == 'boolean':
            if str(value).lower() not in ['true', 'false', '1', '0', 'yes', 'no', 'on', 'off']:
                raise serializers.ValidationError({'value': 'Must be a boolean value'})
        elif value_type == 'json':
            import json
            try:
                if isinstance(value, str):
                    json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({'value': 'Must be valid JSON'})
        
        return data


class ReportTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for report templates.
    """
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'name', 'report_type', 'description', 'config',
            'available_formats', 'is_scheduled', 'schedule',
            'recipients', 'roles', 'is_active', 'is_system',
            'created_by', 'created_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']


class GeneratedReportSerializer(serializers.ModelSerializer):
    """
    Serializer for generated reports.
    """
    
    template_name = serializers.CharField(source='template.name', read_only=True)
    generated_by_email = serializers.EmailField(source='generated_by.email', read_only=True)
    
    class Meta:
        model = GeneratedReport
        fields = [
            'id', 'template', 'template_name', 'name', 'parameters',
            'file', 'file_format', 'file_size', 'status', 'error_message',
            'row_count', 'generated_by', 'generated_by_email',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at', 'file_size']


class AdminNoteSerializer(serializers.ModelSerializer):
    """
    Serializer for admin notes.
    """
    
    admin_email = serializers.EmailField(source='admin.email', read_only=True)
    admin_name = serializers.CharField(source='admin.get_full_name', read_only=True)
    related_object_type = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminNote
        fields = [
            'id', 'admin', 'admin_email', 'admin_name', 'title',
            'content', 'content_type', 'object_id', 'related_object_type',
            'color', 'is_private', 'shared_with', 'is_pinned',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'admin', 'created_at', 'updated_at']
    
    def get_related_object_type(self, obj):
        """Get related object type name."""
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def validate(self, data):
        """Validate note creation."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            data['admin'] = request.user
        return data


class BackupLogSerializer(serializers.ModelSerializer):
    """
    Serializer for backup logs.
    """
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = BackupLog
        fields = [
            'id', 'name', 'backup_type', 'status', 'file',
            'file_size', 'tables_included', 'row_count',
            'created_by', 'created_by_email', 'notes',
            'created_at', 'completed_at'
        ]
        read_only_fields = ['id', 'created_at', 'completed_at']


class MaintenanceModeSerializer(serializers.ModelSerializer):
    """
    Serializer for maintenance mode.
    """
    
    enabled_by_email = serializers.EmailField(source='enabled_by.email', read_only=True)
    
    class Meta:
        model = MaintenanceMode
        fields = [
            'id', 'is_active', 'title', 'message', 'allowed_ips',
            'allowed_paths', 'start_time', 'end_time',
            'enabled_by', 'enabled_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'enabled_by']


class AdminNotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for admin notifications.
    """
    
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    is_dismissed = serializers.SerializerMethodField()
    
    class Meta:
        model = AdminNotification
        fields = [
            'id', 'title', 'message', 'priority', 'for_all_admins',
            'specific_admins', 'action_url', 'action_text',
            'expires_at', 'is_dismissible', 'is_dismissed',
            'dismissed_by', 'created_by', 'created_by_email',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']
    
    def get_is_dismissed(self, obj):
        """Check if current user has dismissed this notification."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user in obj.dismissed_by.all()
        return False


class SystemHealthSerializer(serializers.ModelSerializer):
    """
    Serializer for system health.
    """
    
    class Meta:
        model = SystemHealth
        fields = [
            'id', 'component', 'status', 'response_time',
            'error_rate', 'message', 'metrics', 'checked_at'
        ]
        read_only_fields = ['id', 'checked_at']


class DashboardSummarySerializer(serializers.Serializer):
    """
    Serializer for dashboard summary data.
    """
    
    # User stats
    total_users = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    active_users = serializers.IntegerField()
    
    # Order stats
    total_orders = serializers.IntegerField()
    orders_today = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    revenue_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    # Product stats
    total_products = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    out_of_stock = serializers.IntegerField()
    
    # System stats
    system_health = serializers.CharField()
    pending_tasks = serializers.IntegerField()


class QuickActionSerializer(serializers.Serializer):
    """
    Serializer for quick actions.
    """
    
    action = serializers.ChoiceField(choices=[
        'create_product',
        'create_coupon',
        'send_newsletter',
        'run_report',
        'backup_db',
        'clear_cache',
    ])
    data = serializers.JSONField(default=dict, required=False)


class BulkActionSerializer(serializers.Serializer):
    """
    Serializer for bulk actions on objects.
    """
    
    action = serializers.CharField()
    ids = serializers.ListField(child=serializers.UUIDField())
    data = serializers.JSONField(default=dict, required=False)


class SystemSettingsGroupSerializer(serializers.Serializer):
    """
    Serializer for grouped system settings.
    """
    
    category = serializers.CharField()
    settings = SystemSettingSerializer(many=True)