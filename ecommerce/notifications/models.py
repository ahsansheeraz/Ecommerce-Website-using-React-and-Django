"""
Notification models for e-commerce platform.
Handles all types of notifications: in-app, email, SMS, push notifications.
"""

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from users.models import User
import uuid


class NotificationType(models.Model):
    """
    Master table for notification types and templates.
    """
    
    CATEGORY_CHOICES = (
        ('order', 'Order Notifications'),
        ('payment', 'Payment Notifications'),
        ('product', 'Product Notifications'),
        ('account', 'Account Notifications'),
        ('promotion', 'Promotional Notifications'),
        ('alert', 'System Alerts'),
        ('reminder', 'Reminders'),
        ('support', 'Support Notifications'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Templates for different channels
    email_template = models.TextField(blank=True, help_text="Email HTML template")
    email_subject = models.CharField(max_length=200, blank=True)
    sms_template = models.TextField(blank=True, help_text="SMS text template")
    push_template = models.TextField(blank=True, help_text="Push notification template")
    in_app_template = models.TextField(blank=True, help_text="In-app notification template")
    
    # Which channels are enabled for this type
    enable_email = models.BooleanField(default=False)
    enable_sms = models.BooleanField(default=False)
    enable_push = models.BooleanField(default=False)
    enable_in_app = models.BooleanField(default=True)
    
    # Configuration
    is_active = models.BooleanField(default=True)
    requires_action = models.BooleanField(default=False, help_text="User needs to take action")
    expires_in_hours = models.PositiveIntegerField(null=True, blank=True, help_text="Notification expiry time")
    
    # Metadata
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon class for UI")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Type'
        verbose_name_plural = 'Notification Types'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['category']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Notification(models.Model):
    """
    Main notification model for in-app notifications.
    """
    
    CHANNEL_CHOICES = (
        ('in_app', 'In-App'),
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('push', 'Push Notification'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='notifications'
    )
    user_type = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        help_text="For notifications to all users of a type (admin, seller, etc.)"
    )
    
    # Notification type
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.PROTECT,
        related_name='notifications'
    )
    
    # Content
    title = models.CharField(max_length=255)
    message = models.TextField()
    short_message = models.CharField(max_length=100, blank=True, help_text="For push notifications")
    
    # Rich content
    image = models.URLField(max_length=500, blank=True)
    action_url = models.URLField(max_length=500, blank=True, help_text="URL when user clicks notification")
    action_text = models.CharField(max_length=100, blank=True, help_text="Button text")
    
    # Data payload
    data = models.JSONField(default=dict, blank=True, help_text="Additional data for the notification")
    
    # Channel and status
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES, default='in_app')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Priority
    priority = models.CharField(max_length=20, choices=NotificationType.PRIORITY_CHOICES, default='medium')
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # For generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user_type', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['notification_type', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"{self.title} - {self.user.email}"
        return f"{self.title} - {self.user_type}"
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        self.status = 'sent'
        self.sent_at = timezone.now()
        self.save()
    
    def mark_as_delivered(self):
        """Mark notification as delivered."""
        self.status = 'delivered'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_as_read(self):
        """Mark notification as read."""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def mark_as_failed(self, error=None):
        """Mark notification as failed."""
        self.status = 'failed'
        if error:
            self.metadata['error'] = str(error)
        self.save()


