"""
Django admin configuration for Payments module.
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    PaymentGateway, Transaction, SavedPaymentMethod,
    Payout, PaymentWebhookLog, RefundRequest
)


@admin.register(PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentGateway."""
    
    list_display = ['name', 'display_name', 'is_active', 'is_default', 'test_mode', 'created_at']
    list_filter = ['is_active', 'is_default', 'test_mode']
    search_fields = ['name', 'display_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'is_active', 'is_default')
        }),
        ('API Credentials', {
            'fields': ('api_key', 'api_secret', 'webhook_secret'),
            'classes': ('collapse',)
        }),
        ('Configuration', {
            'fields': ('base_url', 'test_mode', 'config')
        }),
        ('Features', {
            'fields': ('supports_refunds', 'supports_subscriptions', 'supports_international')
        }),
        ('Fees', {
            'fields': ('transaction_fee_percentage', 'transaction_fee_fixed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Admin configuration for Transaction."""
    
    list_display = [
        'transaction_id', 'user_email', 'amount', 'currency',
        'status', 'payment_method', 'initiated_at', 'view_link'
    ]
    list_filter = ['status', 'transaction_type', 'payment_method', 'currency', 'initiated_at']
    search_fields = ['transaction_id', 'gateway_transaction_id', 'user__email', 'customer_email']
    readonly_fields = [
        'transaction_id', 'initiated_at', 'processed_at', 'completed_at',
        'request_data', 'response_data', 'webhook_data'
    ]
    raw_id_fields = ['user', 'order', 'gateway', 'parent_transaction']
    date_hierarchy = 'initiated_at'
    
    fieldsets = (
        (None, {
            'fields': ('transaction_id', 'user', 'order', 'gateway')
        }),
        ('Transaction Details', {
            'fields': ('transaction_type', 'amount', 'currency', 'status', 'payment_method')
        }),
        ('Gateway IDs', {
            'fields': ('gateway_transaction_id', 'gateway_order_id', 'gateway_payment_id')
        }),
        ('Customer Information', {
            'fields': ('customer_email', 'customer_phone', 'customer_name', 'billing_address')
        }),
        ('Payment Method', {
            'fields': ('payment_method_details',)
        }),
        ('Error Information', {
            'fields': ('error_code', 'error_message')
        }),
        ('Refund Information', {
            'fields': ('parent_transaction', 'refund_reason')
        }),
        ('Data', {
            'fields': ('request_data', 'response_data', 'webhook_data', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'processed_at', 'completed_at', 'updated_at')
        }),
    )
    
    def user_email(self, obj):
        """Get user email."""
        return obj.user.email
    user_email.short_description = 'User'
    user_email.admin_order_field = 'user__email'
    
    def view_link(self, obj):
        """Link to view transaction."""
        return format_html('<a href="{}">View</a>", obj.id')
    view_link.short_description = 'Actions'


@admin.register(SavedPaymentMethod)
class SavedPaymentMethodAdmin(admin.ModelAdmin):
    """Admin configuration for SavedPaymentMethod."""
    
    list_display = ['user', 'display_name', 'payment_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['payment_type', 'is_default', 'is_active']
    search_fields = ['user__email', 'display_name', 'card_last4']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'gateway']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Admin configuration for Payout."""
    
    list_display = ['payout_id', 'user', 'amount', 'status', 'period_start', 'period_end', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['payout_id', 'user__email']
    readonly_fields = ['payout_id', 'created_at', 'processed_at', 'completed_at']
    raw_id_fields = ['user']
    filter_horizontal = ['orders']
    
    actions = ['mark_as_processing', 'mark_as_completed']
    
    def mark_as_processing(self, request, queryset):
        """Mark payouts as processing."""
        queryset.update(status='processing', processed_at=timezone.now())
    mark_as_processing.short_description = "Mark selected as Processing"
    
    def mark_as_completed(self, request, queryset):
        """Mark payouts as completed."""
        queryset.update(status='completed', completed_at=timezone.now())
    mark_as_completed.short_description = "Mark selected as Completed"


@admin.register(PaymentWebhookLog)
class PaymentWebhookLogAdmin(admin.ModelAdmin):
    """Admin configuration for PaymentWebhookLog."""
    
    list_display = ['gateway', 'event_type', 'is_processed', 'created_at']
    list_filter = ['gateway', 'is_processed', 'created_at']
    search_fields = ['event_id', 'event_type']
    readonly_fields = ['headers', 'body', 'error_message', 'created_at']


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    """Admin configuration for RefundRequest."""
    
    list_display = ['order', 'user', 'amount', 'reason', 'status', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['order__order_number', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['order', 'user', 'transaction', 'handled_by', 'refund_transaction']
    
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        """Approve refund requests."""
        for refund in queryset:
            refund.approve(request.user, "Approved by admin")
    approve_requests.short_description = "Approve selected refund requests"
    
    def reject_requests(self, request, queryset):
        """Reject refund requests."""
        for refund in queryset:
            refund.reject(request.user, "Rejected by admin")
    reject_requests.short_description = "Reject selected refund requests"