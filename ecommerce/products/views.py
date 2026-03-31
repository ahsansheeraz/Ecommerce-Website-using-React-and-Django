"""
Views for Product module.
Handles all HTTP requests for products, categories, brands, and reviews.
"""

from rest_framework import generics, permissions, status, filters, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db.models import Q, Count, Avg, F
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

# Import all models
from .models import (
    Category, Brand, Product, ProductImage,
    ProductVariant, ProductReview, ProductTag,
    ProductAttribute
)

# Import all serializers
from .serializers import (
    CategorySerializer, BrandSerializer, ProductListSerializer,
    ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductReviewSerializer, ProductReviewCreateSerializer,
    ProductImageSerializer, ProductVariantSerializer,
    ProductTagSerializer, ProductAttributeSerializer
)

# Import filters
from .filters import ProductFilter

# Import permissions from users app
from users.permissions import IsAdminUser, IsAdminOrSeller, IsSellerOrAdmin, IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.
    """
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']  # ✅ Add default ordering to fix pagination warning
    
    def get_queryset(self):
        """
        Optionally filter by parent category.
        """
        queryset = super().get_queryset()
        parent = self.request.query_params.get('parent', None)
        
        if parent == 'null':
            queryset = queryset.filter(parent__isnull=True)
        elif parent:
            queryset = queryset.filter(parent__slug=parent)
        
        # ✅ Don't annotate here - use serializer method instead
        return queryset
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def products(self, request, slug=None):
        """
        Get all products in this category.
        """
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True,
            status='active'
        ).select_related('category', 'brand')
        
        # Annotate with rating
        products = products.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Brand CRUD operations.
    """
    
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']  # ✅ Add default ordering
    
    def get_queryset(self):
        """
        Return queryset without annotation.
        """
        return super().get_queryset()  # ✅ Remove annotation
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def products(self, request, slug=None):
        """
        Get all products from this brand.
        """
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            is_active=True,
            status='active'
        ).select_related('category', 'brand')
        
        # Annotate with rating
        products = products.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        page = self.paginate_queryset(products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product CRUD operations with filtering and search.
    """
    
    queryset = Product.objects.all()
    lookup_field = 'slug'
    permission_classes = [permissions.AllowAny]  # Base permission, will override in methods
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'brand__name', 'category__name']
    ordering_fields = ['created_at', 'regular_price', 'name', 'sold_count', 'views_count']
    ordering = ['-created_at']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only sellers and admins can modify products
            return [permissions.IsAuthenticated(), IsSellerOrAdmin()]
        elif self.action in ['add_review', 'mark_review_helpful']:
            # Authenticated users can add reviews
            return [permissions.IsAuthenticated()]
        else:
            # Anyone can view products
            return [permissions.AllowAny()]
    
    def get_serializer_class(self):
        """
        Return different serializers for list, detail, and create/update.
        """
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_queryset(self):
        """
        Filter products based on user permissions and query params.
        """
        queryset = Product.objects.all()
        
        # For non-authenticated users or customers, show only active products
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_active=True, status='active')
        elif self.request.user.user_type == 'customer':
            queryset = queryset.filter(is_active=True, status='active')
        elif self.request.user.user_type == 'seller':
            # Sellers see their own products plus active products from others
            seller_products = queryset.filter(seller=self.request.user)
            active_products = queryset.filter(is_active=True, status='active').exclude(seller=self.request.user)
            queryset = seller_products | active_products
        # Admin can see all products
        
        # Select related fields for performance
        queryset = queryset.select_related('category', 'brand', 'seller')
        queryset = queryset.prefetch_related('images', 'variants', 'tags')
        
        # Annotate with average rating and review count
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        """
        Set the seller to current user when creating product.
        """
        serializer.save(seller=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Increment view count when product is viewed.
        """
        instance = self.get_object()
        
        # Increment view count only for active products
        if instance.is_active and instance.status == 'active':
            Product.objects.filter(id=instance.id).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_review(self, request, slug=None):
        """
        Add a review to the product.
        """
        product = self.get_object()
        
        # Check if user already reviewed this product
        if ProductReview.objects.filter(product=product, user=request.user).exists():
            return Response({
                'error': 'You have already reviewed this product.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ProductReviewCreateSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(
                product=product,
                user=request.user
            )
            
            return Response(
                ProductReviewSerializer(review, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def mark_review_helpful(self, request, slug=None):
        """
        Mark a review as helpful.
        """
        review_id = request.data.get('review_id')
        is_helpful = request.data.get('is_helpful', True)
        
        try:
            review = ProductReview.objects.get(id=review_id, product=self.get_object())
            
            # Check if user already voted
            from .models import ProductReviewHelpful
            vote, created = ProductReviewHelpful.objects.get_or_create(
                review=review,
                user=request.user,
                defaults={'is_helpful': is_helpful}
            )
            
            if not created:
                # Update existing vote
                if vote.is_helpful != is_helpful:
                    if is_helpful:
                        review.helpful_count += 1
                        review.not_helpful_count -= 1
                    else:
                        review.helpful_count -= 1
                        review.not_helpful_count += 1
                    vote.is_helpful = is_helpful
                    vote.save()
            else:
                # New vote
                if is_helpful:
                    review.helpful_count += 1
                else:
                    review.not_helpful_count += 1
            
            review.save()
            
            return Response({
                'helpful_count': review.helpful_count,
                'not_helpful_count': review.not_helpful_count
            })
            
        except ProductReview.DoesNotExist:
            return Response({
                'error': 'Review not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def featured(self, request):
        """
        Get featured products.
        """
        products = self.get_queryset().filter(featured=True, is_active=True, status='active')[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def new_arrivals(self, request):
        """
        Get new arrivals (products from last 30 days).
        """
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        products = self.get_queryset().filter(
            created_at__gte=thirty_days_ago,
            is_active=True,
            status='active'
        )[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def best_sellers(self, request):
        """
        Get best selling products.
        """
        products = self.get_queryset().filter(is_active=True, status='active').order_by('-sold_count')[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def related_products(self, request, slug=None):
        """
        Get related products based on category and tags.
        """
        product = self.get_object()
        
        # Find products in same category with similar tags
        related = Product.objects.filter(
            Q(category=product.category) |
            Q(tags__in=product.tags.all())
        ).exclude(
            id=product.id
        ).filter(
            is_active=True,
            status='active'
        ).distinct()[:8]
        
        # Annotate with rating
        related = related.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        serializer = ProductListSerializer(related, many=True, context={'request': request})
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product images.
    """
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsSellerOrAdmin]  # ✅ Fixed: Use existing permission
    
    def get_queryset(self):
        """
        Filter images by product.
        """
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Sellers can only access their product images
        if self.request.user.is_authenticated and self.request.user.user_type == 'seller':
            queryset = queryset.filter(product__seller=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Ensure seller can only add images to their products.
        """
        product_id = self.request.data.get('product')
        if product_id:
            product = Product.objects.get(id=product_id)
            if self.request.user.user_type == 'seller' and product.seller != self.request.user:
                raise permissions.PermissionDenied("You can only add images to your own products.")
        serializer.save()


class ProductReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product reviews.
    """
    
    queryset = ProductReview.objects.all()
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter reviews based on user permissions.
        """
        queryset = super().get_queryset()
        
        # Regular users see only approved reviews
        if not self.request.user.is_authenticated or \
           self.request.user.user_type not in ['admin', 'moderator']:
            queryset = queryset.filter(is_approved=True)
        
        # Filter by product
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Users can see their own reviews
        user_id = self.request.query_params.get('user', None)
        if user_id and self.request.user.user_type == 'admin':
            queryset = queryset.filter(user_id=user_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set user when creating review.
        """
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a review (admin only).
        """
        review = self.get_object()
        review.is_approved = True
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.save()
        
        return Response({'status': 'review approved', 'message': 'Review approved successfully'})


class ProductTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product tags.
    """
    
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAdminOrReadOnly]  # ✅ Fixed: Use existing permission
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product attributes.
    """
    
    queryset = ProductAttribute.objects.filter(is_active=True)
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAdminOrReadOnly]  # ✅ Fixed: Use existing permission
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['order', 'name']


class ProductSearchView(generics.ListAPIView):
    """
    Advanced product search endpoint.
    """
    
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'brand__name', 'category__name', 'tags__name']
    ordering_fields = ['-created_at', '-sold_count', 'regular_price', '-average_rating']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get active products with annotations.
        """
        queryset = Product.objects.filter(
            is_active=True,
            status='active'
        ).select_related('category', 'brand').prefetch_related('images', 'tags')
        
        # Annotate with rating
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        return queryset