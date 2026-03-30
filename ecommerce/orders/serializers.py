"""
Serializers for Orders module.
Handles data transformation for orders, items, and related models.
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    Order, OrderItem, OrderStatusHistory, OrderPayment,
    OrderCancellation, OrderReturn, OrderInvoice
)
from users.serializers import AddressSerializer, UserProfileSerializer
from products.serializers import ProductListSerializer
from cart.serializers import CouponSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for order items.
    """
    
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'product_name', 'product_sku',
            'product_image', 'variant', 'variant_details', 'quantity',
            'unit_price', 'discount_amount', 'tax_amount', 'total',
            'is_cancelled', 'is_returned', 'cancellation_reason',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_product_details(self, obj):
        """Get minimal product details."""
        return {
            'id': str(obj.product.id),
            'name': obj.product.name,
            'slug': obj.product.slug,
            'sku': obj.product.sku
        }


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for order status history.
    """
    
    changed_by_name = serializers.CharField(source='changed_by.get_full_name', read_only=True)
    
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'status', 'changed_by', 'changed_by_name', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrderPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for order payments.
    """
    
    class Meta:
        model = OrderPayment
        fields = [
            'id', 'transaction_id', 'payment_method', 'amount',
            'status', 'initiated_at', 'completed_at'
        ]
        read_only_fields = ['id', 'initiated_at', 'completed_at']


class OrderListSerializer(serializers.ModelSerializer):
    """
    Simplified order serializer for list views.
    """
    
    customer_name = serializers.CharField(source='user.get_full_name', read_only=True)
    customer_email = serializers.EmailField(source='user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer_name', 'customer_email',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'total_amount', 'paid_amount', 'total_items',
            'created_at', 'delivered_at'
        ]


class OrderDetailSerializer(serializers.ModelSerializer):
    """
    Detailed order serializer with all related data.
    """
    
    customer = UserProfileSerializer(source='user', read_only=True)
    shipping_address = AddressSerializer(read_only=True)
    billing_address = AddressSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    payments = OrderPaymentSerializer(many=True, read_only=True)
    coupon_details = CouponSerializer(source='coupon', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    payment_status_display = serializers.CharField(source='get_payment_status_display', read_only=True)
    
    is_cancellable = serializers.BooleanField(read_only=True)
    is_returnable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'customer', 'shipping_address', 'billing_address',
            'status', 'status_display', 'payment_status', 'payment_status_display',
            'payment_method', 'payment_method_display', 'subtotal', 'shipping_cost',
            'tax_amount', 'discount_amount', 'total_amount', 'paid_amount',
            'coupon', 'coupon_details', 'customer_notes', 'admin_notes',
            'tracking_number', 'shipped_via', 'estimated_delivery', 'delivered_at',
            'invoice_number', 'invoice_url', 'items', 'status_history', 'payments',
            'is_cancellable', 'is_returnable', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer for creating new orders (checkout process).
    """
    
    shipping_address_id = serializers.UUIDField()
    billing_address_id = serializers.UUIDField(required=False)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    customer_notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate(self, data):
        """
        Validate addresses and coupon.
        """
        user = self.context['request'].user
        
        # Validate shipping address
        try:
            shipping_address = user.addresses.get(
                id=data['shipping_address_id'],
                address_type__in=['shipping', 'both']
            )
            data['shipping_address'] = shipping_address
        except:
            raise serializers.ValidationError({
                'shipping_address_id': 'Invalid shipping address'
            })
        
        # Validate billing address
        if data.get('billing_address_id'):
            try:
                billing_address = user.addresses.get(id=data['billing_address_id'])
                data['billing_address'] = billing_address
            except:
                raise serializers.ValidationError({
                    'billing_address_id': 'Invalid billing address'
                })
        else:
            data['billing_address'] = shipping_address
        
        # Validate coupon if provided
        if data.get('coupon_code'):
            from cart.models import Coupon, Cart
            try:
                coupon = Coupon.objects.get(
                    code=data['coupon_code'].upper(),
                    is_active=True
                )
                
                # Get cart for validation
                from cart.views import CartView
                cart_view = CartView()
                cart = cart_view.get_cart(self.context['request'])
                
                can_apply, message = coupon.can_apply_to_cart(cart, user)
                if not can_apply:
                    raise serializers.ValidationError({
                        'coupon_code': message
                    })
                
                data['coupon'] = coupon
                data['discount_amount'] = coupon.calculate_discount(cart)
                
            except Coupon.DoesNotExist:
                raise serializers.ValidationError({
                    'coupon_code': 'Invalid coupon code'
                })
        
        return data


class OrderStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating order status.
    """
    
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
    notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    tracking_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    shipped_via = serializers.CharField(max_length=100, required=False, allow_blank=True)
    estimated_delivery = serializers.DateField(required=False, allow_null=True)


class OrderCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling orders.
    """
    
    reason = serializers.ChoiceField(choices=OrderCancellation.REASON_CHOICES)
    reason_details = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class OrderReturnSerializer(serializers.Serializer):
    """
    Serializer for initiating returns.
    """
    
    order_item_id = serializers.UUIDField()
    reason = serializers.ChoiceField(choices=OrderReturn.RETURN_REASON_CHOICES)
    reason_details = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    images = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list
    )
    is_exchange = serializers.BooleanField(default=False)
    exchange_product_id = serializers.UUIDField(required=False)
    exchange_variant_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """
        Validate return request.
        """
        order = self.context['order']
        
        # Validate order item belongs to order
        try:
            order_item = order.items.get(id=data['order_item_id'])
            if order_item.is_returned:
                raise serializers.ValidationError({
                    'order_item_id': 'Item already returned'
                })
            data['order_item'] = order_item
        except OrderItem.DoesNotExist:
            raise serializers.ValidationError({
                'order_item_id': 'Invalid order item'
            })
        
        # Validate exchange product if exchange requested
        if data.get('is_exchange'):
            if not data.get('exchange_product_id'):
                raise serializers.ValidationError({
                    'exchange_product_id': 'Required for exchange'
                })
            
            from products.models import Product
            try:
                exchange_product = Product.objects.get(
                    id=data['exchange_product_id'],
                    is_active=True
                )
                data['exchange_product'] = exchange_product
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'exchange_product_id': 'Invalid product'
                })
        
        return data


class OrderInvoiceSerializer(serializers.ModelSerializer):
    """
    Serializer for order invoices.
    """
    
    class Meta:
        model = OrderInvoice
        fields = ['id', 'invoice_number', 'invoice_date', 'due_date', 'invoice_url', 'created_at']
        read_only_fields = ['id', 'invoice_number', 'invoice_date', 'created_at']


class OrderAnalyticsSerializer(serializers.Serializer):
    """
    Serializer for order analytics (admin only).
    """
    
    total_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders_by_status = serializers.DictField()
    revenue_by_date = serializers.ListField()
    top_products = serializers.ListField()
    top_customers = serializers.ListField()