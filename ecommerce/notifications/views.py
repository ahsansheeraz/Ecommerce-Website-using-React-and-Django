"""
Views for Notifications module.
Handles notification delivery, preferences, announcements, and logs.
"""

from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Q, Count
from django.db import models
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend

from users.models import User
from .models import (
    Notification, NotificationType, NotificationPreference,
    NotificationTemplate, Announcement, UserDevice,
    EmailLog, SMSLog, PushNotificationLog, NotificationStats
)
from .serializers import (
    NotificationSerializer, NotificationListSerializer,
    NotificationPreferenceSerializer, NotificationTypeSerializer,
    NotificationTemplateSerializer, AnnouncementSerializer,
    UserDeviceSerializer, EmailLogSerializer, SMSLogSerializer,
    PushNotificationLogSerializer, MarkNotificationReadSerializer,
    BulkNotificationSerializer, NotificationStatsSerializer,
    TestNotificationSerializer
)
from .utils import (
    send_email_notification, send_sms_notification,
    send_push_notification, create_notification
)
from users.permissions import IsAdminOrModerator


class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for user notifications.
    """
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['priority', 'status', 'notification_type']
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        """Get user's notifications."""
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('notification_type')
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'list':
            return NotificationListSerializer
        return NotificationSerializer
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        """
        Mark notifications as read.
        """
        serializer = MarkNotificationReadSerializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data.get('mark_all'):
                # Mark all as read
                self.get_queryset().filter(status='delivered').update(
                    status='read',
                    read_at=timezone.now()
                )
                message = "All notifications marked as read"
            else:
                # Mark specific notifications
                notification_ids = serializer.validated_data.get('notification_ids', [])
                if notification_ids:
                    self.get_queryset().filter(
                        id__in=notification_ids,
                        status='delivered'
                    ).update(status='read', read_at=timezone.now())
                    message = f"{len(notification_ids)} notifications marked as read"
                else:
                    return Response({
                        'success': False,
                        'message': 'No notifications specified'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': message
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get count of unread notifications.
        """
        count = self.get_queryset().filter(
            status__in=['delivered', 'sent']
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'unread_count': count
            }
        })


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    View for managing notification preferences.
    """
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create preferences for current user."""
        pref, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return pref


class NotificationTypeListView(generics.ListAPIView):
    """
    View for listing available notification types.
    """
    
    queryset = NotificationType.objects.filter(is_active=True)
    serializer_class = NotificationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code', 'category']


class AnnouncementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for announcements (admin: full CRUD, users: read only).
    """
    
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'audience', 'is_active']
    search_fields = ['title', 'message']
    ordering_fields = ['-created_at', '-show_from']
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [IsAdminOrModerator]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Get announcements based on user."""
        queryset = super().get_queryset()
        
        if self.action in ['list', 'retrieve'] and not self.request.user.is_staff:
            # For regular users, only show active announcements they should see
            now = timezone.now()
            queryset = queryset.filter(
                is_active=True,
                show_from__lte=now
            ).filter(
                Q(show_until__isnull=True) | Q(show_until__gte=now)
            )
            
            # Filter by audience
            user = self.request.user
            queryset = queryset.filter(
                Q(audience='all') |
                Q(audience='customers', user__user_type='customer') |
                Q(audience='sellers', user__user_type='seller') |
                Q(audience='admins', user__user_type='admin') |
                Q(audience='specific_users', specific_users=user)
            ).distinct()
        
        return queryset
    
    def perform_create(self, serializer):
        """Set created_by when creating announcement."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def track_view(self, request, pk=None):
        """
        Track announcement view.
        """
        announcement = self.get_object()
        announcement.views_count += 1
        announcement.save()
        
        return Response({'status': 'view tracked'})
    
    @action(detail=True, methods=['post'])
    def track_click(self, request, pk=None):
        """
        Track announcement click.
        """
        announcement = self.get_object()
        announcement.clicks_count += 1
        announcement.save()
        
        return Response({'status': 'click tracked'})


class UserDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user devices for push notifications.
    """
    
    serializer_class = UserDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get user's devices."""
        return UserDevice.objects.filter(user=self.request.user, is_active=True)
    
    def perform_create(self, serializer):
        """Register device for user."""
        # Deactivate existing device with same push token
        push_token = serializer.validated_data.get('push_token')
        UserDevice.objects.filter(
            push_token=push_token
        ).update(is_active=False)
        
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def unregister(self, request):
        """
        Unregister device (logout).
        """
        push_token = request.data.get('push_token')
        if push_token:
            UserDevice.objects.filter(
                user=request.user,
                push_token=push_token
            ).update(is_active=False)
            
            return Response({
                'success': True,
                'message': 'Device unregistered'
            })
        
        return Response({
            'success': False,
            'message': 'Push token required'
        }, status=status.HTTP_400_BAD_REQUEST)


class BulkNotificationView(APIView):
    """
    View for sending bulk notifications (admin only).
    """
    
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request):
        """
        Send notification to multiple users.
        """
        serializer = BulkNotificationSerializer(data=request.data)
        if serializer.is_valid():
            notification_type = serializer.validated_data['notification_type']
            title = serializer.validated_data['title']
            message = serializer.validated_data['message']
            action_url = serializer.validated_data.get('action_url', '')
            action_text = serializer.validated_data.get('action_text', '')
            data = serializer.validated_data.get('data', {})
            
            # Get target users
            users = []
            if serializer.validated_data.get('user_ids'):
                users = User.objects.filter(
                    id__in=serializer.validated_data['user_ids']
                )
            elif serializer.validated_data.get('user_type'):
                user_type = serializer.validated_data['user_type']
                if user_type == 'all':
                    users = User.objects.filter(is_active=True)
                elif user_type == 'customers':
                    users = User.objects.filter(user_type='customer', is_active=True)
                elif user_type == 'sellers':
                    users = User.objects.filter(user_type='seller', is_active=True)
                elif user_type == 'admins':
                    users = User.objects.filter(user_type='admin', is_active=True)
            
            # Create notifications
            notifications = []
            for user in users:
                notification = create_notification(
                    user=user,
                    notification_type=notification_type.code,
                    title=title,
                    message=message,
                    action_url=action_url,
                    action_text=action_text,
                    data=data
                )
                notifications.append(str(notification.id))
            
            return Response({
                'success': True,
                'message': f'Notifications sent to {len(users)} users',
                'data': {
                    'notification_ids': notifications,
                    'user_count': len(users)
                }
            })
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TestNotificationView(APIView):
    """
    View for testing notifications (admin only).
    """
    
    permission_classes = [IsAdminOrModerator]
    
    def post(self, request):
        """
        Send test notification.
        """
        serializer = TestNotificationSerializer(data=request.data)
        if serializer.is_valid():
            channel = serializer.validated_data['channel']
            recipient = serializer.validated_data['recipient']
            notification_type_code = serializer.validated_data['notification_type_code']
            
            try:
                notification_type = NotificationType.objects.get(
                    code=notification_type_code,
                    is_active=True
                )
            except NotificationType.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Invalid notification type'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            result = {'success': False, 'message': 'Failed to send'}
            
            if channel == 'email':
                # Send test email
                result = send_email_notification(
                    recipient_email=recipient,
                    subject=f"Test: {notification_type.name}",
                    template="emails/test.html",
                    context={'type': notification_type.name}
                )
            elif channel == 'sms':
                # Send test SMS
                result = send_sms_notification(
                    phone_number=recipient,
                    message=f"Test notification: {notification_type.name}"
                )
            elif channel == 'push':
                # Send test push (recipient should be user_id)
                try:
                    user = User.objects.get(id=recipient)
                    result = send_push_notification(
                        user=user,
                        title=f"Test: {notification_type.name}",
                        body="This is a test notification",
                        data={'test': True}
                    )
                except User.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': 'User not found'
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Create in-app notification
                notification = create_notification(
                    user=request.user,
                    notification_type=notification_type.code,
                    title=f"Test: {notification_type.name}",
                    message="This is a test in-app notification",
                    data={'test': True}
                )
                result = {
                    'success': True,
                    'message': 'Test notification created',
                    'notification_id': str(notification.id)
                }
            
            return Response(result)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing notification logs (admin only).
    """
    
    permission_classes = [IsAdminOrModerator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        """Get logs based on type."""
        log_type = self.kwargs.get('log_type')
        
        if log_type == 'email':
            return EmailLog.objects.all()
        elif log_type == 'sms':
            return SMSLog.objects.all()
        elif log_type == 'push':
            return PushNotificationLog.objects.all()
        return []
    
    def get_serializer_class(self):
        """Return serializer based on log type."""
        log_type = self.kwargs.get('log_type')
        
        if log_type == 'email':
            return EmailLogSerializer
        elif log_type == 'sms':
            return SMSLogSerializer
        elif log_type == 'push':
            return PushNotificationLogSerializer
        return super().get_serializer_class()


class NotificationStatsView(APIView):
    """
    View for notification statistics (admin only).
    """
    
    permission_classes = [IsAdminOrModerator]
    
    def get(self, request):
        """
        Get notification statistics.
        """
        # Date range
        end_date = timezone.now().date()
        start_date = end_date - timezone.timedelta(days=30)
        
        from_date = request.query_params.get('from_date', start_date)
        to_date = request.query_params.get('to_date', end_date)
        
        # Get stats
        stats = NotificationStats.objects.filter(
            date__range=[from_date, to_date]
        ).order_by('date')
        
        # Calculate totals
        totals = stats.aggregate(
            total_sent=models.Sum('total_sent'),
            total_delivered=models.Sum('total_delivered'),
            total_read=models.Sum('total_read'),
            total_failed=models.Sum('total_failed')
        )
        
        # Channel breakdown
        channel_stats = {
            'email': stats.aggregate(total=models.Sum('email_sent'))['total'] or 0,
            'sms': stats.aggregate(total=models.Sum('sms_sent'))['total'] or 0,
            'push': stats.aggregate(total=models.Sum('push_sent'))['total'] or 0,
            'in_app': stats.aggregate(total=models.Sum('in_app_sent'))['total'] or 0,
        }
        
        # Recent activity
        recent = Notification.objects.filter(
            created_at__date__range=[from_date, to_date]
        ).values('status').annotate(count=Count('id'))
        
        return Response({
            'success': True,
            'data': {
                'date_range': {
                    'from': from_date,
                    'to': to_date
                },
                'totals': totals,
                'by_channel': channel_stats,
                'recent_status': recent,
                'daily_stats': NotificationStatsSerializer(stats, many=True).data
            }
        })


class NotificationTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification templates (admin only).
    """
    
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAdminOrModerator]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['notification_type', 'language']
    search_fields = ['notification_type__name']