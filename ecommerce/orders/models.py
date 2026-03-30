"""
Order models for e-commerce platform.
Handles orders, order items, shipping, and order lifecycle.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import User, Address
from products.models import Product, ProductVariant
from cart.models import Coupon
import uuid


class Order(models.Model):
    """
    Main order model tracking complete order information.
    """
    
    # Order status choices
    STATUS_CHOICES = (
        ('pending', 'Pending'),              # Order placed, payment pending
        ('processing', 'Processing'),        # Payment confirmed, processing
        ('confirmed', 'Confirmed'),          # Order confirmed by seller
        ('shipped', 'Shipped'),              # Order shipped
        ('out_for_delivery', 'Out for Delivery'),  # Out for delivery
        ('delivered', 'Delivered'),           # Order delivered
        ('cancelled', 'Cancelled'),           # Order cancelled
        ('refunded', 'Refunded'),             # Order refunded
        ('failed', 'Failed'),                  # Payment failed
        ('on_hold', 'On Hold'),                # Order on hold
    )
    
    # Payment status choices
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('partially_paid', 'Partially Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    )
    
    # Payment method choices
    PAYMENT_METHOD_CHOICES = (
        ('cash_on_delivery', 'Cash on Delivery'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
        ('bank_transfer', 'Bank Transfer'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    
    # Relationships
    user = models.ForeignKey(
        User, 
        on_delete=models.PROTECT, 
        related_name='orders',
        help_text="Customer who placed the order"
    )
    
    # Addresses
    shipping_address = models.ForeignKey(
        Address, 
        on_delete=models.PROTECT, 
        related_name='shipping_orders',
        help_text="Shipping address for the order"
    )
    billing_address = models.ForeignKey(
        Address, 
        on_delete=models.PROTECT, 
        related_name='billing_orders',
        null=True, 
        blank=True,
        help_text="Billing address (if different from shipping)"
    )
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    # Order totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Applied coupon
    coupon = models.ForeignKey(
        Coupon, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='orders'
    )
    
    # Customer notes
    customer_notes = models.TextField(max_length=1000, blank=True)
    admin_notes = models.TextField(max_length=1000, blank=True, help_text="Internal notes for admin")
    
    # Tracking information
    tracking_number = models.CharField(max_length=100, blank=True)
    shipped_via = models.CharField(max_length=100, blank=True, help_text="Shipping carrier")
    estimated_delivery = models.DateField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    # Invoice
    invoice_number = models.CharField(max_length=50, blank=True)
    invoice_url = models.URLField(max_length=500, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Order metadata (for extensibility)
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional order data")
    
    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_status']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        """
        Generate order number if not provided.
        """
        if not self.order_number:
            # Format: ORD-YYYYMMDD-XXXX
            date_prefix = timezone.now().strftime('%Y%m%d')
            last_order = Order.objects.filter(
                order_number__startswith=f"ORD-{date_prefix}"
            ).order_by('-order_number').first()
            
            if last_order:
                last_number = int(last_order.order_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.order_number = f"ORD-{date_prefix}-{new_number:04d}"
        
        super().save(*args, **kwargs)
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def is_paid(self):
        """Check if order is fully paid."""
        return self.payment_status == 'paid'
    
    @property
    def is_cancellable(self):
        """Check if order can be cancelled."""
        cancellable_statuses = ['pending', 'processing', 'confirmed']
        return self.status in cancellable_statuses
    
    @property
    def is_returnable(self):
        """Check if order can be returned."""
        # Can return within 30 days of delivery
        if self.status == 'delivered' and self.delivered_at:
            days_since_delivery = (timezone.now() - self.delivered_at).days
            return days_since_delivery <= 30
        return False
    
    def update_status(self, new_status, user=None, notes=None):
        """
        Update order status with tracking.
        
        Args:
            new_status (str): New status
            user (User): User making the change
            notes (str): Optional notes about status change
        """
        old_status = self.status
        self.status = new_status
        
        # Set delivered timestamp
        if new_status == 'delivered' and not self.delivered_at:
            self.delivered_at = timezone.now()
        
        self.save()
        
        # Create status history entry
        OrderStatusHistory.objects.create(
            order=self,
            status=new_status,
            changed_by=user,
            notes=notes,
            metadata={'old_status': old_status}
        )
        
        # TODO: Send notifications
        # self.send_status_notification()
    
    def calculate_totals(self):
        """
        Recalculate order totals based on items.
        """
        self.subtotal = sum(item.total_price for item in self.items.all())
        self.total_amount = self.subtotal + self.shipping_cost + self.tax_amount - self.discount_amount
        self.save()


class OrderItem(models.Model):
    """
    Individual items within an order.
    Stores snapshot of product details at time of order.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Product snapshot (store details as they were at order time)
    product_name = models.CharField(max_length=200)
    product_sku = models.CharField(max_length=50)
    product_image = models.URLField(max_length=500, blank=True)
    
    # Pricing snapshot
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Quantity
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Variant details (if applicable)
    variant_details = models.JSONField(default=dict, blank=True)
    
    # Status for individual items
    is_cancelled = models.BooleanField(default=False)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.CharField(max_length=500, blank=True)
    
    # Return/refund
    is_returned = models.BooleanField(default=False)
    returned_at = models.DateTimeField(null=True, blank=True)
    return_reason = models.CharField(max_length=500, blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Item'
        verbose_name_plural = 'Order Items'
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.product_name} in Order {self.order.order_number}"
    
    @property
    def total_price(self):
        """Calculate total price for this item."""
        return (self.unit_price - self.discount_amount) * self.quantity
    
    @property
    def total_tax(self):
        """Calculate total tax for this item."""
        return self.tax_amount * self.quantity
    
    def save(self, *args, **kwargs):
        """
        Populate product snapshot if not provided.
        """
        if not self.product_name and self.product:
            self.product_name = self.product.name
            self.product_sku = self.product.sku
            # Get primary image
            primary_image = self.product.images.filter(is_primary=True).first()
            if primary_image and primary_image.image:
                self.product_image = primary_image.image.url
        
        if self.variant and not self.variant_details:
            self.variant_details = {
                'name': self.variant.name,
                'sku': self.variant.sku,
                'attributes': self.variant.attributes
            }
        
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """
    Track order status changes for audit and customer view.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='order_status_changes'
    )
    notes = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Status History'
        verbose_name_plural = 'Order Status Histories'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.order.order_number} - {self.status} at {self.created_at}"


class OrderPayment(models.Model):
    """
    Track payments for orders (supports partial payments).
    """
    
    PAYMENT_METHOD_CHOICES = Order.PAYMENT_METHOD_CHOICES
    PAYMENT_STATUS_CHOICES = (
        ('initiated', 'Initiated'),
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='initiated')
    
    # Gateway response
    gateway_response = models.JSONField(default=dict, blank=True)
    
    # For refunds
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    refund_reason = models.CharField(max_length=500, blank=True)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Order Payment'
        verbose_name_plural = 'Order Payments'
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['order', 'status']),
        ]
    
    def __str__(self):
        return f"Payment {self.transaction_id} for Order {self.order.order_number}"
    
    def mark_success(self, gateway_response=None):
        """Mark payment as successful."""
        self.status = 'success'
        self.completed_at = timezone.now()
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()
        
        # Update order payment status
        order = self.order
        total_paid = order.payments.filter(status='success').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        order.paid_amount = total_paid
        if total_paid >= order.total_amount:
            order.payment_status = 'paid'
        elif total_paid > 0:
            order.payment_status = 'partially_paid'
        order.save()
    
    def mark_failed(self, gateway_response=None):
        """Mark payment as failed."""
        self.status = 'failed'
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()


class OrderCancellation(models.Model):
    """
    Track order cancellations and refunds.
    """
    
    REASON_CHOICES = (
        ('customer_request', 'Customer Request'),
        ('out_of_stock', 'Out of Stock'),
        ('payment_failed', 'Payment Failed'),
        ('fraud_suspicion', 'Fraud Suspicion'),
        ('other', 'Other'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='cancellation')
    
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    reason_details = models.TextField(max_length=1000, blank=True)
    cancelled_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='cancelled_orders'
    )
    
    # Refund details
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    refund_processed_at = models.DateTimeField(null=True, blank=True)
    
    # Approval workflow
    requires_approval = models.BooleanField(default=False)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_cancellations'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Order Cancellation'
        verbose_name_plural = 'Order Cancellations'
    
    def __str__(self):
        return f"Cancellation for Order {self.order.order_number}"


class OrderReturn(models.Model):
    """
    Track order returns and exchanges.
    """
    
    RETURN_REASON_CHOICES = (
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item Shipped'),
        ('size_issue', 'Size Issue'),
        ('changed_mind', 'Changed Mind'),
        ('quality_issue', 'Quality Issue'),
        ('damaged', 'Damaged in Transit'),
        ('other', 'Other'),
    )
    
    RETURN_STATUS_CHOICES = (
        ('requested', 'Return Requested'),
        ('approved', 'Return Approved'),
        ('rejected', 'Return Rejected'),
        ('pickup_scheduled', 'Pickup Scheduled'),
        ('picked_up', 'Picked Up'),
        ('received', 'Received at Warehouse'),
        ('inspected', 'Inspected'),
        ('refund_processed', 'Refund Processed'),
        ('exchange_initiated', 'Exchange Initiated'),
        ('completed', 'Completed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='returns')
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='returns')
    
    reason = models.CharField(max_length=50, choices=RETURN_REASON_CHOICES)
    reason_details = models.TextField(max_length=1000, blank=True)
    status = models.CharField(max_length=30, choices=RETURN_STATUS_CHOICES, default='requested')
    
    # Images
    images = models.JSONField(default=list, blank=True, help_text="List of return images")
    
    # For exchange
    is_exchange = models.BooleanField(default=False)
    exchange_product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='exchange_orders'
    )
    exchange_variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Pickup details
    pickup_address = models.ForeignKey(
        Address, 
        on_delete=models.PROTECT,
        related_name='pickup_returns'
    )
    pickup_scheduled_at = models.DateTimeField(null=True, blank=True)
    pickup_completed_at = models.DateTimeField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    
    # Refund details
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    refund_transaction_id = models.CharField(max_length=100, blank=True)
    refund_processed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin handling
    handled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handled_returns'
    )
    admin_notes = models.TextField(max_length=1000, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Order Return'
        verbose_name_plural = 'Order Returns'
        indexes = [
            models.Index(fields=['order', 'status']),
        ]
    
    def __str__(self):
        return f"Return for Order {self.order.order_number} - Item {self.order_item.product_name}"


class OrderInvoice(models.Model):
    """
    Store generated invoices for orders.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='invoice')
    
    invoice_number = models.CharField(max_length=50, unique=True, db_index=True)
    invoice_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # File
    invoice_file = models.FileField(upload_to='invoices/', null=True, blank=True)
    invoice_url = models.URLField(max_length=500, blank=True)
    
    # PDF data
    pdf_data = models.BinaryField(null=True, blank=True, help_text="Stored PDF binary")
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Order Invoice'
        verbose_name_plural = 'Order Invoices'
    
    def __str__(self):
        return f"Invoice {self.invoice_number} for Order {self.order.order_number}"
    
    def save(self, *args, **kwargs):
        """
        Generate invoice number if not provided.
        """
        if not self.invoice_number:
            # Format: INV-YYYYMMDD-XXXX
            date_prefix = timezone.now().strftime('%Y%m%d')
            last_invoice = OrderInvoice.objects.filter(
                invoice_number__startswith=f"INV-{date_prefix}"
            ).order_by('-invoice_number').first()
            
            if last_invoice:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            self.invoice_number = f"INV-{date_prefix}-{new_number:04d}"
        
        super().save(*args, **kwargs)