"""
Django admin configuration for Product module.
Backup admin interface (main admin will be in React).
"""

from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import (
    Category, Brand, Product, ProductImage,
    ProductVariant, ProductReview, ProductTag,
    ProductAttribute, ProductAttributeValue
)


class ProductImageInline(admin.TabularInline):
    """Inline admin for product images."""
    model = ProductImage
    extra = 1
    fields = ['image', 'thumbnail', 'alt_text', 'is_primary', 'order']
    readonly_fields = ['thumbnail_preview']
    
    def thumbnail_preview(self, obj):
        """Show thumbnail preview in admin."""
        if obj.thumbnail:
            return format_html('<img src="{}" width="50" height="50" />', obj.thumbnail.url)
        return "No thumbnail"
    thumbnail_preview.short_description = "Preview"


class ProductVariantInline(admin.TabularInline):
    """Inline admin for product variants."""
    model = ProductVariant
    extra = 1
    fields = ['name', 'sku', 'attributes', 'price_adjustment', 'stock_quantity', 'is_active']


class ProductAttributeValueInline(admin.TabularInline):
    """Inline admin for product attribute values."""
    model = ProductAttributeValue
    extra = 1
    fields = ['attribute', 'value', 'extra_data']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category."""
    
    list_display = ['name', 'parent', 'is_active', 'featured', 'product_count']
    list_filter = ['is_active', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['parent']
    
    def product_count(self, obj):
        """Display product count."""
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    """Admin configuration for Brand."""
    
    list_display = ['name', 'is_active', 'featured', 'website', 'product_count']
    list_filter = ['is_active', 'featured']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def product_count(self, obj):
        """Display product count."""
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for Product."""
    
    list_display = [
        'name', 'sku', 'category', 'brand', 'regular_price',
        'sale_price', 'stock_quantity', 'status', 'is_active',
        'featured', 'created_at'
    ]
    list_filter = ['status', 'is_active', 'featured', 'category', 'brand', 'product_type']
    search_fields = ['name', 'sku', 'description']
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ['category', 'brand', 'seller']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'barcode', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'brand', 'seller', 'product_type', 'tags')
        }),
        ('Pricing', {
            'fields': ('regular_price', 'sale_price', 'cost_price')
        }),
        ('Inventory', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'track_inventory', 'allow_backorders')
        }),
        ('Shipping', {
            'fields': ('weight', 'length', 'width', 'height')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Tax', {
            'fields': ('tax_class', 'is_taxable'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ProductImageInline, ProductVariantInline, ProductAttributeValueInline]
    
    actions = ['make_active', 'make_inactive', 'mark_featured']
    
    def make_active(self, request, queryset):
        """Make selected products active."""
        queryset.update(is_active=True, status='active')
    make_active.short_description = "Mark selected products as active"
    
    def make_inactive(self, request, queryset):
        """Make selected products inactive."""
        queryset.update(is_active=False, status='inactive')
    make_inactive.short_description = "Mark selected products as inactive"
    
    def mark_featured(self, request, queryset):
        """Mark selected products as featured."""
        queryset.update(featured=True)
    mark_featured.short_description = "Mark selected products as featured"


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    """Admin configuration for ProductReview."""
    
    list_display = ['product', 'user', 'rating', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['product__name', 'user__email', 'title', 'content']
    raw_id_fields = ['product', 'user', 'moderated_by']
    date_hierarchy = 'created_at'
    
    actions = ['approve_reviews', 'reject_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews."""
        queryset.update(is_approved=True, moderated_by=request.user, moderated_at=timezone.now())
    approve_reviews.short_description = "Approve selected reviews"
    
    def reject_reviews(self, request, queryset):
        """Reject selected reviews."""
        queryset.update(is_approved=False, moderated_by=request.user, moderated_at=timezone.now())
    reject_reviews.short_description = "Reject selected reviews"


@admin.register(ProductTag)
class ProductTagAdmin(admin.ModelAdmin):
    """Admin configuration for ProductTag."""
    
    list_display = ['name', 'slug']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    """Admin configuration for ProductAttribute."""
    
    list_display = ['name', 'attribute_type', 'is_active', 'order']
    list_filter = ['attribute_type', 'is_active']
    search_fields = ['name']