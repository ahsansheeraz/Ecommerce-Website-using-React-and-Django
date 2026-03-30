"""
Views for Payments module.
Handles payment processing, webhooks, refunds, and payment method management.
"""

from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Count
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
import hmac
import hashlib
import json

from .models import (
    PaymentGateway, Transaction, SavedPaymentMethod,
    Payout, PaymentWebhookLog, RefundRequest
)
from .serializers import (
    PaymentGatewaySerializer, TransactionSerializer, TransactionDetailSerializer,
    TransactionCreateSerializer, SavedPaymentMethodSerializer,
    PayoutSerializer, RefundRequestSerializer, RefundRequestCreateSerializer,
    PaymentWebhookLogSerializer
)
from orders.models import Order
from users.permissions import IsAdminOrModerator, IsOwnerOrAdmin


class PaymentGatewayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payment gateways (admin only).
    """
    
    queryset = PaymentGateway.objects.all()
    serializer_class = PaymentGatewaySerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'name'


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing transactions.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'transaction_type', 'payment_method', 'currency']
    search_fields = ['transaction_id', 'gateway_transaction_id', 'customer_email']
    ordering_fields = ['-initiated_at', 'amount', 'status']
    
    def get_queryset(self):
        """Get transactions based on user role."""
        if self.request.user.user_type in ['admin', 'moderator']:
            return Transaction.objects.all()
        return Transaction.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return TransactionDetailSerializer
        return TransactionSerializer


class CreatePaymentIntentView(APIView):
    """
    View for creating payment intents.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Create a payment intent.
        """
        serializer = TransactionCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get active payment gateway
        gateway = PaymentGateway.objects.filter(is_active=True, is_default=True).first()
        if not gateway:
            return Response({
                'success': False,
                'message': 'No active payment gateway available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Create transaction record
        with transaction.atomic():
            txn = Transaction.objects.create(
                user=request.user,
                gateway=gateway,
                order=serializer.validated_data.get('order'),
                amount=serializer.validated_data['amount'],
                currency=serializer.validated_data['currency'],
                payment_method=serializer.validated_data['payment_method'],
                customer_email=serializer.validated_data['customer_email'],
                customer_phone=serializer.validated_data.get('customer_phone', ''),
                customer_name=serializer.validated_data.get('customer_name', ''),
                billing_address=serializer.validated_data.get('billing_address', {}),
                metadata=serializer.validated_data.get('metadata', {}),
                status='initiated'
            )
            
            # TODO: Integrate with actual payment gateway
            # For now, simulate payment processing
            
            # If saving payment method
            if serializer.validated_data.get('save_payment_method'):
                # Save payment method for future use
                SavedPaymentMethod.objects.create(
                    user=request.user,
                    gateway=gateway,
                    payment_type='card',  # This would come from gateway response
                    method_id=f"pm_{txn.transaction_id}",
                    display_name="•••• 4242",  # Masked card number
                    card_last4="4242",
                    card_brand="Visa",
                    is_default=not SavedPaymentMethod.objects.filter(user=request.user).exists()
                )
        
        # Return payment intent details
        return Response({
            'success': True,
            'data': {
                'transaction_id': txn.transaction_id,
                'client_secret': f"pi_{txn.transaction_id}_secret",  # Would come from gateway
                'amount': float(txn.amount),
                'currency': txn.currency,
                'gateway': gateway.name
            }
        })


class ConfirmPaymentView(APIView):
    """
    View for confirming payments.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Confirm a payment.
        """
        transaction_id = request.data.get('transaction_id')
        payment_intent_id = request.data.get('payment_intent_id')
        
        if not transaction_id:
            return Response({
                'success': False,
                'message': 'Transaction ID required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            txn = Transaction.objects.get(
                transaction_id=transaction_id,
                user=request.user
            )
        except Transaction.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Transaction not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # TODO: Verify with payment gateway
        # For now, simulate successful payment
        txn.mark_success({
            'payment_intent_id': payment_intent_id,
            'status': 'succeeded',
            'payment_method': 'card'
        })
        
        # Update order status if exists
        if txn.order:
            txn.order.update_status('processing', user=request.user)
        
        return Response({
            'success': True,
            'message': 'Payment confirmed successfully',
            'data': TransactionSerializer(txn).data
        })


class PaymentWebhookView(APIView):
    """
    Webhook endpoint for payment gateways.
    """
    
    permission_classes = [permissions.AllowAny]  # Webhooks are called by gateways
    
    def post(self, request, gateway_name):
        """
        Handle webhook from payment gateway.
        """
        try:
            gateway = PaymentGateway.objects.get(name=gateway_name, is_active=True)
        except PaymentGateway.DoesNotExist:
            return Response({
                'error': 'Gateway not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Log webhook
        webhook_log = PaymentWebhookLog.objects.create(
            gateway=gateway,
            headers=dict(request.headers),
            body=request.data,
            event_type=request.data.get('type', 'unknown')
        )
        
        # Verify webhook signature (implementation depends on gateway)
        # signature = request.headers.get('Stripe-Signature')
        # if not verify_signature(request.body, signature, gateway.webhook_secret):
        #     webhook_log.error_message = "Invalid signature"
        #     webhook_log.save()
        #     return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process webhook based on event type
        event_type = request.data.get('type', '')
        event_data = request.data.get('data', {}).get('object', {})
        
        try:
            if event_type.startswith('payment_intent.'):
                self.handle_payment_intent_event(event_type, event_data, webhook_log)
            elif event_type.startswith('charge.'):
                self.handle_charge_event(event_type, event_data, webhook_log)
            elif event_type.startswith('refund.'):
                self.handle_refund_event(event_type, event_data, webhook_log)
            
            webhook_log.is_processed = True
            webhook_log.processed_at = timezone.now()
            webhook_log.save()
            
        except Exception as e:
            webhook_log.error_message = str(e)
            webhook_log.save()
            return Response({
                'error': 'Webhook processing failed'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({'status': 'success'})
    
    def handle_payment_intent_event(self, event_type, event_data, webhook_log):
        """Handle payment intent events."""
        payment_intent_id = event_data.get('id')
        
        # Find transaction
        txn = Transaction.objects.filter(
            gateway_transaction_id=payment_intent_id
        ).first()
        
        if not txn:
            # Try to find by metadata
            metadata = event_data.get('metadata', {})
            if metadata.get('transaction_id'):
                txn = Transaction.objects.filter(
                    transaction_id=metadata['transaction_id']
                ).first()
        
        if txn:
            webhook_log.transaction = txn
            webhook_log.save()
            
            if event_type == 'payment_intent.succeeded':
                txn.mark_success(event_data)
            elif event_type == 'payment_intent.payment_failed':
                txn.mark_failed(
                    error_code=event_data.get('last_payment_error', {}).get('code'),
                    error_message=event_data.get('last_payment_error', {}).get('message')
                )
    
    def handle_charge_event(self, event_type, event_data, webhook_log):
        """Handle charge events."""
        pass
    
    def handle_refund_event(self, event_type, event_data, webhook_log):
        """Handle refund events."""
        pass


class SavedPaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved payment methods.
    """
    
    serializer_class = SavedPaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's saved payment methods."""
        return SavedPaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    def perform_create(self, serializer):
        """Create saved payment method."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default."""
        payment_method = self.get_object()
        payment_method.is_default = True
        payment_method.save()
        return Response({'status': 'default method set'})


class RefundRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for refund requests.
    """
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'reason']
    search_fields = ['order__order_number', 'transaction__transaction_id']
    
    def get_queryset(self):
        """Get refund requests based on user role."""
        if self.request.user.user_type in ['admin', 'moderator']:
            return RefundRequest.objects.all()
        return RefundRequest.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'create':
            return RefundRequestCreateSerializer
        return RefundRequestSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['create']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminOrModerator]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """Create refund request."""
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve refund request (admin only)."""
        refund_request = self.get_object()
        
        notes = request.data.get('notes', '')
        refund_txn = refund_request.approve(request.user, notes)
        
        return Response({
            'success': True,
            'message': 'Refund approved and processed',
            'data': {
                'refund_transaction_id': refund_txn.transaction_id
            }
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject refund request (admin only)."""
        refund_request = self.get_object()
        reason = request.data.get('reason', '')
        
        refund_request.reject(request.user, reason)
        
        return Response({
            'success': True,
            'message': 'Refund request rejected'
        })


class PayoutViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payouts (admin only).
    """
    
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'user']
    search_fields = ['payout_id', 'user__email']
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Process payout."""
        payout = self.get_object()
        
        # TODO: Integrate with payout gateway
        payout.status = 'processing'
        payout.processed_at = timezone.now()
        payout.save()
        
        return Response({'status': 'payout processing'})


class PaymentMethodListView(generics.ListAPIView):
    """
    View for listing available payment methods.
    """
    
    permission_classes = [permissions.AllowAny]
    serializer_class = PaymentGatewaySerializer
    
    def get_queryset(self):
        """Get active payment gateways."""
        return PaymentGateway.objects.filter(is_active=True)


class TransactionStatsView(APIView):
    """
    View for transaction statistics (admin only).
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def get(self, request):
        """
        Get transaction statistics.
        """
        # Date range
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=30)
        
        from_date = request.query_params.get('from_date', start_date.date())
        to_date = request.query_params.get('to_date', end_date.date())
        
        # Base queryset
        transactions = Transaction.objects.filter(
            initiated_at__date__range=[from_date, to_date]
        )
        
        # Stats
        total_transactions = transactions.count()
        successful_transactions = transactions.filter(status='success').count()
        failed_transactions = transactions.filter(status='failed').count()
        
        total_revenue = transactions.filter(status='success').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # By payment method
        by_method = transactions.filter(status='success').values(
            'payment_method'
        ).annotate(
            count=Count('id'),
            total=Sum('amount')
        )
        
        # Daily breakdown
        daily = transactions.filter(status='success').values(
            'initiated_at__date'
        ).annotate(
            count=Count('id'),
            total=Sum('amount')
        ).order_by('initiated_at__date')
        
        return Response({
            'success': True,
            'data': {
                'date_range': {
                    'from': from_date,
                    'to': to_date
                },
                'summary': {
                    'total_transactions': total_transactions,
                    'successful_transactions': successful_transactions,
                    'failed_transactions': failed_transactions,
                    'success_rate': (successful_transactions / total_transactions * 100) if total_transactions > 0 else 0,
                    'total_revenue': float(total_revenue)
                },
                'by_payment_method': by_method,
                'daily_breakdown': daily
            }
        })


