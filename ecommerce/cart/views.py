"""
Views for Cart module.
Handles all cart operations: add, remove, update, apply coupon, etc.
"""

from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone

from django.db import transaction

from rest_framework import filters   
#from products import filters as products_filters 
from .models import Cart, CartItem, SavedForLater, Coupon, CartCoupon
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    SavedForLaterSerializer, CouponSerializer, CouponApplySerializer,
    CartItemUpdateSerializer, CartMergeSerializer
)
from products.models import Product, ProductVariant
from rest_framework.permissions import IsAuthenticated


class CartView(APIView):
    """
    Main cart view for retrieving and managing cart.
    """
    
    permission_classes = [permissions.AllowAny]  # Allow guests
    
    def get_cart(self, request):
        """
        Get or create cart for current user/session.
        """
        # For authenticated users
        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(
                user=request.user,
                is_active=True,
                is_converted=False,
                defaults={'expires_at': timezone.now() + timezone.timedelta(days=7)}
            )
            
            # Merge with any existing session cart
            session_id = request.session.session_key
            if session_id and not created:
                self.merge_session_cart(cart, session_id)
            
            return cart
        
        # For guest users (session based)
        else:
            if not request.session.session_key:
                request.session.save()
            
            session_id = request.session.session_key
            cart, created = Cart.objects.get_or_create(
                session_id=session_id,
                is_active=True,
                is_converted=False,
                defaults={'expires_at': timezone.now() + timezone.timedelta(days=7)}
            )
            return cart
    
    def merge_session_cart(self, user_cart, session_id):
        """
        Merge session cart items into user cart after login.
        """
        try:
            session_cart = Cart.objects.get(
                session_id=session_id,
                is_active=True,
                is_converted=False
            )
            
            with transaction.atomic():
                # Move items from session cart to user cart
                for session_item in session_cart.items.all():
                    # Check if item already exists in user cart
                    existing_item = user_cart.items.filter(
                        product=session_item.product,
                        variant=session_item.variant
                    ).first()
                    
                    if existing_item:
                        # Update quantity
                        existing_item.quantity += session_item.quantity
                        existing_item.save()
                    else:
                        # Move item to user cart
                        session_item.cart = user_cart
                        session_item.save()
                
                # Delete session cart
                session_cart.is_active = False
                session_cart.save()
                
        except Cart.DoesNotExist:
            pass
    
    def get(self, request):
        """
        Get current cart.
        """
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def delete(self, request):
        """
        Clear entire cart.
        """
        cart = self.get_cart(request)
        cart.clear_cart()
        return Response({
            'success': True,
            'message': 'Cart cleared successfully'
        })


