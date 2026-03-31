"""
Signals for Product module.
Handles automatic actions like creating thumbnails, updating stock, etc.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os

from .models import Product, ProductImage, ProductReview


@receiver(pre_save, sender=Product)
def set_published_date(sender, instance, **kwargs):
    """
    Set published date when product becomes active.
    """
    if instance.status == 'active' and not instance.published_at:
        instance.published_at = timezone.now()


@receiver(post_save, sender=ProductImage)
def create_thumbnail(sender, instance, created, **kwargs):
    """
    Create thumbnail automatically when image is uploaded.
    """
    if created and instance.image:
        try:
            # Open the image
            img = Image.open(instance.image.path)
            
            # Create thumbnail
            img.thumbnail((300, 300))
            
            # Save thumbnail
            thumb_io = BytesIO()
            img.save(thumb_io, format='JPEG' if img.format == 'JPEG' else 'PNG', quality=85)
            
            # Generate thumbnail filename
            filename = os.path.basename(instance.image.name)
            name, ext = os.path.splitext(filename)
            thumb_filename = f"{name}_thumb{ext}"
            
            # Save thumbnail to model
            instance.thumbnail.save(
                thumb_filename,
                ContentFile(thumb_io.getvalue()),
                save=False
            )
            instance.save()
            
        except Exception as e:
            # Log error but don't prevent save
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error creating thumbnail for {instance.image.name}: {e}")


@receiver(post_save, sender=ProductReview)
def update_product_rating(sender, instance, **kwargs):
    """
    Update product average rating when review is approved.
    """
    if instance.is_approved:
        from django.db.models import Avg
        
        product = instance.product
        avg_rating = product.reviews.filter(is_approved=True).aggregate(
            Avg('rating')
        )['rating__avg']
        
        # You can store avg_rating in a denormalized field if needed
        # product.avg_rating = avg_rating
        # product.save()