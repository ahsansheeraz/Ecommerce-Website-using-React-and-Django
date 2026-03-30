"""
Custom filters for Product module.
Provides advanced filtering capabilities for products.
"""

import django_filters
from django.db.models import Q, Min, Max
from .models import Product, Category, Brand
from django.db.models import F


class ProductFilter(django_filters.FilterSet):
    """
    Advanced filter set for products.
    """
    
    # Price range filters
    min_price = django_filters.NumberFilter(field_name="regular_price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="regular_price", lookup_expr='lte')
    
    # Category filters
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    category_slug = django_filters.CharFilter(field_name='category__slug')
    
    # Brand filters
    brand = django_filters.ModelChoiceFilter(queryset=Brand.objects.all())
    brand_slug = django_filters.CharFilter(field_name='brand__slug')
    
    # Status filters
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    on_sale = django_filters.BooleanFilter(method='filter_on_sale')
    featured = django_filters.BooleanFilter(field_name='featured')
    
    # Rating filter
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    
    # Attribute filters
    attributes = django_filters.CharFilter(method='filter_attributes')
    
    # Date filters
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    
    class Meta:
        model = Product
        fields = [
            'category', 'brand', 'status', 'is_active',
            'featured', 'product_type', 'tax_class'
        ]
    
    def filter_in_stock(self, queryset, name, value):
        """
        Filter products that are in stock.
        """
        if value:
            return queryset.filter(
                Q(track_inventory=False) |
                Q(stock_quantity__gt=0) |
                Q(allow_backorders=True)
            )
        return queryset.filter(
            track_inventory=True,
            stock_quantity=0,
            allow_backorders=False
        )
    
    def filter_on_sale(self, queryset, name, value):
        """
        Filter products that are on sale.
        """
        if value:
            return queryset.filter(
                sale_price__isnull=False,
                sale_price__lt=F('regular_price')
            )
        return queryset.filter(
            Q(sale_price__isnull=True) |
            Q(sale_price__gte=F('regular_price'))
        )
    
    def filter_min_rating(self, queryset, name, value):
        """
        Filter products with minimum average rating.
        """
        from django.db.models import Avg, Count
        
        return queryset.annotate(
            avg_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True))
        ).filter(avg_rating__gte=value)
    
    def filter_attributes(self, queryset, name, value):
        """
        Filter by product attributes (format: attr_name:value,attr_name2:value2)
        """
        if not value:
            return queryset
        
        # Parse attribute filters
        attr_filters = value.split(',')
        for attr_filter in attr_filters:
            if ':' in attr_filter:
                attr_name, attr_value = attr_filter.split(':', 1)
                queryset = queryset.filter(
                    attribute_values__attribute__name=attr_name,
                    attribute_values__value=attr_value
                )
        
        return queryset.distinct()


class CategoryFilter(django_filters.FilterSet):
    """
    Filter set for categories.
    """
    
    has_products = django_filters.BooleanFilter(method='filter_has_products')
    
    class Meta:
        model = Category
        fields = ['is_active', 'featured', 'parent']
    
    def filter_has_products(self, queryset, name, value):
        """
        Filter categories that have active products.
        """
        from django.db.models import Count
        
        queryset = queryset.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )
        
        if value:
            return queryset.filter(product_count__gt=0)
        return queryset.filter(product_count=0)