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

# Import permissions
from users.permissions import IsAdminOrSeller, IsOwnerOrAdmin, IsAdminOrReadOnly


class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category CRUD operations.
    """
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
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
        
        # Annotate with product count
        queryset = queryset.annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Get all products in this category.
        """
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category', 'brand')
        
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
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    def get_queryset(self):
        """
        Annotate queryset with product count.
        """
        return super().get_queryset().annotate(
            product_count=Count('products', filter=Q(products__is_active=True))
        )
    
    @action(detail=True, methods=['get'])
    def products(self, request, slug=None):
        """
        Get all products from this brand.
        """
        brand = self.get_object()
        products = Product.objects.filter(
            brand=brand,
            is_active=True
        ).select_related('category', 'brand')
        
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
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku', 'brand__name', 'category__name']
    ordering_fields = ['created_at', 'regular_price', 'name', 'sold_count', 'views_count']
    
    def get_permissions(self):
        """
        Return appropriate permissions based on action.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Allow any authenticated user (superuser, admin, seller)
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
        
        # Show only active products to non-admin users
        if not self.request.user.is_authenticated or \
           (self.request.user.user_type not in ['admin', 'seller'] and not self.request.user.is_superuser):
            queryset = queryset.filter(is_active=True, status='active')
        
        # For sellers, show only their products
        if self.request.user.is_authenticated and self.request.user.user_type == 'seller':
            queryset = queryset.filter(seller=self.request.user)
        
        # Select related fields for performance
        queryset = queryset.select_related('category', 'brand', 'seller')
        queryset = queryset.prefetch_related('images', 'variants', 'reviews')
        
        # Annotate with average rating and review count
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set the seller to current user when creating product.
        """
        serializer.save(seller=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product with debug info.
        """
        # Debug print
        print("=" * 50)
        print("CREATE PRODUCT - POST Request")
        print("User:", request.user)
        print("User authenticated:", request.user.is_authenticated)
        print("User is superuser:", request.user.is_superuser)
        print("User type:", getattr(request.user, 'user_type', 'N/A'))
        print("Request data:", request.data)
        print("=" * 50)
        
        return super().create(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Increment view count when product is viewed.
        """
        instance = self.get_object()
        
        # Increment view count
        Product.objects.filter(id=instance.id).update(views_count=F('views_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
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
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured products.
        """
        products = self.get_queryset().filter(featured=True)[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def new_arrivals(self, request):
        """
        Get new arrivals (products from last 30 days).
        """
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        products = self.get_queryset().filter(created_at__gte=thirty_days_ago)[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def best_sellers(self, request):
        """
        Get best selling products.
        """
        products = self.get_queryset().order_by('-sold_count')[:10]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
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
        
        serializer = ProductListSerializer(related, many=True, context={'request': request})
        return Response(serializer.data)


class ProductImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product images.
    """
    
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer
    permission_classes = [IsAdminOrSeller]
    
    def get_queryset(self):
        """
        Filter images by product.
        """
        queryset = super().get_queryset()
        product_id = self.request.query_params.get('product', None)
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        # Sellers can only access their product images
        if self.request.user.user_type == 'seller':
            queryset = queryset.filter(product__seller=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Ensure seller can only add images to their products.
        """
        product_id = self.request.data.get('product')
        if self.request.user.user_type == 'seller':
            product = Product.objects.get(id=product_id, seller=self.request.user)
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
        if not self.request.user.user_type in ['admin', 'moderator']:
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
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def approve(self, request, pk=None):
        """
        Approve a review (admin only).
        """
        review = self.get_object()
        review.is_approved = True
        review.moderated_by = request.user
        review.moderated_at = timezone.now()
        review.save()
        
        return Response({'status': 'review approved'})


class ProductTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product tags.
    """
    
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductAttributeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing product attributes.
    """
    
    queryset = ProductAttribute.objects.filter(is_active=True)
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsAdminOrReadOnly]
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
    
    def get_queryset(self):
        """
        Get active products with annotations.
        """
        queryset = Product.objects.filter(
            is_active=True,
            status='active'
        ).select_related('category', 'brand').prefetch_related('images')
        
        # Annotate with rating
        queryset = queryset.annotate(
            average_rating=Avg('reviews__rating', filter=Q(reviews__is_approved=True)),
            reviews_count=Count('reviews', filter=Q(reviews__is_approved=True))
        )
        
        return queryset