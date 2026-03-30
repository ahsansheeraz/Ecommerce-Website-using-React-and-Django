"""
Django admin configuration for Orders module.
Backup admin interface for monitoring orders.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderPayment,
    OrderCancellation, OrderReturn, OrderInvoice
)


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price']
    fields = ['product', 'product_name', 'quantity', 'unit_price', 'total_price', 'is_cancelled']
    
    def total_price(self, obj):
        """Display total price."""
        return f"${obj.total_price}"
    total_price.short_description = 'Total'


class OrderStatusHistoryInline(admin.TabularInline):
    """Inline admin for status history."""
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['status', 'changed_by', 'notes', 'created_at']
    fields = ['status', 'changed_by', 'notes', 'created_at']
    ordering = ['-created_at']


class OrderPaymentInline(admin.TabularInline):
    """Inline admin for payments."""
    model = OrderPayment
    extra = 0
    readonly_fields = ['transaction_id', 'payment_method', 'amount', 'status', 'completed_at']
    fields = ['transaction_id', 'payment_method', 'amount', 'status', 'completed_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order."""
    
    list_display = [
        'order_number', 'user_email', 'total_amount', 'status',
        'payment_status', 'payment_method', 'created_at', 'view_link'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = [
        'order_number', 'subtotal', 'total_amount', 'paid_amount',
        'created_at', 'updated_at', 'invoice_link'
    ]
    inlines = [OrderItemInline, OrderStatusHistoryInline, OrderPaymentInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'payment_status', 'payment_method')
        }),
        ('Addresses', {
            'fields': ('shipping_address', 'billing_address')
        }),
        ('Financial', {
            'fields': ('subtotal', 'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount', 'paid_amount')
        }),
        ('Tracking', {
            'fields': ('tracking_number', 'shipped_via', 'estimated_delivery', 'delivered_at')
        }),
        ('Notes', {
            'fields': ('customer_notes', 'admin_notes')
        }),
        ('Invoice', {
            'fields': ('invoice_number', 'invoice_url', 'invoice_link')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        """Get user email."""
        return obj.user.email
    user_email.short_description = 'Customer'
    user_email.admin_order_field = 'user__email'
    
    def view_link(self, obj):
        """Link to view order in frontend."""
        return format_html('<a href="/admin/orders/order/{}/change/">Edit</a>', obj.id)
    view_link.short_description = 'Actions'
    
    def invoice_link(self, obj):
        """Link to invoice if available."""
        if obj.invoice_url:
            return format_html('<a href="{}" target="_blank">View Invoice</a>', obj.invoice_url)
        return 'No invoice'
    invoice_link.short_description = 'Invoice'
    
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered']
    
    def mark_as_processing(self, request, queryset):
        """Mark orders as processing."""
        queryset.update(status='processing')
    mark_as_processing.short_description = "Mark selected as Processing"
    
    def mark_as_shipped(self, request, queryset):
        """Mark orders as shipped."""
        queryset.update(status='shipped')
    mark_as_shipped.short_description = "Mark selected as Shipped"
    
    def mark_as_delivered(self, request, queryset):
        """Mark orders as delivered."""
        queryset.update(status='delivered', delivered_at=timezone.now())
    mark_as_delivered.short_description = "Mark selected as Delivered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem."""
    
    list_display = ['id', 'order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['is_cancelled', 'is_returned']
    search_fields = ['order__order_number', 'product_name', 'product_sku']
    readonly_fields = ['total_price']
    raw_id_fields = ['order', 'product', 'variant']
    
    def total_price(self, obj):
        """Display total price."""
        return f"${obj.total_price}"
    total_price.short_description = 'Total'


@admin.register(OrderCancellation)
class OrderCancellationAdmin(admin.ModelAdmin):
    """Admin configuration for OrderCancellation."""
    
    list_display = ['order', 'reason', 'refund_amount', 'requires_approval', 'created_at']
    list_filter = ['reason', 'requires_approval', 'created_at']
    search_fields = ['order__order_number']
    readonly_fields = ['created_at', 'processed_at']
    raw_id_fields = ['order', 'cancelled_by', 'approved_by']
    
    actions = ['approve_cancellation', 'reject_cancellation']
    
    def approve_cancellation(self, request, queryset):
        """Approve cancellation requests."""
        for cancellation in queryset:
            cancellation.approved_by = request.user
            cancellation.approved_at = timezone.now()
            cancellation.processed_at = timezone.now()
            cancellation.save()
            
            # Update order
            order = cancellation.order
            order.update_status('cancelled', user=request.user)
            
            # Process refund if paid
            if order.is_paid:
                # TODO: Process refund
                pass
    approve_cancellation.short_description = "Approve selected cancellations"
    
    def reject_cancellation(self, request, queryset):
        """Reject cancellation requests."""
        queryset.delete()
    reject_cancellation.short_description = "Reject selected cancellations"


@admin.register(OrderReturn)
class OrderReturnAdmin(admin.ModelAdmin):
    """Admin configuration for OrderReturn."""
    
    list_display = ['order', 'order_item', 'reason', 'status', 'is_exchange', 'created_at']
    list_filter = ['status', 'reason', 'is_exchange', 'created_at']
    search_fields = ['order__order_number', 'order_item__product_name']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    raw_id_fields = ['order', 'order_item', 'handled_by']
    
    actions = ['approve_returns', 'reject_returns']
    
    def approve_returns(self, request, queryset):
        """Approve return requests."""
        queryset.update(
            status='approved',
            handled_by=request.user,
            admin_notes='Approved by admin'
        )
    approve_returns.short_description = "Approve selected returns"
    
    def reject_returns(self, request, queryset):
        """Reject return requests."""
        queryset.update(
            status='rejected',
            handled_by=request.user
        )
    reject_returns.short_description = "Reject selected returns"


@admin.register(OrderInvoice)
class OrderInvoiceAdmin(admin.ModelAdmin):
    """Admin configuration for OrderInvoice."""
    
    list_display = ['invoice_number', 'order', 'invoice_date', 'created_at']
    list_filter = ['invoice_date']
    search_fields = ['invoice_number', 'order__order_number']
    readonly_fields = ['invoice_number', 'invoice_date', 'created_at']