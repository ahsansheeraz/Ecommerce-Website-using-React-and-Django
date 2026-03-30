"""
Admin Panel models for e-commerce platform.
Handles dashboard settings, activity logs, reports, and admin-specific data.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from users.models import User
import uuid


class DashboardWidget(models.Model):
    """
    Configurable dashboard widgets for admin panel.
    """
    
    WIDGET_TYPES = (
        ('chart', 'Chart'),
        ('table', 'Table'),
        ('metric', 'Metric'),
        ('list', 'List'),
        ('calendar', 'Calendar'),
    )
    
    CHART_TYPES = (
        ('line', 'Line Chart'),
        ('bar', 'Bar Chart'),
        ('pie', 'Pie Chart'),
        ('area', 'Area Chart'),
        ('number', 'Number Card'),
    )
    
    SIZE_CHOICES = (
        ('small', 'Small (1/4)'),
        ('medium', 'Medium (1/2)'),
        ('large', 'Large (3/4)'),
        ('full', 'Full Width'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=20, choices=WIDGET_TYPES)
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, null=True, blank=True)
    
    # Widget configuration
    config = models.JSONField(default=dict, help_text="Widget-specific configuration")
    data_source = models.CharField(max_length=200, help_text="API endpoint or data source")
    
    # Appearance
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, default='medium')
    order = models.PositiveIntegerField(default=0)
    
    # Access control
    roles = models.JSONField(default=list, help_text="User roles that can see this widget")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False, help_text="Default widget for all admins")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Dashboard Widget'
        verbose_name_plural = 'Dashboard Widgets'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class AdminDashboard(models.Model):
    """
    Custom dashboard layouts for different admins.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_dashboards')
    name = models.CharField(max_length=100, default='Default Dashboard')
    
    # Widgets in this dashboard
    widgets = models.ManyToManyField(
        DashboardWidget,
        through='DashboardWidgetPlacement',
        related_name='dashboards'
    )
    
    # Layout configuration
    layout = models.JSONField(default=dict, help_text="Dashboard layout configuration")
    
    # Status
    is_default = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Dashboard'
        verbose_name_plural = 'Admin Dashboards'
        unique_together = ['user', 'is_default']
    
    def __str__(self):
        return f"{self.user.email}'s Dashboard - {self.name}"


