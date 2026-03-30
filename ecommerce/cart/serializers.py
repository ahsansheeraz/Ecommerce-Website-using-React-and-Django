"""
Serializers for Cart module.
Handles data transformation for cart, items, and coupons.
"""

from rest_framework import serializers
from .models import Cart, CartItem, SavedForLater, Coupon, CartCoupon
from products.models import Product, ProductVariant
from products.serializers import ProductListSerializer


class CartItemProductSerializer(serializers.ModelSerializer):
    """
    Simplified product serializer for cart items.
    """
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'sku', 'regular_price', 'sale_price', 'current_price']
        read_only_fields = ['id', 'name', 'slug', 'sku']


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for cart items with product details.
    """
    
    product_details = serializers.SerializerMethodField()
    variant_details = serializers.SerializerMethodField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_details', 'variant', 'variant_details',
            'quantity', 'unit_price', 'discount_amount', 'total',
            'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'unit_price', 'created_at', 'updated_at']
    
    def get_product_details(self, obj):
        """Get product details."""
        return CartItemProductSerializer(obj.product, context=self.context).data
    
    def get_variant_details(self, obj):
        """Get variant details if exists."""
        if obj.variant:
            return {
                'id': str(obj.variant.id),
                'name': obj.variant.name,
                'sku': obj.variant.sku,
                'attributes': obj.variant.attributes
            }
        return None
    
    def validate_quantity(self, value):
        """
        Validate quantity against stock.
        """
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value
    
    def validate(self, data):
        """
        Validate stock availability.
        """
        product = data.get('product', getattr(self.instance, 'product', None))
        variant = data.get('variant', getattr(self.instance, 'variant', None))
        quantity = data.get('quantity', getattr(self.instance, 'quantity', 1))
        
        if product and product.track_inventory:
            available_stock = product.stock_quantity
            if variant:
                available_stock = variant.stock_quantity
            
            if quantity > available_stock and not product.allow_backorders:
                raise serializers.ValidationError(
                    f"Only {available_stock} items available in stock"
                )
        
        return data


class CartItemCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding items to cart.
    """
    
    class Meta:
        model = CartItem
        fields = ['product', 'variant', 'quantity', 'notes']
    
    def validate(self, data):
        """
        Validate product and quantity.
        """
        product = data.get('product')
        variant = data.get('variant')
        quantity = data.get('quantity', 1)
        
        # Check if product is active
        if not product.is_active or product.status != 'active':
            raise serializers.ValidationError("Product is not available for purchase")
        
        # Check variant belongs to product
        if variant and variant.product != product:
            raise serializers.ValidationError("Variant does not belong to this product")
        
        # Check stock
        if product.track_inventory:
            available_stock = product.stock_quantity
            if variant:
                available_stock = variant.stock_quantity
            
            if quantity > available_stock and not product.allow_backorders:
                raise serializers.ValidationError(
                    f"Only {available_stock} items available in stock"
                )
        
        return data


class CartSerializer(serializers.ModelSerializer):
    """
    Complete cart serializer with items and calculations.
    """
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    applied_coupons = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'session_id', 'is_active', 'is_converted',
            'items', 'total_items', 'subtotal', 'total_discount',
            'total', 'applied_coupons', 'created_at', 'updated_at', 'expires_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_applied_coupons(self, obj):
        """Get applied coupons with details."""
        coupons = obj.applied_coupons.all()
        return [
            {
                'code': coupon.coupon.code,
                'discount_type': coupon.coupon.discount_type,
                'discount_amount': float(coupon.discount_amount)
            }
            for coupon in coupons
        ]
    
    def to_representation(self, instance):
        """Add cart summary to representation."""
        data = super().to_representation(instance)
        data['summary'] = instance.get_cart_summary()
        return data


class SavedForLaterSerializer(serializers.ModelSerializer):
    """
    Serializer for saved for later items.
    """
    
    product_details = ProductListSerializer(source='product', read_only=True)
    variant_details = serializers.SerializerMethodField()
    
    class Meta:
        model = SavedForLater
        fields = ['id', 'product', 'product_details', 'variant', 'variant_details', 'notes', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_variant_details(self, obj):
        """Get variant details if exists."""
        if obj.variant:
            return {
                'id': str(obj.variant.id),
                'name': obj.variant.name,
                'attributes': obj.variant.attributes
            }
        return None


class CouponSerializer(serializers.ModelSerializer):
    """
    Serializer for coupons (admin use).
    """
    
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'description', 'discount_type', 'discount_value',
            'max_discount_amount', 'usage_limit', 'usage_limit_per_user',
            'used_count', 'min_cart_amount', 'min_quantity',
            'applicable_products', 'applicable_categories', 'excluded_products',
            'start_date', 'end_date', 'is_active', 'is_first_order_only',
            'is_valid', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'used_count', 'created_at', 'updated_at']


class CouponApplySerializer(serializers.Serializer):
    """
    Serializer for applying coupon to cart.
    """
    
    code = serializers.CharField(max_length=50)
    
    def validate_code(self, value):
        """
        Validate coupon exists and is active.
        """
        try:
            coupon = Coupon.objects.get(code=value.upper(), is_active=True)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code")
        
        # Check if coupon is valid
        if not coupon.is_valid:
            raise serializers.ValidationError("Coupon is expired or inactive")
        
        return value.upper()


class CartItemUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating cart item quantity.
    """
    
    quantity = serializers.IntegerField(min_value=0, max_value=999)
    
    def validate_quantity(self, value):
        """Validate quantity."""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


class CartMergeSerializer(serializers.Serializer):
    """
    Serializer for merging guest cart with user cart after login.
    """
    
    session_id = serializers.CharField(max_length=100)
    
    def validate_session_id(self, value):
        """Validate session cart exists."""
        if not Cart.objects.filter(session_id=value, is_active=True).exists():
            raise serializers.ValidationError("No active cart found for this session")
        return value