"""
App configuration for orders module.
"""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """
    Configuration class for orders app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import orders.signals  # noqa