class CartItemAddView(APIView):
    """
    View for adding items to cart.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Add item to cart.
        """
        # Get cart
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        # Validate and create item
        serializer = CartItemCreateSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data['product']
            variant = serializer.validated_data.get('variant')
            quantity = serializer.validated_data['quantity']
            
            # Check if item already exists in cart
            existing_item = cart.items.filter(
                product=product,
                variant=variant
            ).first()
            
            if existing_item:
                # Update quantity
                new_quantity = existing_item.quantity + quantity
                
                # Check stock
                if product.track_inventory and not product.allow_backorders:
                    available_stock = product.stock_quantity
                    if variant:
                        available_stock = variant.stock_quantity
                    
                    if new_quantity > available_stock:
                        return Response({
                            'success': False,
                            'message': f'Only {available_stock} items available in stock'
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                existing_item.quantity = new_quantity
                existing_item.save()
                item = existing_item
            else:
                # Create new cart item
                item = CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    quantity=quantity,
                    notes=serializer.validated_data.get('notes', '')
                )
            
            # TODO: Track cart abandonment
            # track_cart_activity(cart)
            
            return Response({
                'success': True,
                'message': 'Item added to cart',
                'data': CartItemSerializer(item, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CartItemDetailView(APIView):
    """
    View for updating or removing specific cart items.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get_cart_item(self, request, item_id):
        """
        Get cart item ensuring it belongs to current cart.
        """
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        try:
            return cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return None
    
    def put(self, request, item_id):
        """
        Update cart item quantity.
        """
        item = self.get_cart_item(request, item_id)
        if not item:
            return Response({
                'success': False,
                'message': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemUpdateSerializer(data=request.data)
        if serializer.is_valid():
            quantity = serializer.validated_data['quantity']
            
            if quantity == 0:
                # Remove item if quantity is 0
                item.delete()
                return Response({
                    'success': True,
                    'message': 'Item removed from cart'
                })
            
            # Check stock
            product = item.product
            if product.track_inventory and not product.allow_backorders:
                available_stock = product.stock_quantity
                if item.variant:
                    available_stock = item.variant.stock_quantity
                
                if quantity > available_stock:
                    return Response({
                        'success': False,
                        'message': f'Only {available_stock} items available in stock'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            item.quantity = quantity
            item.save()
            
            return Response({
                'success': True,
                'message': 'Cart updated',
                'data': CartItemSerializer(item, context={'request': request}).data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, item_id):
        """
        Remove item from cart.
        """
        item = self.get_cart_item(request, item_id)
        if not item:
            return Response({
                'success': False,
                'message': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        item.delete()
        
        return Response({
            'success': True,
            'message': 'Item removed from cart'
        })


class CartItemMoveToSavedView(APIView):
    """
    View for moving cart items to saved for later.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, item_id):
        """
        Move cart item to saved for later.
        """
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Cart item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create saved for later item
        saved_item, created = SavedForLater.objects.get_or_create(
            user=request.user,
            product=item.product,
            variant=item.variant,
            defaults={'notes': item.notes}
        )
        
        # Remove from cart
        item.delete()
        
        return Response({
            'success': True,
            'message': 'Item moved to saved for later',
            'data': SavedForLaterSerializer(saved_item).data
        })


class SavedForLaterView(generics.ListCreateAPIView):
    """
    View for listing and adding saved for later items.
    """
    
    serializer_class = SavedForLaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's saved items."""
        return SavedForLater.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create saved item."""
        serializer.save(user=self.request.user)


class SavedForLaterDetailView(generics.DestroyAPIView):
    """
    View for removing saved for later items.
    """
    
    serializer_class = SavedForLaterSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's saved items."""
        return SavedForLater.objects.filter(user=self.request.user)


class SavedForLaterMoveToCartView(APIView):
    """
    View for moving saved items back to cart.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, item_id):
        """
        Move saved item to cart.
        """
        try:
            saved_item = SavedForLater.objects.get(id=item_id, user=request.user)
        except SavedForLater.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Saved item not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get cart
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        # Check if already in cart
        existing_item = cart.items.filter(
            product=saved_item.product,
            variant=saved_item.variant
        ).first()
        
        if existing_item:
            existing_item.quantity += 1
            existing_item.save()
        else:
            CartItem.objects.create(
                cart=cart,
                product=saved_item.product,
                variant=saved_item.variant,
                quantity=1,
                notes=saved_item.notes
            )
        
        # Remove from saved
        saved_item.delete()
        
        return Response({
            'success': True,
            'message': 'Item moved to cart'
        })


class CouponApplyView(APIView):
    """
    View for applying coupon to cart.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Apply coupon to current cart.
        """
        # Get cart
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        # Validate coupon
        serializer = CouponApplySerializer(data=request.data)
        if serializer.is_valid():
            coupon = Coupon.objects.get(code=serializer.validated_data['code'])
            
            # Check if coupon can be applied
            can_apply, message = coupon.can_apply_to_cart(
                cart, 
                user=request.user if request.user.is_authenticated else None
            )
            
            if not can_apply:
                return Response({
                    'success': False,
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if coupon already applied
            if CartCoupon.objects.filter(cart=cart, coupon=coupon).exists():
                return Response({
                    'success': False,
                    'message': 'Coupon already applied to this cart'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Calculate discount
            discount_amount = coupon.calculate_discount(cart)
            
            # Apply coupon
            CartCoupon.objects.create(
                cart=cart,
                coupon=coupon,
                discount_amount=discount_amount
            )
            
            # Increment usage count
            coupon.used_count += 1
            coupon.save()
            
            return Response({
                'success': True,
                'message': f'Coupon {coupon.code} applied successfully',
                'data': {
                    'code': coupon.code,
                    'discount_type': coupon.discount_type,
                    'discount_amount': float(discount_amount)
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CouponRemoveView(APIView):
    """
    View for removing coupon from cart.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def delete(self, request):
        """
        Remove coupon from cart.
        """
        code = request.query_params.get('code')
        if not code:
            return Response({
                'success': False,
                'message': 'Coupon code required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get cart
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        try:
            coupon = Coupon.objects.get(code=code.upper())
            cart_coupon = CartCoupon.objects.get(cart=cart, coupon=coupon)
            cart_coupon.delete()
            
            # Decrement usage count
            coupon.used_count = max(0, coupon.used_count - 1)
            coupon.save()
            
            return Response({
                'success': True,
                'message': 'Coupon removed successfully'
            })
            
        except (Coupon.DoesNotExist, CartCoupon.DoesNotExist):
            return Response({
                'success': False,
                'message': 'Coupon not applied to this cart'
            }, status=status.HTTP_404_NOT_FOUND)


class CartSummaryView(APIView):
    """
    View for getting cart summary without full cart details.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        """
        Get cart summary (total items, subtotal, etc.)
        """
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        return Response({
            'success': True,
            'data': cart.get_cart_summary()
        })


class CartMergeView(APIView):
    """
    View for merging guest cart with user cart after login.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Merge session cart with user cart.
        """
        serializer = CartMergeSerializer(data=request.data)
        if serializer.is_valid():
            session_id = serializer.validated_data['session_id']
            
            cart_view = CartView()
            user_cart = cart_view.get_cart(request)
            cart_view.merge_session_cart(user_cart, session_id)
            
            return Response({
                'success': True,
                'message': 'Carts merged successfully'
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class CouponListView(generics.ListAPIView):
    """
    View for listing available coupons (public).
    """
    
    serializer_class = CouponSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        """Get active and valid coupons."""
        from django.utils import timezone
        now = timezone.now()
        
        return Coupon.objects.filter(
            is_active=True,
            start_date__lte=now,
            end_date__gte=now
        ).order_by('-created_at')[:10]  # Limit to 10 most recent


# Admin Views for Coupon Management
class CouponAdminViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin to manage coupons.
    """
    
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'code'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    #some_filter = products_filters.ProductFilter
    search_fields = ['code', 'description']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'used_count']


class CartAdminView(generics.ListAPIView):
    """
    Admin view for monitoring carts.
    """
    
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """Get carts with filters."""
        queryset = Cart.objects.filter(is_active=True)
        
        # Filter by date
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        # Filter by user type
        user_type = self.request.query_params.get('user_type')
        if user_type == 'registered':
            queryset = queryset.filter(user__isnull=False)
        elif user_type == 'guest':
            queryset = queryset.filter(user__isnull=True)
        
        return queryset.select_related('user').prefetch_related('items')