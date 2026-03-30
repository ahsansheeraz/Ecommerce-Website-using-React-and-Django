"""
Signals for Notifications module.
Automatically creates notifications for various events.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

# Line 68 par "Notification" undefined - add import:
from .models import Notification
from django.utils import timezone
from orders.models import Order, OrderStatusHistory
from payments.models import Transaction
from users.models import User
from .utils import create_order_notification, create_payment_notification
from .models import NotificationStats


@receiver(post_save, sender=Order)
def order_notification(sender, instance, created, **kwargs):
    """
    Create notification when order status changes.
    """
    if not created:
        # Check if status changed
        try:
            old_instance = Order.objects.get(id=instance.id)
            if old_instance.status != instance.status:
                # Status changed - send notification
                event_map = {
                    'confirmed': 'confirmed',
                    'processing': 'confirmed',
                    'shipped': 'shipped',
                    'delivered': 'delivered',
                    'cancelled': 'cancelled',
                }
                
                if instance.status in event_map:
                    create_order_notification(instance, event_map[instance.status])
        except Order.DoesNotExist:
            pass


@receiver(post_save, sender=Transaction)
def payment_notification(sender, instance, created, **kwargs):
    """
    Create notification for payment events.
    """
    if not created and instance.status == 'success':
        create_payment_notification(instance, 'success')
    elif not created and instance.status == 'failed':
        create_payment_notification(instance, 'failed')


@receiver(post_save, sender=User)
def welcome_notification(sender, instance, created, **kwargs):
    """
    Send welcome notification to new users.
    """
    if created:
        from .utils import create_notification
        create_notification(
            user=instance,
            notification_type='welcome',
            title=f'Welcome to {settings.SITE_NAME}!',
            message=f'Hi {instance.first_name}, thank you for joining us!',
            data={'user_id': str(instance.id)}
        )


@receiver(post_save, sender=Notification)
def update_notification_stats(sender, instance, created, **kwargs):
    """
    Update notification statistics.
    """
    if created:
        today = timezone.now().date()
        stat, _ = NotificationStats.objects.get_or_create(date=today)
        
        # Update total sent
        stat.total_sent += 1
        
        # Update by channel
        if instance.channel == 'email':
            stat.email_sent += 1
        elif instance.channel == 'sms':
            stat.sms_sent += 1
        elif instance.channel == 'push':
            stat.push_sent += 1
        else:
            stat.in_app_sent += 1
        
        # Update by type
        type_stats = stat.stats_by_type
        type_code = instance.notification_type.code
        type_stats[type_code] = type_stats.get(type_code, 0) + 1
        stat.stats_by_type = type_stats
        
        # Update by priority
        priority_stats = stat.stats_by_priority
        priority_stats[instance.priority] = priority_stats.get(instance.priority, 0) + 1
        stat.stats_by_priority = priority_stats
        
        stat.save()


# Signal for low stock notifications (commented for future use)
"""
@receiver(post_save, sender=Product)
def low_stock_notification(sender, instance, **kwargs):
    # Notify seller when product is low on stock
    if instance.track_inventory and instance.stock_quantity <= instance.low_stock_threshold:
        from .utils import create_notification
        
        create_notification(
            user=instance.seller,
            notification_type='low_stock',
            title='Low Stock Alert',
            message=f'{instance.name} is running low on stock. Current stock: {instance.stock_quantity}',
            data={'product_id': str(instance.id), 'product_name': instance.name},
            related_object=instance
        )
"""


# Signal for abandoned cart notifications
"""
@receiver(post_save, sender=AbandonedCart)
def abandoned_cart_notification(sender, instance, created, **kwargs):
    # Send reminder for abandoned carts
    if created and instance.user:
        from .utils import create_notification
        
        create_notification(
            user=instance.user,
            notification_type='abandoned_cart',
            title='Complete Your Purchase',
            message='You have items waiting in your cart. Complete your purchase now!',
            data={'cart_id': str(instance.cart.id)},
            related_object=instance.cart
        )
"""