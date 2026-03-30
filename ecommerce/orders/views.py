"""
Views for Orders module.
Handles checkout, order management, returns, and cancellations.
"""

from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count, Avg
from django.utils import timezone
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend

from .models import (
    Order, OrderItem, OrderStatusHistory, OrderPayment,
    OrderCancellation, OrderReturn, OrderInvoice
)
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer,
    OrderStatusUpdateSerializer, OrderCancelSerializer,
    OrderReturnSerializer, OrderInvoiceSerializer, OrderAnalyticsSerializer
)
from cart.models import Cart, CartItem, CartCoupon
from cart.views import CartView
from products.models import Product
from users.permissions import IsAdminOrModerator, IsOwnerOrAdmin
from notifications.utils import create_notification


class CheckoutView(APIView):
    """
    View for processing checkout and creating orders.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request):
        """
        Create order from cart.
        """
        # Get user's active cart
        cart_view = CartView()
        cart = cart_view.get_cart(request)
        
        # Check if cart has items
        if cart.total_items == 0:
            return Response({
                'success': False,
                'message': 'Cart is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate checkout data
        serializer = OrderCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=serializer.validated_data['shipping_address'],
            billing_address=serializer.validated_data['billing_address'],
            payment_method=serializer.validated_data['payment_method'],
            customer_notes=serializer.validated_data.get('customer_notes', ''),
            coupon=serializer.validated_data.get('coupon'),
            discount_amount=serializer.validated_data.get('discount_amount', 0),
            subtotal=cart.subtotal,
            shipping_cost=0,  # Calculate based on shipping method
            tax_amount=0,      # Calculate based on tax rules
            total_amount=cart.total - (serializer.validated_data.get('discount_amount', 0))
        )
        
        # Create order items from cart items
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                variant=cart_item.variant,
                product_name=cart_item.product.name,
                product_sku=cart_item.product.sku,
                unit_price=cart_item.unit_price,
                discount_amount=cart_item.discount_amount or 0,
                quantity=cart_item.quantity,
                variant_details=cart_item.variant.attributes if cart_item.variant else {}
            )
            
            # Update product stock
            product = cart_item.product
            if product.track_inventory:
                product.stock_quantity -= cart_item.quantity
                product.sold_count += cart_item.quantity
                product.save()
        
        # Mark cart as converted
        cart.is_converted = True
        cart.save()
        
        # Create initial status history
        OrderStatusHistory.objects.create(
            order=order,
            status='pending',
            notes='Order placed successfully'
        )
        
        # TODO: Send order confirmation email
        # send_order_confirmation(order)
        
        # Create notification
        create_notification(
            user=request.user,
            notification_type='order_confirmation',
            title='Order Confirmed',
            message=f'Your order #{order.order_number} has been placed successfully.',
            data={'order_id': str(order.id), 'order_number': order.order_number}
        )
        
        # Notify admin
        create_notification(
            user_type='admin',
            notification_type='new_order',
            title='New Order Received',
            message=f'New order #{order.order_number} from {request.user.email}',
            data={'order_id': str(order.id), 'order_number': order.order_number}
        )
        
        return Response({
            'success': True,
            'message': 'Order created successfully',
            'data': {
                'order_id': str(order.id),
                'order_number': order.order_number,
                'total_amount': float(order.total_amount)
            }
        }, status=status.HTTP_201_CREATED)


class OrderListView(generics.ListAPIView):
    """
    View for listing user orders.
    """
    
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    ordering_fields = ['-created_at', 'total_amount']
    
    def get_queryset(self):
        """Get orders for current user."""
        queryset = Order.objects.filter(user=self.request.user)
        
        # Apply date filters
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        return queryset.select_related('user').prefetch_related('items')


class OrderDetailView(generics.RetrieveAPIView):
    """
    View for retrieving order details.
    """
    
    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders based on user role."""
        if self.request.user.user_type in ['admin', 'moderator']:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)