class NotificationPreference(models.Model):
    """
    User preferences for notifications (opt-in/opt-out per type and channel).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Which notification types the user wants (JSON for flexibility)
    preferences = models.JSONField(default=dict, help_text="""
        {
            "order_confirmation": {"email": true, "sms": false, "push": true},
            "payment_received": {"email": true, "in_app": true}
        }
    """)
    
    # Global opt-out
    email_opt_out = models.BooleanField(default=False)
    sms_opt_out = models.BooleanField(default=False)
    push_opt_out = models.BooleanField(default=False)
    
    # Quiet hours (don't send notifications during these times)
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    quiet_hours_timezone = models.CharField(max_length=50, default='UTC')
    
    # Device tokens for push notifications
    push_tokens = models.JSONField(default=list, blank=True)
    
    # Email settings
    email_frequency = models.CharField(
        max_length=20,
        choices=[
            ('instant', 'Instant'),
            ('daily', 'Daily Digest'),
            ('weekly', 'Weekly Digest'),
            ('never', 'Never')
        ],
        default='instant'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
        indexes = [
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
    
    def can_send(self, notification_type_code, channel):
        """
        Check if user can receive this notification type on this channel.
        
        Args:
            notification_type_code (str): Code of notification type
            channel (str): Channel to check
            
        Returns:
            bool: True if can send
        """
        # Check global opt-out
        if channel == 'email' and self.email_opt_out:
            return False
        if channel == 'sms' and self.sms_opt_out:
            return False
        if channel == 'push' and self.push_opt_out:
            return False
        
        # Check specific preference
        prefs = self.preferences.get(notification_type_code, {})
        if prefs.get(channel) is False:  # Explicitly disabled
            return False
        
        # Check quiet hours
        if self.quiet_hours_enabled and channel in ['sms', 'push']:
            now = timezone.localtime(timezone.now())
            current_time = now.time()
            
            if self.quiet_hours_start and self.quiet_hours_end:
                if self.quiet_hours_start <= self.quiet_hours_end:
                    # Normal range (e.g., 22:00 to 06:00)
                    if self.quiet_hours_start <= current_time <= self.quiet_hours_end:
                        return False
                else:
                    # Overnight range (e.g., 22:00 to 06:00 next day)
                    if current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end:
                        return False
        
        return True


class NotificationTemplate(models.Model):
    """
    Templates for notifications with dynamic variables.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE,
        related_name='templates'
    )
    
    # Template variables (for documentation)
    available_variables = models.JSONField(default=list, help_text="List of variables available for this template")
    
    # Templates
    email_subject_template = models.CharField(max_length=200)
    email_html_template = models.TextField()
    email_text_template = models.TextField(blank=True)
    
    sms_template = models.TextField()
    push_title_template = models.CharField(max_length=100)
    push_body_template = models.TextField()
    in_app_template = models.TextField()
    
    # Language support
    language = models.CharField(max_length=10, default='en')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        unique_together = ['notification_type', 'language']
    
    def __str__(self):
        return f"Template for {self.notification_type.name} ({self.language})"
    
    def render(self, context, channel):
        """
        Render template with context variables.
        
        Args:
            context (dict): Variables to replace
            channel (str): Channel to render for
            
        Returns:
            str: Rendered template
        """
        from django.template import Template, Context
        
        if channel == 'email':
            template_str = self.email_html_template
        elif channel == 'sms':
            template_str = self.sms_template
        elif channel == 'push':
            template_str = self.push_body_template
        else:
            template_str = self.in_app_template
        
        template = Template(template_str)
        return template.render(Context(context))


