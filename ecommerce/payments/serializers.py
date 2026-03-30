"""
Serializers for Payments module.
Handles data transformation for transactions, payment methods, etc.
"""

from rest_framework import serializers
from orders.models import Order
#from users.models import User
from .models import (
    PaymentGateway, Transaction, SavedPaymentMethod,
    Payout, PaymentWebhookLog, RefundRequest
)
from orders.serializers import OrderListSerializer


class PaymentGatewaySerializer(serializers.ModelSerializer):
    """
    Serializer for PaymentGateway (admin only).
    """
    
    class Meta:
        model = PaymentGateway
        fields = [
            'id', 'name', 'display_name', 'api_key', 'api_secret',
            'webhook_secret', 'base_url', 'test_mode', 'config',
            'is_active', 'is_default', 'supports_refunds',
            'supports_subscriptions', 'supports_international',
            'transaction_fee_percentage', 'transaction_fee_fixed',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'api_key': {'write_only': True},
            'api_secret': {'write_only': True},
            'webhook_secret': {'write_only': True},
        }


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    """
    
    gateway_name = serializers.CharField(source='gateway.display_name', read_only=True)
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_id', 'order', 'order_number',
            'user', 'user_email', 'user_name', 'gateway', 'gateway_name',
            'transaction_type', 'amount', 'currency', 'status',
            'gateway_transaction_id', 'payment_method',
            'payment_method_details', 'customer_email',
            'customer_phone', 'customer_name', 'error_code',
            'error_message', 'initiated_at', 'processed_at',
            'completed_at'
        ]
        read_only_fields = ['id', 'transaction_id', 'initiated_at', 'processed_at', 'completed_at']
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.get_full_name()


class TransactionDetailSerializer(TransactionSerializer):
    """
    Detailed transaction serializer with additional data.
    """
    
    refunds = serializers.SerializerMethodField()
    order_details = OrderListSerializer(source='order', read_only=True)
    
    class Meta(TransactionSerializer.Meta):
        fields = TransactionSerializer.Meta.fields + [
            'request_data', 'response_data', 'webhook_data',
            'refunds', 'order_details', 'metadata'
        ]
    
    def get_refunds(self, obj):
        """Get refund transactions."""
        refunds = obj.refunds.all()
        return TransactionSerializer(refunds, many=True).data


class TransactionCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new transactions.
    """
    
    order_id = serializers.UUIDField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=Transaction.CURRENCY_CHOICES, default='USD')
    payment_method = serializers.CharField(max_length=50)
    payment_method_id = serializers.CharField(required=False, allow_blank=True)
    save_payment_method = serializers.BooleanField(default=False)
    
    # Customer details
    customer_email = serializers.EmailField()
    customer_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    customer_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    # Billing address
    billing_address = serializers.JSONField(default=dict, required=False)
    
    # Metadata
    metadata = serializers.JSONField(default=dict, required=False)
    
    def validate(self, data):
        """Validate order and amount."""
        if data.get('order_id'):
            try:
                order = Order.objects.get(id=data['order_id'])
                if order.user != self.context['request'].user:
                    raise serializers.ValidationError("Order does not belong to you")
                
                # Validate amount matches order total
                if data['amount'] != order.total_amount:
                    raise serializers.ValidationError({
                        'amount': f'Amount should be {order.total_amount}'
                    })
                
                data['order'] = order
            except Order.DoesNotExist:
                raise serializers.ValidationError({'order_id': 'Invalid order'})
        
        return data