class OrderStatusUpdateView(APIView):
    """
    View for updating order status (admin/seller only).
    """
    
    permission_classes = [permissions.IsAuthenticated, IsAdminOrModerator]
    
    def post(self, request, order_number):
        """
        Update order status.
        """
        order = get_object_or_404(Order, order_number=order_number)
        
        serializer = OrderStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            old_status = order.status
            new_status = serializer.validated_data['status']
            
            # Update order
            order.status = new_status
            
            # Update tracking info if provided
            if serializer.validated_data.get('tracking_number'):
                order.tracking_number = serializer.validated_data['tracking_number']
            if serializer.validated_data.get('shipped_via'):
                order.shipped_via = serializer.validated_data['shipped_via']
            if serializer.validated_data.get('estimated_delivery'):
                order.estimated_delivery = serializer.validated_data['estimated_delivery']
            
            # Set delivered timestamp
            if new_status == 'delivered':
                order.delivered_at = timezone.now()
            
            order.save()
            
            # Create status history
            OrderStatusHistory.objects.create(
                order=order,
                status=new_status,
                changed_by=request.user,
                notes=serializer.validated_data.get('notes', '')
            )
            
            # Notify customer
            create_notification(
                user=order.user,
                notification_type='order_status_update',
                title=f'Order #{order.order_number} Status Updated',
                message=f'Your order status has been updated to {order.get_status_display()}.',
                data={'order_id': str(order.id), 'status': new_status}
            )
            
            return Response({
                'success': True,
                'message': f'Order status updated to {new_status}',
                'data': OrderDetailSerializer(order, context={'request': request}).data
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderCancelView(APIView):
    """
    View for cancelling orders.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, order_number):
        """
        Cancel an order.
        """
        order = get_object_or_404(Order, order_number=order_number)
        
        # Check permissions
        if order.user != request.user and request.user.user_type not in ['admin', 'moderator']:
            return Response({
                'success': False,
                'message': 'Permission denied'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Check if order can be cancelled
        if not order.is_cancellable:
            return Response({
                'success': False,
                'message': f'Order cannot be cancelled in {order.status} status'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderCancelSerializer(data=request.data)
        if serializer.is_valid():
            # Create cancellation record
            cancellation = OrderCancellation.objects.create(
                order=order,
                reason=serializer.validated_data['reason'],
                reason_details=serializer.validated_data.get('reason_details', ''),
                cancelled_by=request.user,
                refund_amount=order.total_amount if order.is_paid else 0,
                requires_approval=order.is_paid  # Require approval if paid
            )
            
            # Update order status
            order.update_status(
                'cancelled' if not order.is_paid else 'on_hold',
                user=request.user,
                notes=f"Cancelled: {cancellation.reason}"
            )
            
            # Restore stock if not paid
            if not order.is_paid:
                for item in order.items.all():
                    product = item.product
                    if product.track_inventory:
                        product.stock_quantity += item.quantity
                        product.sold_count -= item.quantity
                        product.save()
            
            # Notify user
            create_notification(
                user=order.user,
                notification_type='order_cancelled',
                title=f'Order #{order.order_number} Cancelled',
                message=f'Your order has been cancelled. Reason: {cancellation.get_reason_display()}',
                data={'order_id': str(order.id)}
            )
            
            return Response({
                'success': True,
                'message': 'Cancellation request submitted',
                'data': {
                    'cancellation_id': str(cancellation.id),
                    'requires_approval': cancellation.requires_approval
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderReturnView(APIView):
    """
    View for initiating returns.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @transaction.atomic
    def post(self, request, order_number):
        """
        Initiate return for order items.
        """
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Check if order can be returned
        if not order.is_returnable:
            return Response({
                'success': False,
                'message': 'Order is not eligible for return'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = OrderReturnSerializer(
            data=request.data,
            context={'order': order}
        )
        
        if serializer.is_valid():
            order_item = serializer.validated_data['order_item']
            
            # Create return record
            order_return = OrderReturn.objects.create(
                order=order,
                order_item=order_item,
                reason=serializer.validated_data['reason'],
                reason_details=serializer.validated_data.get('reason_details', ''),
                images=serializer.validated_data.get('images', []),
                is_exchange=serializer.validated_data.get('is_exchange', False),
                exchange_product=serializer.validated_data.get('exchange_product'),
                pickup_address=order.shipping_address
            )
            
            # Update order item
            order_item.is_returned = True
            order_item.return_reason = order_return.reason
            order_item.save()
            
            # Notify admin
            create_notification(
                user_type='admin',
                notification_type='return_request',
                title='New Return Request',
                message=f'Return request for Order #{order.order_number}',
                data={'return_id': str(order_return.id)}
            )
            
            return Response({
                'success': True,
                'message': 'Return request submitted successfully',
                'data': {
                    'return_id': str(order_return.id),
                    'status': order_return.status
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class OrderPaymentView(APIView):
    """
    View for processing order payments.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, order_number):
        """
        Process payment for order.
        """
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        
        # Check if already paid
        if order.is_paid:
            return Response({
                'success': False,
                'message': 'Order is already paid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get payment details from request
        payment_method = request.data.get('payment_method')
        transaction_id = request.data.get('transaction_id')
        amount = request.data.get('amount')
        
        if not all([payment_method, transaction_id, amount]):
            return Response({
                'success': False,
                'message': 'Payment method, transaction ID, and amount are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create payment record
        payment = OrderPayment.objects.create(
            order=order,
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            gateway_response=request.data.get('gateway_response', {})
        )
        
        # Mark payment as success (simplified - actual implementation would verify with gateway)
        payment.mark_success()
        
        # Update order status
        if order.status == 'pending':
            order.update_status('processing', user=request.user)
        
        return Response({
            'success': True,
            'message': 'Payment processed successfully',
            'data': {
                'payment_id': str(payment.id),
                'transaction_id': payment.transaction_id,
                'amount': float(payment.amount),
                'status': payment.status
            }
        })


class OrderInvoiceView(generics.RetrieveAPIView):
    """
    View for retrieving order invoice.
    """
    
    serializer_class = OrderInvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    lookup_field = 'order_number'
    
    def get_queryset(self):
        """Get orders for invoice generation."""
        if self.request.user.user_type in ['admin', 'moderator']:
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or generate invoice for order."""
        order = super().get_object()
        
        # Get or create invoice
        invoice, created = OrderInvoice.objects.get_or_create(order=order)
        
        # Generate invoice if not exists
        if created or not invoice.invoice_file:
            self.generate_invoice(invoice, order)
        
        return invoice
    
    def generate_invoice(self, invoice, order):
        """
        Generate invoice PDF.
        This would integrate with a PDF generation service.
        """
        # TODO: Implement PDF generation
        # For now, just set invoice URL
        invoice.invoice_url = f"/api/orders/{order.order_number}/invoice/download/"
        invoice.save()


class OrderTrackingView(APIView):
    """
    View for tracking order status.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, order_number):
        """
        Get order tracking information.
        """
        order = get_object_or_404(Order, order_number=order_number)
        
        # Get status history
        status_history = OrderStatusHistory.objects.filter(order=order).values(
            'status', 'notes', 'created_at'
        )
        
        # Get tracking info
        tracking_info = {
            'tracking_number': order.tracking_number,
            'shipped_via': order.shipped_via,
            'estimated_delivery': order.estimated_delivery,
            'delivered_at': order.delivered_at
        }
        
        return Response({
            'success': True,
            'data': {
                'order_number': order.order_number,
                'current_status': order.status,
                'current_status_display': order.get_status_display(),
                'status_history': status_history,
                'tracking_info': tracking_info
            }
        })


# Admin Views
class AdminOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for admin order management.
    """
    
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'payment_method']
    search_fields = ['order_number', 'user__email', 'user__first_name', 'user__last_name']
    ordering_fields = ['-created_at', 'total_amount', 'status']
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer
    
    def get_queryset(self):
        """Get queryset with filters."""
        queryset = super().get_queryset()
        
        # Date range filters
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(created_at__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__lte=to_date)
        
        # Customer filter
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(user_id=customer_id)
        
        return queryset.select_related('user', 'shipping_address').prefetch_related('items')


class AdminReturnViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing returns (admin only).
    """
    
    queryset = OrderReturn.objects.all()
    permission_classes = [permissions.IsAdminUser]
    serializer_class = OrderReturnSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'reason', 'is_exchange']
    search_fields = ['order__order_number', 'order_item__product_name']
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve return request."""
        order_return = self.get_object()
        
        order_return.status = 'approved'
        order_return.handled_by = request.user
        order_return.save()
        
        # Schedule pickup (integration with shipping service)
        
        # Notify customer
        create_notification(
            user=order_return.order.user,
            notification_type='return_approved',
            title='Return Request Approved',
            message=f'Your return request for Order #{order_return.order.order_number} has been approved.'
        )
        
        return Response({'status': 'return approved'})
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject return request."""
        order_return = self.get_object()
        
        order_return.status = 'rejected'
        order_return.handled_by = request.user
        order_return.admin_notes = request.data.get('notes', '')
        order_return.save()
        
        # Notify customer
        create_notification(
            user=order_return.order.user,
            notification_type='return_rejected',
            title='Return Request Rejected',
            message=f'Your return request for Order #{order_return.order.order_number} has been rejected.'
        )
        
        return Response({'status': 'return rejected'})


class OrderAnalyticsView(APIView):
    """
    View for order analytics (admin only).
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Get order analytics data.
        """
        # Date range
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=30)
        
        from_date = request.query_params.get('from_date', start_date.date())
        to_date = request.query_params.get('to_date', end_date.date())
        
        # Base queryset
        orders = Order.objects.filter(created_at__date__range=[from_date, to_date])
        
        # Total stats
        total_orders = orders.count()
        total_revenue = orders.filter(payment_status='paid').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        # Orders by status
        orders_by_status = orders.values('status').annotate(
            count=Count('id'),
            total=Sum('total_amount')
        )
        
        # Revenue by date
        revenue_by_date = orders.filter(payment_status='paid').values('created_at__date').annotate(
            revenue=Sum('total_amount'),
            orders=Count('id')
        ).order_by('created_at__date')
        
        # Top products
        top_products = OrderItem.objects.filter(
            order__in=orders
        ).values(
            'product__id', 'product__name'
        ).annotate(
            total_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-total_sold')[:10]
        
        # Top customers
        top_customers = orders.values(
            'user__id', 'user__email', 'user__first_name', 'user__last_name'
        ).annotate(
            total_orders=Count('id'),
            total_spent=Sum('total_amount')
        ).order_by('-total_spent')[:10]
        
        return Response({
            'success': True,
            'data': {
                'date_range': {
                    'from': from_date,
                    'to': to_date
                },
                'summary': {
                    'total_orders': total_orders,
                    'total_revenue': float(total_revenue),
                    'average_order_value': float(avg_order_value)
                },
                'orders_by_status': orders_by_status,
                'revenue_by_date': revenue_by_date,
                'top_products': top_products,
                'top_customers': top_customers
            }
        })