# Stripe integration views (commented for future use)
"""
class StripeWebhookView(APIView):
    # Stripe-specific webhook handler.
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError:
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError:
            return HttpResponse(status=400)
        
        # Handle the event
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            # Handle successful payment
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            # Handle failed payment
        
        return HttpResponse(status=200)


class StripePaymentIntentView(APIView):
    # Create Stripe Payment Intent.
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = StripePaymentIntentSerializer(data=request.data)
        if serializer.is_valid():
            try:
                intent = stripe.PaymentIntent.create(
                    amount=int(serializer.validated_data['amount'] * 100),  # in cents
                    currency=serializer.validated_data['currency'],
                    payment_method=serializer.validated_data.get('payment_method'),
                    customer=serializer.validated_data.get('customer_id'),
                    setup_future_usage=serializer.validated_data.get('setup_future_usage'),
                    metadata=serializer.validated_data.get('metadata', {})
                )
                
                return Response({
                    'client_secret': intent.client_secret,
                    'intent_id': intent.id
                })
            except stripe.error.StripeError as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""


# PayPal integration views (commented for future use)
"""
class PayPalOrderView(APIView):
    # Create PayPal order.
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = PayPalOrderSerializer(data=request.data)
        if serializer.is_valid():
            # Initialize PayPal client
            paypal_client = PayPalClient(
                client_id=settings.PAYPAL_CLIENT_ID,
                client_secret=settings.PAYPAL_CLIENT_SECRET,
                sandbox=settings.PAYPAL_MODE == 'sandbox'
            )
            
            try:
                order = paypal_client.create_order({
                    'intent': 'CAPTURE',
                    'purchase_units': [{
                        'amount': {
                            'currency_code': serializer.validated_data['currency'],
                            'value': str(serializer.validated_data['amount'])
                        },
                        'description': serializer.validated_data.get('description', '')
                    }],
                    'application_context': {
                        'return_url': serializer.validated_data['return_url'],
                        'cancel_url': serializer.validated_data['cancel_url']
                    }
                })
                
                return Response({
                    'order_id': order['id'],
                    'approval_url': next(link['href'] for link in order['links'] if link['rel'] == 'approve')
                })
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""