class EmailLog(models.Model):
    """
    Log of all sent emails.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    recipient_email = models.EmailField(db_index=True)
    recipient_name = models.CharField(max_length=200, blank=True)
    
    # Email details
    subject = models.CharField(max_length=500)
    from_email = models.EmailField()
    
    # Content
    html_content = models.TextField()
    text_content = models.TextField(blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('opened', 'Opened'),
            ('clicked', 'Clicked'),
            ('bounced', 'Bounced'),
            ('failed', 'Failed')
        ],
        default='sent'
    )
    
    # Related notification
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='email_logs'
    )
    
    # Provider response
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Tracking
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Email Log'
        verbose_name_plural = 'Email Logs'
        indexes = [
            models.Index(fields=['recipient_email', '-created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['provider_message_id']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Email to {self.recipient_email} - {self.subject}"


class SMSLog(models.Model):
    """
    Log of all sent SMS messages.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    phone_number = models.CharField(max_length=20, db_index=True)
    
    # Message
    message = models.TextField()
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('failed', 'Failed')
        ],
        default='sent'
    )
    
    # Related notification
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sms_logs'
    )
    
    # Provider response
    provider_message_id = models.CharField(max_length=255, blank=True)
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'SMS Log'
        verbose_name_plural = 'SMS Logs'
        indexes = [
            models.Index(fields=['phone_number', '-created_at']),
            models.Index(fields=['status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"SMS to {self.phone_number}"


class PushNotificationLog(models.Model):
    """
    Log of all sent push notifications.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_logs')
    device_token = models.CharField(max_length=500)
    device_type = models.CharField(
        max_length=20,
        choices=[
            ('ios', 'iOS'),
            ('android', 'Android'),
            ('web', 'Web')
        ]
    )
    
    # Notification
    title = models.CharField(max_length=200)
    body = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('opened', 'Opened'),
            ('failed', 'Failed')
        ],
        default='sent'
    )
    
    # Related notification
    notification = models.ForeignKey(
        Notification,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='push_logs'
    )
    
    # Provider response
    provider_response = models.JSONField(default=dict, blank=True)
    
    # Tracking
    opened_at = models.DateTimeField(null=True, blank=True)
    
    # Error
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Push Notification Log'
        verbose_name_plural = 'Push Notification Logs'
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['device_token']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Push to {self.user.email} - {self.title}"


class Announcement(models.Model):
    """
    System-wide announcements for all users.
    """
    
    PRIORITY_CHOICES = (
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('important', 'Important'),
        ('critical', 'Critical'),
    )
    
    AUDIENCE_CHOICES = (
        ('all', 'All Users'),
        ('customers', 'Customers Only'),
        ('sellers', 'Sellers Only'),
        ('admins', 'Admins Only'),
        ('specific_users', 'Specific Users'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Content
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='info')
    
    # Audience
    audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    specific_users = models.ManyToManyField(User, blank=True, related_name='targeted_announcements')
    
    # Display settings
    show_from = models.DateTimeField(default=timezone.now)
    show_until = models.DateTimeField(null=True, blank=True)
    is_dismissible = models.BooleanField(default=True)
    
    # Action
    action_url = models.URLField(max_length=500, blank=True)
    action_text = models.CharField(max_length=100, blank=True)
    
    # Image
    image = models.URLField(max_length=500, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Tracking
    views_count = models.PositiveIntegerField(default=0)
    clicks_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_announcements'
    )
    
    class Meta:
        verbose_name = 'Announcement'
        verbose_name_plural = 'Announcements'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['audience', 'is_active']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def should_show_to(self, user):
        """
        Check if announcement should be shown to user.
        
        Args:
            user (User): User to check
            
        Returns:
            bool: True if should show
        """
        if not self.is_active:
            return False
        
        now = timezone.now()
        if now < self.show_from:
            return False
        if self.show_until and now > self.show_until:
            return False
        
        if self.audience == 'all':
            return True
        elif self.audience == 'customers' and user.user_type == 'customer':
            return True
        elif self.audience == 'sellers' and user.user_type == 'seller':
            return True
        elif self.audience == 'admins' and user.user_type == 'admin':
            return True
        elif self.audience == 'specific_users' and user in self.specific_users.all():
            return True
        
        return False


class UserDevice(models.Model):
    """
    User devices for push notifications.
    """
    
    DEVICE_TYPE_CHOICES = (
        ('ios', 'iOS'),
        ('android', 'Android'),
        ('web', 'Web Browser'),
        ('desktop', 'Desktop App'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='devices')
    
    # Device identification
    device_id = models.CharField(max_length=255, unique=True, db_index=True)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    device_name = models.CharField(max_length=255, blank=True)
    device_model = models.CharField(max_length=255, blank=True)
    device_os = models.CharField(max_length=100, blank=True)
    device_os_version = models.CharField(max_length=50, blank=True)
    
    # Push token
    push_token = models.CharField(max_length=500, unique=True, db_index=True)
    
    # App info
    app_version = models.CharField(max_length=50, blank=True)
    
    # Last activity
    last_active_at = models.DateTimeField(auto_now=True)
    last_ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['push_token']),
        ]
    
    def __str__(self):
        return f"{self.device_name} - {self.user.email}"


class NotificationStats(models.Model):
    """
    Statistics for notifications (daily aggregation).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    date = models.DateField(db_index=True)
    
    # Totals
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_read = models.PositiveIntegerField(default=0)
    total_failed = models.PositiveIntegerField(default=0)
    
    # By channel
    email_sent = models.PositiveIntegerField(default=0)
    sms_sent = models.PositiveIntegerField(default=0)
    push_sent = models.PositiveIntegerField(default=0)
    in_app_sent = models.PositiveIntegerField(default=0)
    
    # By type
    stats_by_type = models.JSONField(default=dict, help_text="Stats per notification type")
    
    # By priority
    stats_by_priority = models.JSONField(default=dict, help_text="Stats per priority level")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Notification Stat'
        verbose_name_plural = 'Notification Stats'
        indexes = [
            models.Index(fields=['date']),
        ]
        unique_together = ['date']
    
    def __str__(self):
        return f"Stats for {self.date}"