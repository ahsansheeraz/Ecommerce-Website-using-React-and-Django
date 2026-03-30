"""
Signals for Orders module.
Handles automatic actions like stock updates, notifications, etc.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import django.db.models as models
from .models import Order, OrderItem, OrderPayment


@receiver(post_save, sender=Order)
def create_order_status_history(sender, instance, created, **kwargs):
    """
    Create initial status history when order is created.
    """
    if created:
        from .models import OrderStatusHistory
        OrderStatusHistory.objects.create(
            order=instance,
            status=instance.status,
            notes='Order created'
        )


@receiver(post_save, sender=OrderPayment)
def update_order_payment_status(sender, instance, **kwargs):
    """
    Update order payment status when payment is processed.
    """
    if instance.status == 'success':
        order = instance.order
        total_paid = order.payments.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        order.paid_amount = total_paid
        if total_paid >= order.total_amount:
            order.payment_status = 'paid'
        elif total_paid > 0:
            order.payment_status = 'partially_paid'
        order.save()


@receiver(pre_save, sender=OrderItem)
def track_order_item_changes(sender, instance, **kwargs):
    """
    Track changes to order items (cancellations, returns).
    """
    if instance.pk:
        try:
            old_instance = OrderItem.objects.get(pk=instance.pk)
            
            # Check if cancelled
            if not old_instance.is_cancelled and instance.is_cancelled:
                instance.cancelled_at = timezone.now()
                
                # Restore stock
                product = instance.product
                if product.track_inventory:
                    product.stock_quantity += instance.quantity
                    product.sold_count -= instance.quantity
                    product.save()
            
            # Check if returned
            if not old_instance.is_returned and instance.is_returned:
                instance.returned_at = timezone.now()
                
        except OrderItem.DoesNotExist:
            pass


# TODO: Signal for low stock notification based on orders
"""
@receiver(post_save, sender=OrderItem)
def check_low_stock_after_order(sender, instance, **kwargs):
    # Check if product stock is low after order
    product = instance.product
    if product.track_inventory and product.stock_quantity <= product.low_stock_threshold:
        # Notify seller/admin
        create_notification(
            user_type='seller',
            title='Low Stock Alert',
            message=f'{product.name} is running low on stock. Current stock: {product.stock_quantity}',
            data={'product_id': str(product.id)}
        )
"""


# Signal for order confirmation email
"""
@receiver(post_save, sender=Order)
def send_order_confirmation_email(sender, instance, created, **kwargs):
    # Send email when order is created
    if created:
        send_mail(
            subject=f'Order Confirmation - #{instance.order_number}',
            message=f'Your order has been confirmed. Total: ${instance.total_amount}',
            from_email='noreply@ecommerce.com',
            recipient_list=[instance.user.email],
            html_message=render_to_string('emails/order_confirmation.html', {'order': instance})
        )
"""