"""
Django admin configuration for Cart module.
Backup admin interface for monitoring carts and coupons.
"""

from django.contrib import admin
from django.db import models
from django.utils import timezone
from .models import Cart, CartItem, SavedForLater, Coupon, CartCoupon, AbandonedCart


class CartItemInline(admin.TabularInline):
    """Inline admin for cart items."""
    model = CartItem
    extra = 0
    readonly_fields = ['product', 'variant', 'quantity', 'unit_price', 'total_price']
    fields = ['product', 'variant', 'quantity', 'unit_price', 'total_price']
    
    def total_price(self, obj):
        """Display total price."""
        return obj.total_price
    total_price.short_description = 'Total'


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart."""
    
    list_display = ['id', 'user', 'session_id', 'total_items', 'subtotal', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_converted', 'created_at']
    search_fields = ['user__email', 'session_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_items', 'subtotal', 'total']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('id', 'user', 'session_id')
        }),
        ('Status', {
            'fields': ('is_active', 'is_converted', 'expires_at')
        }),
        ('Totals', {
            'fields': ('total_items', 'subtotal', 'total')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def total_items(self, obj):
        """Display total items."""
        return obj.total_items
    total_items.short_description = 'Total Items'
    
    def subtotal(self, obj):
        """Display subtotal."""
        return f"${obj.subtotal}"
    subtotal.short_description = 'Subtotal'
    
    def total(self, obj):
        """Display total."""
        return f"${obj.total}"
    total.short_description = 'Total'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem."""
    
    list_display = ['id', 'cart', 'product', 'quantity', 'unit_price', 'total_price', 'created_at']
    list_filter = ['created_at']
    search_fields = ['product__name', 'cart__user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'total_price']
    raw_id_fields = ['cart', 'product', 'variant']
    
    def total_price(self, obj):
        """Display total price."""
        return f"${obj.total_price}"
    total_price.short_description = 'Total'


@admin.register(SavedForLater)
class SavedForLaterAdmin(admin.ModelAdmin):
    """Admin configuration for SavedForLater."""
    
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
    raw_id_fields = ['user', 'product', 'variant']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    """Admin configuration for Coupon."""
    
    list_display = [
        'code', 'discount_type', 'discount_value', 'usage_limit',
        'used_count', 'is_active', 'start_date', 'end_date'
    ]
    list_filter = ['discount_type', 'is_active', 'is_first_order_only']
    search_fields = ['code', 'description']
    readonly_fields = ['used_count', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_products', 'applicable_categories', 'excluded_products']
    
    fieldsets = (
        (None, {
            'fields': ('code', 'description', 'is_active')
        }),
        ('Discount', {
            'fields': ('discount_type', 'discount_value', 'max_discount_amount')
        }),
        ('Usage Limits', {
            'fields': ('usage_limit', 'usage_limit_per_user', 'used_count', 'is_first_order_only')
        }),
        ('Minimum Requirements', {
            'fields': ('min_cart_amount', 'min_quantity')
        }),
        ('Applicability', {
            'fields': ('applicable_products', 'applicable_categories', 'excluded_products')
        }),
        ('Validity Period', {
            'fields': ('start_date', 'end_date')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    actions = ['activate_coupons', 'deactivate_coupons']
    
    def activate_coupons(self, request, queryset):
        """Activate selected coupons."""
        queryset.update(is_active=True)
    activate_coupons.short_description = "Activate selected coupons"
    
    def deactivate_coupons(self, request, queryset):
        """Deactivate selected coupons."""
        queryset.update(is_active=False)
    deactivate_coupons.short_description = "Deactivate selected coupons"


@admin.register(CartCoupon)
class CartCouponAdmin(admin.ModelAdmin):
    """Admin configuration for CartCoupon."""
    
    list_display = ['cart', 'coupon', 'discount_amount', 'applied_at']
    list_filter = ['applied_at']
    search_fields = ['cart__user__email', 'coupon__code']
    readonly_fields = ['applied_at']


@admin.register(AbandonedCart)
class AbandonedCartAdmin(admin.ModelAdmin):
    """Admin configuration for AbandonedCart."""
    
    list_display = ['id', 'user', 'cart_total', 'status', 'reminder_count', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['cart_snapshot', 'created_at', 'updated_at']
    raw_id_fields = ['cart', 'user', 'recovered_order']
    
    actions = ['mark_as_lost', 'send_reminder']
    
    def mark_as_lost(self, request, queryset):
        """Mark abandoned carts as lost."""
        queryset.update(status='lost')
    mark_as_lost.short_description = "Mark selected as lost"
    
    def send_reminder(self, request, queryset):
        """Send reminder emails for abandoned carts."""
        # This would integrate with email service
        queryset.update(
            status='reminded',
            reminder_sent_at=timezone.now(),
            reminder_count=models.F('reminder_count') + 1
        )
    send_reminder.short_description = "Send reminder emails"