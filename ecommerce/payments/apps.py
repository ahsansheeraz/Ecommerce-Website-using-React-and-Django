"""
App configuration for payments module.
"""

from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    """
    Configuration class for payments app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payments'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import payments.signals  # noqa