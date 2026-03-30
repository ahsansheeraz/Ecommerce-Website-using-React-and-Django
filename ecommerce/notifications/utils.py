"""
Utility functions for Notifications module.
Helper functions for creating and sending notifications.
"""

from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.conf import settings
from .models import (
    Notification, NotificationType, NotificationPreference,
    EmailLog, SMSLog, PushNotificationLog, UserDevice
)
import logging

logger = logging.getLogger(__name__)


def create_notification(user=None, user_type=None, notification_type=None,
                        title=None, message=None, short_message=None,
                        image=None, action_url=None, action_text=None,
                        data=None, priority='medium', channel='in_app',
                        related_object=None):
    """
    Create a notification.
    
    Args:
        user (User): Recipient user
        user_type (str): Recipient user type (for bulk notifications)
        notification_type (str): Notification type code
        title (str): Notification title
        message (str): Notification message
        short_message (str): Short message for push
        image (str): Image URL
        action_url (str): Action URL
        action_text (str): Action button text
        data (dict): Additional data
        priority (str): Priority level
        channel (str): Notification channel
        related_object (Model): Related object
        
    Returns:
        Notification: Created notification
    """
    try:
        # Get notification type
        if isinstance(notification_type, str):
            notif_type = NotificationType.objects.get(
                code=notification_type,
                is_active=True
            )
        else:
            notif_type = notification_type
        
        # Set expiry if configured
        expires_at = None
        if notif_type.expires_in_hours:
            expires_at = timezone.now() + timezone.timedelta(
                hours=notif_type.expires_in_hours
            )
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            user_type=user_type,
            notification_type=notif_type,
            title=title,
            message=message,
            short_message=short_message or message[:100],
            image=image,
            action_url=action_url,
            action_text=action_text,
            data=data or {},
            priority=priority,
            channel=channel,
            expires_at=expires_at,
            status='pending'
        )
        
        # Set related object if provided
        if related_object:
            notification.related_object = related_object
            notification.save()
        
        # Send through appropriate channel
        if channel == 'email' and notif_type.enable_email:
            send_email_notification.delay(notification.id)
        elif channel == 'sms' and notif_type.enable_sms:
            send_sms_notification.delay(notification.id)
        elif channel == 'push' and notif_type.enable_push:
            send_push_notification.delay(notification.id)
        else:
            # In-app notification - mark as delivered immediately
            notification.mark_as_delivered()
        
        return notification
        
    except NotificationType.DoesNotExist:
        logger.error(f"Notification type {notification_type} not found")
        return None
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return None


def send_email_notification(notification_id):
    """
    Send email notification.
    
    Args:
        notification_id (UUID): Notification ID
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check if user wants email
        if notification.user:
            prefs = NotificationPreference.objects.get_or_create(
                user=notification.user
            )[0]
            
            if not prefs.can_send(
                notification.notification_type.code,
                'email'
            ):
                notification.mark_as_failed("User opted out")
                return
        
        # Get template
        template = notification.notification_type.templates.filter(
            language='en'
        ).first()
        
        if not template:
            logger.error(f"No template found for {notification.notification_type.code}")
            notification.mark_as_failed("No template")
            return
        
        # Render email
        context = {
            'user': notification.user,
            'notification': notification,
            'data': notification.data,
            'site_url': settings.SITE_URL,
        }
        
        html_content = render_to_string(
            template.email_html_template,
            context
        )
        
        # Send email
        recipient = notification.user.email if notification.user else None
        if recipient:
            # TODO: Integrate with email service
            # For now, just log
            email_log = EmailLog.objects.create(
                recipient_email=recipient,
                subject=template.email_subject_template,
                from_email=settings.DEFAULT_FROM_EMAIL,
                html_content=html_content,
                text_content=template.email_text_template,
                notification=notification,
                status='sent'
            )
            
            notification.mark_as_sent()
            logger.info(f"Email sent to {recipient}")
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Error sending email: {str(e)}")
        if 'notification' in locals():
            notification.mark_as_failed(str(e))


def send_sms_notification(notification_id):
    """
    Send SMS notification.
    
    Args:
        notification_id (UUID): Notification ID
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        # Check if user wants SMS
        if notification.user:
            prefs = NotificationPreference.objects.get_or_create(
                user=notification.user
            )[0]
            
            if not prefs.can_send(
                notification.notification_type.code,
                'sms'
            ):
                notification.mark_as_failed("User opted out")
                return
        
        # Get template
        template = notification.notification_type.templates.filter(
            language='en'
        ).first()
        
        if not template:
            logger.error(f"No template found for {notification.notification_type.code}")
            notification.mark_as_failed("No template")
            return
        
        # Render SMS
        context = {
            'user': notification.user,
            'notification': notification,
            'data': notification.data,
        }
        
        from django.template import Template, Context
        template_obj = Template(template.sms_template)
        message = template_obj.render(Context(context))
        
        # Send SMS
        phone = notification.user.phone if notification.user else None
        if phone:
            # TODO: Integrate with SMS service
            # For now, just log
            sms_log = SMSLog.objects.create(
                phone_number=phone,
                message=message,
                notification=notification,
                status='sent'
            )
            
            notification.mark_as_sent()
            logger.info(f"SMS sent to {phone}")
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Error sending SMS: {str(e)}")
        if 'notification' in locals():
            notification.mark_as_failed(str(e))


