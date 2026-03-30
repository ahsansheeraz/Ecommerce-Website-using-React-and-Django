"""
Signals for Cart module.
Handles automatic actions like cart expiry, abandoned cart tracking, etc.
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Cart, CartItem, AbandonedCart
import json


@receiver(post_save, sender=CartItem)
def update_cart_modified(sender, instance, **kwargs):
    """
    Update cart's updated_at timestamp when items change.
    """
    instance.cart.save()  # This will trigger auto_now


@receiver(post_save, sender=Cart)
def track_abandoned_cart(sender, instance, **kwargs):
    """
    Track carts that are abandoned (not converted to order after certain time).
    """
    # Check if cart is older than 24 hours and still active
    if instance.is_active and not instance.is_converted:
        time_threshold = timezone.now() - timezone.timedelta(hours=24)
        
        if instance.created_at < time_threshold:
            # Check if not already tracked
            if not AbandonedCart.objects.filter(cart=instance).exists():
                # Create snapshot of cart items
                cart_snapshot = {
                    'items': [
                        {
                            'product_id': str(item.product.id),
                            'product_name': item.product.name,
                            'quantity': item.quantity,
                            'unit_price': float(item.unit_price),
                            'total': float(item.total_price)
                        }
                        for item in instance.items.all()
                    ],
                    'subtotal': float(instance.subtotal),
                    'total': float(instance.total)
                }
                
                AbandonedCart.objects.create(
                    cart=instance,
                    user=instance.user,
                    cart_snapshot=cart_snapshot,
                    cart_total=instance.total,
                    status='new'
                )


# TODO: Signal for low stock notification when items in cart
"""
@receiver(post_save, sender=CartItem)
def check_cart_item_stock(sender, instance, **kwargs):
    # Check if item in cart is low on stock
    product = instance.product
    if product.track_inventory and product.stock_quantity <= product.low_stock_threshold:
        # Notify seller/admin
        create_notification(
            user_type='seller',
            title='Low Stock Alert',
            message=f'{product.name} is low on stock. Items in cart: {instance.quantity}'
        )
"""


# Signal for cleaning expired carts
@receiver(post_save, sender=Cart)
def clean_expired_carts(sender, **kwargs):
    """
    Clean up expired carts periodically.
    This would typically be called by a cron job or Celery task.
    """
    # Mark expired carts as inactive
    expired_carts = Cart.objects.filter(
        expires_at__lt=timezone.now(),
        is_active=True,
        is_converted=False
    )
    
    for cart in expired_carts:
        cart.is_active = False
        cart.save()