class DashboardWidgetPlacement(models.Model):
    """
    Through model for widget placement in dashboards.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dashboard = models.ForeignKey(AdminDashboard, on_delete=models.CASCADE)
    widget = models.ForeignKey(DashboardWidget, on_delete=models.CASCADE)
    
    # Position in dashboard
    row = models.PositiveIntegerField(default=0)
    column = models.PositiveIntegerField(default=0)
    
    # Custom configuration for this placement
    custom_config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Widget Placement'
        verbose_name_plural = 'Widget Placements'
        ordering = ['row', 'column']
        unique_together = ['dashboard', 'widget']


class AdminActivityLog(models.Model):
    """
    Log all admin activities for audit purposes.
    """
    
    ACTION_TYPES = (
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('settings_change', 'Settings Change'),
        ('permission_change', 'Permission Change'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Who performed the action
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='admin_activities'
    )
    
    # What action was performed
    action = models.CharField(max_length=50, choices=ACTION_TYPES)
    
    # On which model/object
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')
    object_repr = models.CharField(max_length=200, help_text="String representation of the object")
    
    # Details
    details = models.JSONField(default=dict, help_text="Action details and changes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='success', choices=[
        ('success', 'Success'),
        ('failure', 'Failure'),
        ('pending', 'Pending'),
    ])
    error_message = models.TextField(blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Admin Activity Log'
        verbose_name_plural = 'Admin Activity Logs'
        indexes = [
            models.Index(fields=['admin', '-created_at']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.admin.email if self.admin else 'Unknown'} - {self.action} - {self.created_at}"
    
    def save(self, *args, **kwargs):
        """Set object_repr automatically."""
        if self.content_object and not self.object_repr:
            self.object_repr = str(self.content_object)
        super().save(*args, **kwargs)


class SystemSetting(models.Model):
    """
    System-wide settings configurable via admin panel.
    """
    
    VALUE_TYPE_CHOICES = (
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
        ('email', 'Email'),
        ('url', 'URL'),
    )
    
    CATEGORY_CHOICES = (
        ('general', 'General'),
        ('payment', 'Payment'),
        ('shipping', 'Shipping'),
        ('email', 'Email'),
        ('tax', 'Tax'),
        ('seo', 'SEO'),
        ('security', 'Security'),
        ('features', 'Features'),
        ('maintenance', 'Maintenance'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.CharField(max_length=100, unique=True, db_index=True)
    value = models.TextField()
    value_type = models.CharField(max_length=20, choices=VALUE_TYPE_CHOICES, default='string')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='general')
    
    # Display information
    label = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Validation
    validation_rules = models.JSONField(default=dict, blank=True, help_text="JSON schema for validation")
    
    # For select/choice types
    options = models.JSONField(default=list, blank=True, help_text="Available options for select type")
    
    # Is this setting editable
    is_editable = models.BooleanField(default=True)
    is_encrypted = models.BooleanField(default=False, help_text="Should be stored encrypted")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='updated_settings'
    )
    
    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'
        ordering = ['category', 'key']
    
    def __str__(self):
        return f"{self.category} - {self.key}"
    
    def get_typed_value(self):
        """Get value with correct type."""
        if self.value_type == 'integer':
            return int(self.value)
        elif self.value_type == 'float':
            return float(self.value)
        elif self.value_type == 'boolean':
            return self.value.lower() in ['true', '1', 'yes', 'on']
        elif self.value_type == 'json':
            import json
            return json.loads(self.value)
        return self.value


class ReportTemplate(models.Model):
    """
    Predefined report templates for admin.
    """
    
    REPORT_TYPES = (
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('customer', 'Customer Report'),
        ('product', 'Product Report'),
        ('payment', 'Payment Report'),
        ('shipping', 'Shipping Report'),
        ('tax', 'Tax Report'),
        ('custom', 'Custom Report'),
    )
    
    FORMAT_CHOICES = (
        ('csv', 'CSV'),
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
        ('json', 'JSON'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    
    # Report configuration
    config = models.JSONField(default=dict, help_text="Report configuration (fields, filters, etc.)")
    
    # Available formats
    available_formats = models.JSONField(default=list, help_text="List of available export formats")
    
    # Schedule (for automated reports)
    is_scheduled = models.BooleanField(default=False)
    schedule = models.JSONField(default=dict, blank=True, help_text="Cron expression or schedule config")
    recipients = models.JSONField(default=list, blank=True, help_text="Email recipients for scheduled reports")
    
    # Access control
    roles = models.JSONField(default=list, help_text="User roles that can access this report")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_system = models.BooleanField(default=False, help_text="System default report")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports'
    )
    
    class Meta:
        verbose_name = 'Report Template'
        verbose_name_plural = 'Report Templates'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class GeneratedReport(models.Model):
    """
    Generated report instances.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        ReportTemplate,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    name = models.CharField(max_length=200)
    
    # Report parameters
    parameters = models.JSONField(default=dict, help_text="Parameters used to generate this report")
    
    # Generated file
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    file_format = models.CharField(max_length=20, choices=ReportTemplate.FORMAT_CHOICES)
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True)
    
    # Metadata
    row_count = models.PositiveIntegerField(default=0)
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_reports'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Generated Report'
        verbose_name_plural = 'Generated Reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.date()}"


