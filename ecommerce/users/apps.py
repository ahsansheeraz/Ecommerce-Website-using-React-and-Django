"""
App configuration for users module.
"""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration class for users app.
    """
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        """
        Import signals when app is ready.
        """
        import users.signals  # noqa