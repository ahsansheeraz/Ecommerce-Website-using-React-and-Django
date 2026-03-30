"""
Signals for User module.
Handles automatic actions like creating profile when user is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal to create UserProfile automatically when a new User is created.
    
    Args:
        sender: Model class (User)
        instance: User instance that was saved
        created: Boolean indicating if a new record was created
        **kwargs: Additional keyword arguments
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal to save UserProfile when User is saved.
    
    Args:
        sender: Model class (User)
        instance: User instance that was saved
        **kwargs: Additional keyword arguments
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()