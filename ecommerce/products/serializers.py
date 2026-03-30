"""
Serializers for Product module.
Handles data transformation for all product-related models.
"""

from rest_framework import serializers
from django.db.models import Avg, Count
from .models import (
    Category, Brand, Product, ProductImage, 
    ProductVariant, ProductReview, ProductTag,
    ProductAttribute, ProductAttributeValue
)


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model with nested children support.
    """
    
    product_count = serializers.IntegerField(read_only=True)
    full_path = serializers.CharField(read_only=True)
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent',
            'image', 'icon', 'is_active', 'featured',
            'product_count', 'full_path', 'children',
            'meta_title', 'meta_description', 'meta_keywords',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """
        Get child categories recursively.
        """
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []
    
    def validate_parent(self, value):
        """
        Prevent circular parent relationships.
        """
        if value and value == self.instance:
            raise serializers.ValidationError("Category cannot be its own parent.")
        return value


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Simplified category serializer for list views.
    """
    
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'product_count', 'image']


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for Brand model.
    """
    
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo',
            'cover_image', 'website', 'is_active', 'featured',
            'email', 'phone', 'address', 'product_count',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model.
    """
    
    image_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'image_url', 'thumbnail', 'thumbnail_url',
            'alt_text', 'is_primary', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_image_url(self, obj):
        """Get full URL for image."""
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None
    
    def get_thumbnail_url(self, obj):
        """Get full URL for thumbnail."""
        request = self.context.get('request')
        if obj.thumbnail and request:
            return request.build_absolute_uri(obj.thumbnail.url)
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductVariant model.
    """
    
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    sale_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'attributes', 'price_adjustment',
            'sale_price_adjustment', 'price', 'sale_price',
            'stock_quantity', 'image', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductReview model with user details.
    """
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    helpful_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'title', 'content', 'rating', 'pros', 'cons',
            'images', 'is_approved', 'is_featured', 'user_name',
            'user_email', 'helpful_count', 'not_helpful_count',
            'helpful_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'is_approved', 'is_featured', 'helpful_count',
            'not_helpful_count', 'created_at', 'updated_at'
        ]
    
    def get_helpful_percentage(self, obj):
        """Calculate helpful percentage."""
        total = obj.helpful_count + obj.not_helpful_count
        if total > 0:
            return (obj.helpful_count / total) * 100
        return 0


class ProductListSerializer(serializers.ModelSerializer):
    """
    Simplified product serializer for list views.
    """
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True, default='')
    primary_image = serializers.SerializerMethodField()
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'category', 'category_name',
            'brand', 'brand_name', 'primary_image', 'regular_price',
            'sale_price', 'current_price', 'discount_percentage',
            'average_rating', 'reviews_count', 'in_stock',
            'featured', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image URL."""
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Detailed product serializer for product detail views.
    """
    
    category = CategoryListSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()
    tags = serializers.StringRelatedField(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.get_full_name', read_only=True)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.FloatField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    reviews_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku', 'barcode', 'description',
            'short_description', 'product_type', 'category', 'brand',
            'seller', 'seller_name', 'regular_price', 'sale_price',
            'cost_price', 'current_price', 'discount_percentage',
            'stock_quantity', 'low_stock_threshold', 'track_inventory',
            'allow_backorders', 'weight', 'length', 'width', 'height',
            'status', 'is_active', 'featured', 'images', 'variants',
            'attributes', 'tags', 'average_rating', 'reviews_count',
            'reviews', 'in_stock', 'views_count', 'sold_count',
            'tax_class', 'is_taxable', 'meta_title', 'meta_description',
            'meta_keywords', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = [
            'id', 'views_count', 'sold_count', 'created_at',
            'updated_at', 'published_at'
        ]
    
    def get_reviews(self, obj):
        """Get approved reviews for the product."""
        reviews = obj.reviews.filter(is_approved=True)[:5]  # Limit to 5 most recent
        return ProductReviewSerializer(reviews, many=True, context=self.context).data
    
    def get_attributes(self, obj):
        """Get product attributes with values."""
        attributes = {}
        for attr_value in obj.attribute_values.select_related('attribute').all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes:
                attributes[attr_name] = {
                    'type': attr_value.attribute.attribute_type,
                    'values': []
                }
            attributes[attr_name]['values'].append({
                'id': attr_value.id,
                'value': attr_value.value,
                'extra_data': attr_value.extra_data
            })
        return attributes


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    """
    
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'barcode', 'description', 'short_description',
            'product_type', 'category', 'brand', 'regular_price',
            'sale_price', 'cost_price', 'stock_quantity', 'low_stock_threshold',
            'track_inventory', 'allow_backorders', 'weight', 'length',
            'width', 'height', 'status', 'is_active', 'featured',
            'tax_class', 'is_taxable', 'meta_title', 'meta_description',
            'meta_keywords'
        ]
    
    def validate(self, data):
        """
        Custom validation for product data.
        """
        # Validate sale price <= regular price
        if data.get('sale_price') and data.get('regular_price'):
            if data['sale_price'] >= data['regular_price']:
                raise serializers.ValidationError({
                    'sale_price': 'Sale price must be less than regular price.'
                })
        
        # Validate stock quantity for tracked inventory
        if data.get('track_inventory') and data.get('stock_quantity', 0) < 0:
            raise serializers.ValidationError({
                'stock_quantity': 'Stock quantity cannot be negative.'
            })
        
        return data


class ProductReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating product reviews.
    """
    
    class Meta:
        model = ProductReview
        fields = ['title', 'content', 'rating', 'pros', 'cons', 'images']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5."""
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value


class ProductAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductAttribute model.
    """
    
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name', 'attribute_type', 'options', 'is_active', 'order']
        read_only_fields = ['id']


class ProductTagSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductTag model.
    """
    
    class Meta:
        model = ProductTag
        fields = ['id', 'name', 'slug']
        read_only_fields = ['id', 'slug']