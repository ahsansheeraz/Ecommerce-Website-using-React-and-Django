"""
Signals for Payments module.
Handles automatic actions like updating order status on payment success.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Transaction, RefundRequest


@receiver(post_save, sender=Transaction)
def update_order_on_payment(sender, instance, created, **kwargs):
    """
    Update order status when payment is successful.
    """
    if instance.status == 'success' and instance.order:
        order = instance.order
        
        # Update order payment status
        order.payment_status = 'paid'
        order.paid_amount = instance.amount
        
        # Update order status if pending
        if order.status == 'pending':
            order.status = 'processing'
        
        order.save()


@receiver(post_save, sender=RefundRequest)
def notify_refund_status(sender, instance, created, **kwargs):
    """
    Send notification when refund request status changes.
    """
    if not created:
        # TODO: Send notification to user
        # if instance.status == 'approved':
        #     send_refund_approved_notification(instance)
        # elif instance.status == 'rejected':
        #     send_refund_rejected_notification(instance)
        pass


# Signal for updating seller balance on successful order
"""
@receiver(post_save, sender=Transaction)
def update_seller_balance(sender, instance, **kwargs):
    # Update seller balance when payment is successful.
    if instance.status == 'success' and instance.order:
        from users.models import SellerBalance
        
        for item in instance.order.items.all():
            seller = item.product.seller
            balance, created = SellerBalance.objects.get_or_create(
                seller=seller,
                defaults={'balance': 0, 'pending_balance': 0}
            )
            
            # Calculate seller's earning (order total - platform fee)
            seller_amount = item.total_price * 0.8  # 80% to seller
            balance.pending_balance += seller_amount
            balance.save()
"""