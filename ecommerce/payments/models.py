"""
Payment models for e-commerce platform.
Handles payment gateways, transactions, refunds, and payment methods.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User
from orders.models import Order
import uuid
import json


class PaymentGateway(models.Model):
    """
    Payment gateway configuration model.
    Stores settings for different payment providers.
    """
    
    GATEWAY_TYPES = (
        ('stripe', 'Stripe'),
        ('paypal', 'PayPal'),
        ('razorpay', 'Razorpay'),
        ('instamojo', 'Instamojo'),
        ('cashfree', 'Cashfree'),
        ('phonepe', 'PhonePe'),
        ('google_pay', 'Google Pay'),
        ('apple_pay', 'Apple Pay'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash_on_delivery', 'Cash on Delivery'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=GATEWAY_TYPES, unique=True)
    display_name = models.CharField(max_length=100)
    
    # Gateway credentials (encrypted in production)
    api_key = models.CharField(max_length=500, blank=True)
    api_secret = models.CharField(max_length=500, blank=True)
    webhook_secret = models.CharField(max_length=500, blank=True)
    
    # Gateway endpoints
    base_url = models.URLField(max_length=500, blank=True)
    test_mode = models.BooleanField(default=True)
    
    # Configuration as JSON for gateway-specific settings
    config = models.JSONField(default=dict, blank=True, help_text="Gateway-specific configuration")
    
    # Status
    is_active = models.BooleanField(default=False)
    is_default = models.BooleanField(default=False)
    
    # Supported features
    supports_refunds = models.BooleanField(default=True)
    supports_subscriptions = models.BooleanField(default=False)
    supports_international = models.BooleanField(default=False)
    
    # Fee structure
    transaction_fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    transaction_fee_fixed = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Payment Gateway'
        verbose_name_plural = 'Payment Gateways'
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({'Test' if self.test_mode else 'Live'})"
    
    def save(self, *args, **kwargs):
        """Ensure only one default gateway."""
        if self.is_default:
            PaymentGateway.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """
    Main transaction model for all payment transactions.
    """
    
    TRANSACTION_TYPES = (
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('capture', 'Capture'),
        ('void', 'Void'),
    )
    
    STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
        ('disputed', 'Disputed'),
    )
    
    CURRENCY_CHOICES = (
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        ('INR', 'Indian Rupee'),
        ('PKR', 'Pakistani Rupee'),
        ('AED', 'UAE Dirham'),
        ('SAR', 'Saudi Riyal'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Relationships
    order = models.ForeignKey(
        Order, 
        on_delete=models.PROTECT, 
        related_name='payment_transactions',
        null=True, 
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='transactions')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    
    # Gateway transaction IDs
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    gateway_order_id = models.CharField(max_length=255, blank=True)
    gateway_payment_id = models.CharField(max_length=255, blank=True)
    gateway_subscription_id = models.CharField(max_length=255, blank=True)
    
    # Payment method details
    payment_method = models.CharField(max_length=50, blank=True)  # card, upi, wallet, etc.
    payment_method_details = models.JSONField(default=dict, blank=True)  # Masked card number, etc.
    
    # Customer details
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    customer_name = models.CharField(max_length=200, blank=True)
    
    # Billing address
    billing_address = models.JSONField(default=dict, blank=True)
    
    # Gateway request/response
    request_data = models.JSONField(default=dict, blank=True)
    response_data = models.JSONField(default=dict, blank=True)
    webhook_data = models.JSONField(default=dict, blank=True)
    
    # Error tracking
    error_code = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    
    # For refunds (if this is a refund transaction)
    parent_transaction = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='refunds'
    )
    refund_reason = models.CharField(max_length=500, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['gateway_transaction_id']),
            models.Index(fields=['order', 'status']),
            models.Index(fields=['user', '-initiated_at']),
            models.Index(fields=['status', 'initiated_at']),
        ]
        ordering = ['-initiated_at']
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} {self.currency} - {self.status}"
    
    def save(self, *args, **kwargs):
        """
        Generate transaction ID if not provided.
        """
        if not self.transaction_id:
            # Format: TXN-YYYYMMDD-XXXXXXXX
            import random
            import string
            
            date_prefix = timezone.now().strftime('%Y%m%d')
            random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            self.transaction_id = f"TXN-{date_prefix}-{random_str}"
        
        super().save(*args, **kwargs)
    
    def mark_success(self, gateway_response=None):
        """Mark transaction as successful."""
        self.status = 'success'
        self.completed_at = timezone.now()
        if gateway_response:
            self.response_data = gateway_response
        self.save()
        
        # Update order payment status
        if self.order:
            from orders.models import OrderPayment
            OrderPayment.objects.create(
                order=self.order,
                transaction_id=self.transaction_id,
                payment_method=self.payment_method,
                amount=self.amount,
                status='success',
                gateway_response=gateway_response,
                completed_at=self.completed_at
            )
    
    def mark_failed(self, error_code=None, error_message=None):
        """Mark transaction as failed."""
        self.status = 'failed'
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        self.save()
    
    def process_refund(self, amount=None, reason=""):
        """
        Process refund for this transaction.
        
        Args:
            amount (decimal): Refund amount (None for full refund)
            reason (str): Reason for refund
            
        Returns:
            Transaction: Refund transaction object
        """
        refund_amount = amount or self.amount
        
        # Create refund transaction
        refund = Transaction.objects.create(
            order=self.order,
            user=self.user,
            gateway=self.gateway,
            transaction_type='refund',
            amount=refund_amount,
            currency=self.currency,
            status='initiated',
            parent_transaction=self,
            refund_reason=reason,
            payment_method=self.payment_method,
            customer_email=self.customer_email,
            customer_phone=self.customer_phone,
            customer_name=self.customer_name
        )
        
        # TODO: Call gateway refund API
        # refund_response = gateway.process_refund(self, refund_amount)
        
        return refund


class SavedPaymentMethod(models.Model):
    """
    Saved payment methods for users (cards, wallets, etc.)
    """
    
    PAYMENT_TYPE_CHOICES = (
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
        ('netbanking', 'Net Banking'),
        ('bank_account', 'Bank Account'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_payment_methods')
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT)
    
    # Payment method details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    method_id = models.CharField(max_length=255, help_text="Gateway's payment method ID")
    
    # Display information (masked)
    display_name = models.CharField(max_length=100, help_text="e.g., •••• 4242")
    card_last4 = models.CharField(max_length=4, blank=True)
    card_brand = models.CharField(max_length=50, blank=True)  # Visa, Mastercard, etc.
    card_exp_month = models.CharField(max_length=2, blank=True)
    card_exp_year = models.CharField(max_length=4, blank=True)
    
    # UPI/Wallet details
    upi_id = models.CharField(max_length=100, blank=True)
    wallet_name = models.CharField(max_length=50, blank=True)
    
    # Bank account details
    bank_name = models.CharField(max_length=100, blank=True)
    account_last4 = models.CharField(max_length=4, blank=True)
    
    # Status
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Billing address
    billing_address = models.JSONField(default=dict, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Saved Payment Method'
        verbose_name_plural = 'Saved Payment Methods'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['method_id']),
        ]
    
    def __str__(self):
        return f"{self.display_name} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        """Ensure only one default payment method per user."""
        if self.is_default:
            SavedPaymentMethod.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)


class Payout(models.Model):
    """
    Payouts to sellers/vendors.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payout_id = models.CharField(max_length=100, unique=True, db_index=True)
    
    # Recipient
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='payouts')
    
    # Payout details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Bank account details
    bank_account_holder = models.CharField(max_length=200)
    bank_name = models.CharField(max_length=200)
    bank_account_number = models.CharField(max_length=100)  # Encrypted
    bank_ifsc_code = models.CharField(max_length=20, blank=True)
    bank_swift_code = models.CharField(max_length=20, blank=True)
    
    # For wallets
    wallet_type = models.CharField(max_length=50, blank=True)
    wallet_account = models.CharField(max_length=200, blank=True)
    
    # Gateway transaction ID
    gateway_payout_id = models.CharField(max_length=255, blank=True)
    
    # Period covered
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Orders included in this payout
    orders = models.ManyToManyField(Order, related_name='payouts', blank=True)
    
    # Fee
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Notes
    notes = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"Payout {self.payout_id} - {self.user.email} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Generate payout ID if not provided."""
        if not self.payout_id:
            # Format: PAY-YYYYMMDD-XXXX
            date_prefix = timezone.now().strftime('%Y%m%d')
            last_payout = Payout.objects.filter(
                payout_id__startswith=f"PAY-{date_prefix}"
            ).order_by('-payout_id').first()
            
            if last_payout:
                last_number = int(last_payout.payout_id.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.payout_id = f"PAY-{date_prefix}-{new_number:04d}"
        
        self.net_amount = self.amount - self.fee_amount
        super().save(*args, **kwargs)


class PaymentWebhookLog(models.Model):
    """
    Log all webhook requests from payment gateways.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.CASCADE, related_name='webhook_logs')
    
    # Webhook data
    event_type = models.CharField(max_length=100, blank=True)
    event_id = models.CharField(max_length=255, blank=True)
    
    # Request details
    headers = models.JSONField(default=dict)
    body = models.JSONField(default=dict)
    
    # Processing result
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    # Related transaction
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhook_logs'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Payment Webhook Log'
        verbose_name_plural = 'Payment Webhook Logs'
        indexes = [
            models.Index(fields=['gateway', '-created_at']),
            models.Index(fields=['event_id']),
        ]
    
    def __str__(self):
        return f"Webhook {self.event_type} from {self.gateway.name} at {self.created_at}"


class RefundRequest(models.Model):
    """
    Refund requests from customers (for admin approval).
    """
    
    REASON_CHOICES = (
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item Shipped'),
        ('quality_issue', 'Quality Issue'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('processed', 'Refund Processed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refund_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='refund_requests')
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='refund_requests',
        help_text="Original transaction to refund"
    )
    
    # Refund details
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_details = models.TextField(max_length=1000, blank=True)
    
    # Evidence
    images = models.JSONField(default=list, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Admin handling
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_refunds'
    )
    admin_notes = models.TextField(max_length=1000, blank=True)
    handled_at = models.DateTimeField(null=True, blank=True)
    
    # Refund transaction (when processed)
    refund_transaction = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='original_refund_request'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Refund Request'
        verbose_name_plural = 'Refund Requests'
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order', 'status']),
        ]
    
    def __str__(self):
        return f"Refund Request for Order {self.order.order_number} - {self.amount}"
    
    def approve(self, admin_user, notes=""):
        """Approve refund request."""
        self.status = 'approved'
        self.handled_by = admin_user
        self.admin_notes = notes
        self.handled_at = timezone.now()
        self.save()
        
        # Process refund
        refund_txn = self.transaction.process_refund(
            amount=self.amount,
            reason=f"Refund request approved: {self.reason}"
        )
        
        self.refund_transaction = refund_txn
        self.save()
        
        # TODO: Notify user
        # send_refund_approved_notification(self)
        
        return refund_txn
    
    def reject(self, admin_user, reason):
        """Reject refund request."""
        self.status = 'rejected'
        self.handled_by = admin_user
        self.admin_notes = reason
        self.handled_at = timezone.now()
        self.save()
        
        # TODO: Notify user
        # send_refund_rejected_notification(self)