class AdminNote(models.Model):
    """
    Private notes for admin users.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_notes')
    
    # Note content
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    # For notes related to specific objects
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Color/label for organization
    color = models.CharField(max_length=20, default='blue', choices=[
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('yellow', 'Yellow'),
        ('purple', 'Purple'),
    ])
    
    # Sharing
    is_private = models.BooleanField(default=True, help_text="Only visible to creator")
    shared_with = models.ManyToManyField(
        User,
        blank=True,
        related_name='shared_notes',
        help_text="Other admins to share with"
    )
    
    # Pin to dashboard
    is_pinned = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Admin Note'
        verbose_name_plural = 'Admin Notes'
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title


class BackupLog(models.Model):
    """
    Track database backups.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    TYPE_CHOICES = (
        ('full', 'Full Backup'),
        ('partial', 'Partial Backup'),
        ('auto', 'Automated Backup'),
        ('manual', 'Manual Backup'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    backup_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File
    file = models.FileField(upload_to='backups/', null=True, blank=True)
    file_size = models.PositiveIntegerField(default=0)
    
    # Details
    tables_included = models.JSONField(default=list)
    row_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_backups'
    )
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Backup Log'
        verbose_name_plural = 'Backup Logs'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.date()}"


class MaintenanceMode(models.Model):
    """
    Track maintenance mode periods.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_active = models.BooleanField(default=False)
    
    # Maintenance message
    title = models.CharField(max_length=200, default='Under Maintenance')
    message = models.TextField(default='We are currently performing maintenance. Please check back soon.')
    
    # Allowed IPs (can still access during maintenance)
    allowed_ips = models.JSONField(default=list, blank=True)
    
    # Allowed paths (can still access during maintenance)
    allowed_paths = models.JSONField(default=list, blank=True, help_text="URL paths that remain accessible")
    
    # Schedule
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    
    # Who enabled it
    enabled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='enabled_maintenance'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Maintenance Mode'
        verbose_name_plural = 'Maintenance Modes'
    
    def __str__(self):
        return f"Maintenance: {'Active' if self.is_active else 'Inactive'}"


class AdminNotification(models.Model):
    """
    System notifications for admins (alerts, warnings, info).
    """
    
    PRIORITY_CHOICES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('critical', 'Critical'),
        ('success', 'Success'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='info')
    
    # Which admins should see this
    for_all_admins = models.BooleanField(default=True)
    specific_admins = models.ManyToManyField(User, blank=True, related_name='admin_notifications')
    
    # Action
    action_url = models.URLField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Dismissible
    is_dismissible = models.BooleanField(default=True)
    
    # Who dismissed it (tracking)
    dismissed_by = models.ManyToManyField(
        User,
        blank=True,
        related_name='dismissed_notifications'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_admin_notifications'
    )
    
    class Meta:
        verbose_name = 'Admin Notification'
        verbose_name_plural = 'Admin Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class SystemHealth(models.Model):
    """
    System health check records.
    """
    
    COMPONENT_CHOICES = (
        ('database', 'Database'),
        ('cache', 'Cache'),
        ('storage', 'Storage'),
        ('email', 'Email Service'),
        ('payment', 'Payment Gateway'),
        ('sms', 'SMS Service'),
        ('cdn', 'CDN'),
    )
    
    STATUS_CHOICES = (
        ('healthy', 'Healthy'),
        ('degraded', 'Degraded'),
        ('down', 'Down'),
        ('maintenance', 'Under Maintenance'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    component = models.CharField(max_length=50, choices=COMPONENT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    
    # Details
    response_time = models.FloatField(null=True, blank=True, help_text="Response time in ms")
    error_rate = models.FloatField(null=True, blank=True, help_text="Error rate percentage")
    message = models.TextField(blank=True)
    
    # Metrics
    metrics = models.JSONField(default=dict, blank=True)
    
    checked_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'System Health'
        verbose_name_plural = 'System Health'
        indexes = [
            models.Index(fields=['component', '-checked_at']),
        ]
        ordering = ['-checked_at']
    
    def __str__(self):
        return f"{self.component} - {self.status} at {self.checked_at}"