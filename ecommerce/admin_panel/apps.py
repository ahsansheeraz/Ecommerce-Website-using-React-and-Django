"""
App configuration for admin_panel module.
"""

from django.apps import AppConfig


class AdminPanelConfig(AppConfig):
    """
    Configuration class for admin_panel app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admin_panel'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import admin_panel.signals  # noqa