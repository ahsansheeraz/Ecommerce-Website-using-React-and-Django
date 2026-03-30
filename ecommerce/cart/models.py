"""
Cart models for e-commerce platform.
Handles shopping cart, cart items, and related functionality.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from products.models import Product, ProductVariant
import uuid

class Cart(models.Model):
    """
    Shopping cart model for storing user's selected items.
    Supports both authenticated users and guest sessions.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Cart owner - either authenticated user or session based
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    
    # Cart status
    is_active = models.BooleanField(default=True, help_text="Cart is active and can be modified")
    is_converted = models.BooleanField(default=False, help_text="Cart has been converted to order")
    
    # Cart metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True, help_text="Cart expiry time for abandoned carts")
    
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_id', 'is_active']),
            models.Index(fields=['expires_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        if self.user:
            return f"Cart - {self.user.email} ({self.created_at.date()})"
        return f"Cart - Guest ({self.session_id})"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def subtotal(self):
        """Calculate cart subtotal before discounts."""
        total = 0
        for item in self.items.all():
            total += item.total_price
        return total
    
    @property
    def total_discount(self):
        """Calculate total discount from all items."""
        total = 0
        for item in self.items.all():
            if item.discount_amount:
                total += item.discount_amount * item.quantity
        return total
    
    @property
    def total(self):
        """Calculate final cart total after all discounts."""
        return self.subtotal - self.total_discount
    
    def get_cart_summary(self):
        """
        Get complete cart summary with all calculations.
        """
        return {
            'total_items': self.total_items,
            'subtotal': float(self.subtotal),
            'total_discount': float(self.total_discount),
            'total': float(self.total),
            'items': [
                {
                    'id': str(item.id),
                    'product_id': str(item.product.id),
                    'product_name': item.product.name,
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total_price': float(item.total_price),
                    'discount': float(item.discount_amount) if item.discount_amount else 0
                }
                for item in self.items.all()
            ]
        }
    
    def clear_cart(self):
        """Remove all items from cart."""
        self.items.all().delete()
        self.save()


class CartItem(models.Model):
    """
    Individual items in shopping cart.
    Tracks product, quantity, pricing, and any applied discounts.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    variant = models.ForeignKey(
        ProductVariant, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='cart_items'
    )
    
    # Quantity
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Price snapshot (store price at time of adding to cart)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Discount per unit if any"
    )
    
    # Additional data
    notes = models.CharField(max_length=500, blank=True, help_text="Customer notes for this item")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Cart Item'
        verbose_name_plural = 'Cart Items'
        indexes = [
            models.Index(fields=['cart', 'product']),
        ]
        unique_together = ['cart', 'product', 'variant']  # Prevent duplicate items
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name} in cart"
    
    @property
    def total_price(self):
        """Calculate total price for this item (unit price * quantity)."""
        return self.unit_price * self.quantity
    
    @property
    def total_with_discount(self):
        """Calculate total after discount."""
        if self.discount_amount:
            return (self.unit_price - self.discount_amount) * self.quantity
        return self.total_price
    
    def save(self, *args, **kwargs):
        """
        Override save to set unit price from product if not provided.
        """
        if not self.unit_price:
            # Get current price from product (consider sale price)
            self.unit_price = self.product.current_price
        
        super().save(*args, **kwargs)


class SavedForLater(models.Model):
    """
    Items saved for later (wishlist within cart).
    Allows users to move items from cart to saved for later.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    notes = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Saved for Later'
        verbose_name_plural = 'Saved for Later'
        indexes = [
            models.Index(fields=['user', 'created_at']),
        ]
        unique_together = ['user', 'product', 'variant']
    
    def __str__(self):
        return f"{self.product.name} saved by {self.user.email}"


class Coupon(models.Model):
    """
    Discount coupons that can be applied to cart.
    Supports various discount types and restrictions.
    """
    
    DISCOUNT_TYPE_CHOICES = (
        ('percentage', 'Percentage Discount'),
        ('fixed', 'Fixed Amount'),
        ('free_shipping', 'Free Shipping'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Coupon identification
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=255, blank=True)
    
    # Discount details
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Percentage or fixed amount based on type"
    )
    max_discount_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Maximum discount amount for percentage coupons"
    )
    
    # Usage limits
    usage_limit = models.PositiveIntegerField(default=1, help_text="Total number of times coupon can be used")
    usage_limit_per_user = models.PositiveIntegerField(default=1, help_text="Times per user")
    used_count = models.PositiveIntegerField(default=0)
    
    # Minimum requirements
    min_cart_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Minimum cart total required"
    )
    min_quantity = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Minimum quantity of items required"
    )
    
    # Applicable products/categories
    applicable_products = models.ManyToManyField(
        Product, 
        blank=True,
        help_text="Specific products coupon applies to"
    )
    applicable_categories = models.ManyToManyField(
        'products.Category', 
        blank=True,
        help_text="Categories coupon applies to"
    )
    excluded_products = models.ManyToManyField(
        Product, 
        blank=True,
        related_name='excluded_from_coupons',
        help_text="Products excluded from coupon"
    )
    
    # Validity period
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Status
    is_active = models.BooleanField(default=True)
    is_first_order_only = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Coupon'
        verbose_name_plural = 'Coupons'
        indexes = [
            models.Index(fields=['code', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.get_discount_type_display()}"
    
    @property
    def is_valid(self):
        """Check if coupon is currently valid."""
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.start_date <= now <= self.end_date and
            (not self.usage_limit or self.used_count < self.usage_limit)
        )
    
    def can_apply_to_cart(self, cart, user=None):
        """
        Check if coupon can be applied to given cart.
        
        Args:
            cart (Cart): Cart to check
            user (User): User applying coupon
            
        Returns:
            tuple: (bool, message)
        """
        # Check basic validity
        if not self.is_valid:
            return False, "Coupon is expired or inactive"
        
        # Check cart total requirement
        if self.min_cart_amount and cart.subtotal < self.min_cart_amount:
            return False, f"Minimum cart amount of {self.min_cart_amount} required"
        
        # Check user usage limit
        if user and self.usage_limit_per_user:
            from orders.models import Order
            user_usage = Order.objects.filter(
                user=user,
                coupon=self
            ).count()
            if user_usage >= self.usage_limit_per_user:
                return False, "You have already used this coupon maximum times"
        
        # Check if first order only
        if self.is_first_order_only and user:
            from orders.models import Order
            if Order.objects.filter(user=user).exists():
                return False, "This coupon is for first order only"
        
        return True, "Coupon can be applied"
    
    def calculate_discount(self, cart):
        """
        Calculate discount amount for given cart.
        
        Args:
            cart (Cart): Cart to calculate discount for
            
        Returns:
            float: Discount amount
        """
        if self.discount_type == 'fixed':
            return min(self.discount_value, cart.subtotal)
        
        elif self.discount_type == 'percentage':
            discount = cart.subtotal * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return discount
        
        elif self.discount_type == 'free_shipping':
            # This will be handled at shipping calculation
            return 0
        
        return 0


class CartCoupon(models.Model):
    """
    Tracks coupons applied to cart.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='applied_coupons')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Cart Coupon'
        verbose_name_plural = 'Cart Coupons'
        unique_together = ['cart', 'coupon']
    
    def __str__(self):
        return f"{self.coupon.code} applied to cart"


class AbandonedCart(models.Model):
    """
    Tracks abandoned carts for recovery campaigns.
    """
    
    STATUS_CHOICES = (
        ('new', 'Newly Abandoned'),
        ('reminded', 'Reminder Sent'),
        ('recovered', 'Recovered'),
        ('lost', 'Lost'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='abandoned_record')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    # Recovery tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    reminder_count = models.PositiveIntegerField(default=0)
    
    # Cart snapshot
    cart_snapshot = models.JSONField(help_text="Snapshot of cart items when abandoned")
    cart_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Recovery data
    recovered_at = models.DateTimeField(null=True, blank=True)
    recovered_order = models.ForeignKey(
        'orders.Order',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recovered_cart'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Abandoned Cart'
        verbose_name_plural = 'Abandoned Carts'
        indexes = [
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Abandoned cart - {self.user.email if self.user else 'Guest'}"