def send_push_notification(notification_id):
    """
    Send push notification.
    
    Args:
        notification_id (UUID): Notification ID
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        if not notification.user:
            logger.error("No user for push notification")
            return
        
        # Check if user wants push
        prefs = NotificationPreference.objects.get_or_create(
            user=notification.user
        )[0]
        
        if not prefs.can_send(
            notification.notification_type.code,
            'push'
        ):
            notification.mark_as_failed("User opted out")
            return
        
        # Get user's devices
        devices = UserDevice.objects.filter(
            user=notification.user,
            is_active=True
        )
        
        if not devices.exists():
            notification.mark_as_failed("No devices")
            return
        
        # Get template
        template = notification.notification_type.templates.filter(
            language='en'
        ).first()
        
        if template:
            context = {
                'user': notification.user,
                'notification': notification,
                'data': notification.data,
            }
            
            from django.template import Template, Context
            title_template = Template(template.push_title_template)
            body_template = Template(template.push_body_template)
            
            title = title_template.render(Context(context))
            body = body_template.render(Context(context))
        else:
            title = notification.title
            body = notification.message
        
        # Send to all devices
        for device in devices:
            # TODO: Integrate with push service (FCM/APNS)
            # For now, just log
            push_log = PushNotificationLog.objects.create(
                user=notification.user,
                device_token=device.push_token,
                device_type=device.device_type,
                title=title,
                body=body,
                data=notification.data,
                notification=notification,
                status='sent'
            )
        
        notification.mark_as_sent()
        logger.info(f"Push sent to {devices.count()} devices")
        
    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        logger.error(f"Error sending push: {str(e)}")
        if 'notification' in locals():
            notification.mark_as_failed(str(e))


def create_order_notification(order, event_type):
    """
    Create notification for order events.
    
    Args:
        order (Order): Order object
        event_type (str): Event type (confirmed, shipped, delivered, etc.)
    """
    templates = {
        'confirmed': {
            'type': 'order_confirmed',
            'title': 'Order Confirmed',
            'message': f'Your order #{order.order_number} has been confirmed.'
        },
        'shipped': {
            'type': 'order_shipped',
            'title': 'Order Shipped',
            'message': f'Your order #{order.order_number} has been shipped.'
        },
        'delivered': {
            'type': 'order_delivered',
            'title': 'Order Delivered',
            'message': f'Your order #{order.order_number} has been delivered.'
        },
        'cancelled': {
            'type': 'order_cancelled',
            'title': 'Order Cancelled',
            'message': f'Your order #{order.order_number} has been cancelled.'
        },
    }
    
    if event_type in templates:
        template = templates[event_type]
        create_notification(
            user=order.user,
            notification_type=template['type'],
            title=template['title'],
            message=template['message'],
            data={'order_id': str(order.id), 'order_number': order.order_number},
            related_object=order
        )


def create_payment_notification(transaction, event_type):
    """
    Create notification for payment events.
    
    Args:
        transaction (Transaction): Transaction object
        event_type (str): Event type (success, failed, refunded)
    """
    templates = {
        'success': {
            'type': 'payment_success',
            'title': 'Payment Successful',
            'message': f'Payment of {transaction.amount} {transaction.currency} was successful.'
        },
        'failed': {
            'type': 'payment_failed',
            'title': 'Payment Failed',
            'message': 'Your payment failed. Please try again.'
        },
        'refunded': {
            'type': 'payment_refunded',
            'title': 'Payment Refunded',
            'message': f'Amount of {transaction.amount} {transaction.currency} has been refunded.'
        },
    }
    
    if event_type in templates:
        template = templates[event_type]
        create_notification(
            user=transaction.user,
            notification_type=template['type'],
            title=template['title'],
            message=template['message'],
            data={
                'transaction_id': str(transaction.id),
                'amount': float(transaction.amount),
                'currency': transaction.currency
            },
            related_object=transaction
        )


def create_product_notification(product, event_type):
    """
    Create notification for product events.
    
    Args:
        product (Product): Product object
        event_type (str): Event type (back_in_stock, price_drop, etc.)
    """
    templates = {
        'back_in_stock': {
            'type': 'back_in_stock',
            'title': 'Back in Stock',
            'message': f'{product.name} is back in stock!'
        },
        'price_drop': {
            'type': 'price_drop',
            'title': 'Price Drop',
            'message': f'{product.name} price has dropped to {product.current_price}!'
        },
    }
    
    if event_type in templates:
        template = templates[event_type]
        # This would be sent to users who have wishlisted the product
        # Implementation depends on your wishlist system
        pass


# Celery tasks (commented for future use)
"""
from celery import shared_task

@shared_task
def send_email_task(notification_id):
    return send_email_notification(notification_id)

@shared_task
def send_sms_task(notification_id):
    return send_sms_notification(notification_id)

@shared_task
def send_push_task(notification_id):
    return send_push_notification(notification_id)
"""