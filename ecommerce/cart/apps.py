"""
App configuration for cart module.
"""

from django.apps import AppConfig


class CartConfig(AppConfig):
    """
    Configuration class for cart app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cart'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import cart.signals  # noqa