class SavedPaymentMethodSerializer(serializers.ModelSerializer):
    """
    Serializer for saved payment methods.
    """
    
    gateway_name = serializers.CharField(source='gateway.display_name', read_only=True)
    
    class Meta:
        model = SavedPaymentMethod
        fields = [
            'id', 'payment_type', 'display_name', 'card_last4',
            'card_brand', 'card_exp_month', 'card_exp_year',
            'upi_id', 'wallet_name', 'bank_name', 'account_last4',
            'is_default', 'gateway', 'gateway_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PayoutSerializer(serializers.ModelSerializer):
    """
    Serializer for payouts.
    """
    
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Payout
        fields = [
            'id', 'payout_id', 'user', 'user_email', 'user_name',
            'amount', 'currency', 'status', 'bank_account_holder',
            'bank_name', 'bank_account_number', 'bank_ifsc_code',
            'bank_swift_code', 'wallet_type', 'wallet_account',
            'gateway_payout_id', 'period_start', 'period_end',
            'fee_amount', 'net_amount', 'notes', 'created_at',
            'processed_at', 'completed_at'
        ]
        read_only_fields = ['id', 'payout_id', 'created_at', 'processed_at', 'completed_at']


class RefundRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for refund requests.
    """
    
    order_number = serializers.CharField(source='order.order_number', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    transaction_id = serializers.CharField(source='transaction.transaction_id', read_only=True)
    
    class Meta:
        model = RefundRequest
        fields = [
            'id', 'order', 'order_number', 'user', 'user_email',
            'user_name', 'transaction', 'transaction_id', 'amount',
            'reason', 'reason_details', 'images', 'status',
            'admin_notes', 'created_at', 'handled_at'
        ]
        read_only_fields = ['id', 'status', 'admin_notes', 'created_at', 'handled_at']


class RefundRequestCreateSerializer(serializers.Serializer):
    """
    Serializer for creating refund requests.
    """
    
    order_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.ChoiceField(choices=RefundRequest.REASON_CHOICES)
    reason_details = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list
    )
    
    def validate(self, data):
        """Validate refund request."""
        try:
            order = Order.objects.get(
                id=data['order_id'],
                user=self.context['request'].user
            )
            
            # Check if order is eligible for refund
            if order.status not in ['delivered', 'cancelled']:
                raise serializers.ValidationError(
                    "Order is not eligible for refund"
                )
            
            # Check if already requested
            if RefundRequest.objects.filter(
                order=order,
                status__in=['pending', 'approved']
            ).exists():
                raise serializers.ValidationError(
                    "Refund already requested for this order"
                )
            
            # Get transaction
            transaction = Transaction.objects.filter(
                order=order,
                status='success'
            ).first()
            
            if not transaction:
                raise serializers.ValidationError(
                    "No successful transaction found for this order"
                )
            
            data['order'] = order
            data['transaction'] = transaction
            data['user'] = self.context['request'].user
            
        except Order.DoesNotExist:
            raise serializers.ValidationError({'order_id': 'Invalid order'})
        
        return data


class PaymentWebhookLogSerializer(serializers.ModelSerializer):
    """
    Serializer for webhook logs (admin only).
    """
    
    gateway_name = serializers.CharField(source='gateway.name', read_only=True)
    
    class Meta:
        model = PaymentWebhookLog
        fields = [
            'id', 'gateway', 'gateway_name', 'event_type',
            'event_id', 'headers', 'body', 'is_processed',
            'error_message', 'transaction', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Stripe-specific serializers (commented for future use)
"""
class StripePaymentIntentSerializer(serializers.Serializer):
    # Serializer for Stripe Payment Intent creation.
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=Transaction.CURRENCY_CHOICES, default='usd')
    payment_method = serializers.CharField(required=False)
    customer_id = serializers.CharField(required=False)
    setup_future_usage = serializers.CharField(required=False)
    metadata = serializers.JSONField(default=dict)


class StripeRefundSerializer(serializers.Serializer):
    # Serializer for Stripe refund creation.
    
    payment_intent_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = serializers.CharField(required=False)
"""


# PayPal-specific serializers (commented for future use)
"""
class PayPalOrderSerializer(serializers.Serializer):
    # Serializer for PayPal order creation.
    
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.ChoiceField(choices=Transaction.CURRENCY_CHOICES, default='USD')
    description = serializers.CharField(required=False)
    return_url = serializers.URLField()
    cancel_url = serializers.URLField()


class PayPalCaptureSerializer(serializers.Serializer):
    # Serializer for PayPal payment capture.
    
    order_id = serializers.CharField()
"""