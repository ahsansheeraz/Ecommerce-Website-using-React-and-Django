"""
App configuration for products module.
"""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """
    Configuration class for products app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'products'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import products.signals  # noqa