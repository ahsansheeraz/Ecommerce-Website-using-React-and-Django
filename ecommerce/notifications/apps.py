"""
App configuration for notifications module.
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """
    Configuration class for notifications app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import notifications.signals  # noqa