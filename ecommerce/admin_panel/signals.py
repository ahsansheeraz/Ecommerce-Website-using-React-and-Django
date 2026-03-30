"""
Signals for Admin Panel module.
Automatically logs admin activities and updates system health.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import DashboardWidget, DashboardWidgetPlacement
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import AdminActivityLog, SystemHealth
import threading

# Store current request in thread local
_thread_locals = threading.local()

def get_current_request():
    """Get current request from thread local."""
    return getattr(_thread_locals, 'request', None)

def set_current_request(request):
    """Set current request in thread local."""
    _thread_locals.request = request


class AdminActivityMiddleware:
    """Middleware to capture request for admin activity logging."""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        set_current_request(request)
        response = self.get_response(request)
        return response


@receiver(post_save)
def log_admin_create_update(sender, instance, created, **kwargs):
    """
    Log create/update actions by admin users.
    """
    # Skip for certain models
    if sender in [AdminActivityLog, SystemHealth]:
        return
    
    request = get_current_request()
    if not request or not request.user.is_authenticated:
        return
    
    # Only log for admin users
    if request.user.user_type not in ['admin', 'moderator']:
        return
    
    action = 'create' if created else 'update'
    
    # Get changes for update
    details = {}
    if not created and hasattr(instance, '_loaded_values'):
        # Track field changes
        for field, old_value in instance._loaded_values.items():
            new_value = getattr(instance, field)
            if old_value != new_value:
                details[field] = {
                    'old': str(old_value),
                    'new': str(new_value)
                }
    
    # Get IP address
    ip_address = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    
    AdminActivityLog.objects.create(
        admin=request.user,
        action=action,
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance)[:200],
        details=details,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        status='success'
    )


@receiver(pre_delete)
def log_admin_delete(sender, instance, **kwargs):
    """
    Log delete actions by admin users.
    """
    # Skip for certain models
    if sender in [AdminActivityLog, SystemHealth]:
        return
    
    request = get_current_request()
    if not request or not request.user.is_authenticated:
        return
    
    # Only log for admin users
    if request.user.user_type not in ['admin', 'moderator']:
        return
    
    # Get IP address
    ip_address = request.META.get('REMOTE_ADDR')
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    
    AdminActivityLog.objects.create(
        admin=request.user,
        action='delete',
        content_type=ContentType.objects.get_for_model(instance),
        object_id=instance.pk,
        object_repr=str(instance)[:200],
        details={'deleted_object': str(instance)},
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        status='success'
    )


# Signal for creating default widgets on first install
@receiver(post_save, sender=DashboardWidget)
def create_default_dashboards(sender, created, **kwargs):
    """
    Create default dashboards for existing admins when new widgets are added.
    """
    if created and kwargs.get('raw', False):
        # Only run for manually created widgets, not fixtures
        return
    
    if created and kwargs.get('instance', False):
        instance = kwargs['instance']
        if instance.is_default:
            # Add to all admin dashboards
            from .models import AdminDashboard
            dashboards = AdminDashboard.objects.filter(is_default=True)
            
            for dashboard in dashboards:
                DashboardWidgetPlacement.objects.get_or_create(
                    dashboard=dashboard,
                    widget=instance
                )