"""
Views for Admin Panel module.
Handles admin dashboard, settings, reports, logs, and system management.
"""

from rest_framework import generics, permissions, status, viewsets, filters
from rest_framework.response import Response
from django.db import models
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Q, Count, Sum, Avg
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import json

from .models import (
    DashboardWidget, AdminDashboard, DashboardWidgetPlacement,
    AdminActivityLog, SystemSetting, ReportTemplate, GeneratedReport,
    AdminNote, BackupLog, MaintenanceMode, AdminNotification, SystemHealth
)
from .serializers import (
    DashboardWidgetSerializer, AdminDashboardSerializer, AdminDashboardCreateSerializer,
    AdminActivityLogSerializer, SystemSettingSerializer, ReportTemplateSerializer,
    GeneratedReportSerializer, AdminNoteSerializer, BackupLogSerializer,
    MaintenanceModeSerializer, AdminNotificationSerializer, SystemHealthSerializer,
    DashboardSummarySerializer, QuickActionSerializer, BulkActionSerializer,
    SystemSettingsGroupSerializer
)
from users.models import User
from orders.models import Order
from products.models import Product
from payments.models import Transaction
from users.permissions import IsAdminOrModerator


class AdminPermissionMixin:
    """Mixin for admin-only views."""
    permission_classes = [IsAdminOrModerator]


class DashboardWidgetViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing dashboard widgets.
    """
    
    queryset = DashboardWidget.objects.all()
    serializer_class = DashboardWidgetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['widget_type', 'is_active', 'is_default']
    search_fields = ['name']
    ordering_fields = ['order', 'name', 'created_at']


class AdminDashboardViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for admin dashboards.
    """
    
    serializer_class = AdminDashboardSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def get_queryset(self):
        """Get dashboards for current admin."""
        return AdminDashboard.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action in ['create', 'update', 'partial_update']:
            return AdminDashboardCreateSerializer
        return AdminDashboardSerializer
    
    def perform_create(self, serializer):
        """Create dashboard for current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get default dashboard for current admin."""
        dashboard = AdminDashboard.objects.filter(
            user=request.user,
            is_default=True
        ).first()
        
        if not dashboard:
            # Create default dashboard with system widgets
            dashboard = AdminDashboard.objects.create(
                user=request.user,
                name='Default Dashboard',
                is_default=True,
                layout={'columns': 3}
            )
            
            # Add default widgets
            default_widgets = DashboardWidget.objects.filter(is_default=True)
            for idx, widget in enumerate(default_widgets):
                DashboardWidgetPlacement.objects.create(
                    dashboard=dashboard,
                    widget=widget,
                    row=idx // 3,
                    column=idx % 3
                )
        
        serializer = self.get_serializer(dashboard)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_widget(self, request, pk=None):
        """Add widget to dashboard."""
        dashboard = self.get_object()
        widget_id = request.data.get('widget_id')
        row = request.data.get('row', 0)
        column = request.data.get('column', 0)
        
        try:
            widget = DashboardWidget.objects.get(id=widget_id, is_active=True)
            
            # Check if already exists
            if DashboardWidgetPlacement.objects.filter(
                dashboard=dashboard,
                widget=widget
            ).exists():
                return Response({
                    'success': False,
                    'message': 'Widget already exists in dashboard'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            placement = DashboardWidgetPlacement.objects.create(
                dashboard=dashboard,
                widget=widget,
                row=row,
                column=column
            )
            
            return Response({
                'success': True,
                'data': DashboardWidgetPlacementSerializer(placement).data
            })
            
        except DashboardWidget.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Widget not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_widget(self, request, pk=None):
        """Remove widget from dashboard."""
        dashboard = self.get_object()
        placement_id = request.data.get('placement_id')
        
        try:
            placement = DashboardWidgetPlacement.objects.get(
                id=placement_id,
                dashboard=dashboard
            )
            placement.delete()
            
            return Response({
                'success': True,
                'message': 'Widget removed'
            })
            
        except DashboardWidgetPlacement.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Widget placement not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def reorder_widgets(self, request, pk=None):
        """Reorder widgets in dashboard."""
        dashboard = self.get_object()
        placements = request.data.get('placements', [])
        
        for placement_data in placements:
            try:
                placement = DashboardWidgetPlacement.objects.get(
                    id=placement_data['id'],
                    dashboard=dashboard
                )
                placement.row = placement_data.get('row', placement.row)
                placement.column = placement_data.get('column', placement.column)
                placement.save()
            except (DashboardWidgetPlacement.DoesNotExist, KeyError):
                pass
        
        return Response({'success': True})


class DashboardSummaryView(AdminPermissionMixin, APIView):
    """
    View for dashboard summary data.
    """
    
    def get(self, request):
        """Get dashboard summary statistics."""
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # User stats
        total_users = User.objects.count()
        new_users_today = User.objects.filter(date_joined__date=today).count()
        active_users = User.objects.filter(last_login__date=today).count()
        
        # Order stats
        total_orders = Order.objects.count()
        orders_today = Order.objects.filter(created_at__date=today).count()
        pending_orders = Order.objects.filter(status='pending').count()
        
        # Revenue stats
        total_revenue = Transaction.objects.filter(
            status='success'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        revenue_today = Transaction.objects.filter(
            status='success',
            completed_at__date=today
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Product stats
        total_products = Product.objects.count()
        low_stock_products = Product.objects.filter(
            track_inventory=True,
            stock_quantity__lte=models.F('low_stock_threshold')
        ).count()
        out_of_stock = Product.objects.filter(
            track_inventory=True,
            stock_quantity=0
        ).count()
        
        # System health
        latest_health = SystemHealth.objects.order_by('-checked_at').first()
        system_health = latest_health.status if latest_health else 'unknown'
        
        # Pending tasks
        pending_tasks = (
            Order.objects.filter(status='pending').count() +
            AdminNotification.objects.filter(
                expires_at__gt=timezone.now()
            ).count()
        )
        
        data = {
            'total_users': total_users,
            'new_users_today': new_users_today,
            'active_users': active_users,
            'total_orders': total_orders,
            'orders_today': orders_today,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'revenue_today': revenue_today,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
            'out_of_stock': out_of_stock,
            'system_health': system_health,
            'pending_tasks': pending_tasks,
        }
        
        serializer = DashboardSummarySerializer(data)
        return Response(serializer.data)


class AdminActivityLogViewSet(AdminPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing admin activity logs.
    """
    
    queryset = AdminActivityLog.objects.all()
    serializer_class = AdminActivityLogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['action', 'status', 'content_type']
    search_fields = ['admin__email', 'object_repr', 'details']
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        """Get filtered logs."""
        queryset = super().get_queryset()
        
        # Date range filter
        from_date = self.request.query_params.get('from_date')
        to_date = self.request.query_params.get('to_date')
        
        if from_date:
            queryset = queryset.filter(created_at__date__gte=from_date)
        if to_date:
            queryset = queryset.filter(created_at__date__lte=to_date)
        
        # User filter
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(admin_id=user_id)
        
        return queryset.select_related('admin', 'content_type')


class SystemSettingViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing system settings.
    """
    
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'value_type', 'is_editable']
    search_fields = ['key', 'label', 'description']
    
    def perform_update(self, serializer):
        """Track who updated the setting."""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get settings grouped by category."""
        categories = SystemSetting.objects.values_list('category', flat=True).distinct()
        result = []
        
        for category in categories:
            settings = SystemSetting.objects.filter(category=category)
            result.append({
                'category': category,
                'settings': SystemSettingSerializer(settings, many=True).data
            })
        
        serializer = SystemSettingsGroupSerializer(result, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Update multiple settings at once."""
        updates = request.data.get('settings', [])
        success_count = 0
        
        for update in updates:
            try:
                setting = SystemSetting.objects.get(key=update['key'])
                setting.value = str(update['value'])
                setting.updated_by = request.user
                setting.save()
                success_count += 1
            except (SystemSetting.DoesNotExist, KeyError):
                pass
        
        return Response({
            'success': True,
            'message': f'Updated {success_count} settings'
        })


class ReportTemplateViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing report templates.
    """
    
    queryset = ReportTemplate.objects.all()
    serializer_class = ReportTemplateSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['report_type', 'is_active', 'is_system']
    search_fields = ['name', 'description']
    
    def perform_create(self, serializer):
        """Set created_by."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def generate(self, request, pk=None):
        """Generate report from template."""
        template = self.get_object()
        parameters = request.data.get('parameters', {})
        
        # Create generated report
        report = GeneratedReport.objects.create(
            template=template,
            name=f"{template.name} - {timezone.now().strftime('%Y-%m-%d %H:%M')}",
            parameters=parameters,
            file_format=request.data.get('format', 'csv'),
            status='pending',
            generated_by=request.user
        )
        
        # TODO: Trigger async report generation
        # generate_report.delay(report.id)
        
        return Response({
            'success': True,
            'message': 'Report generation started',
            'report_id': report.id
        })


class GeneratedReportViewSet(AdminPermissionMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing generated reports.
    """
    
    queryset = GeneratedReport.objects.all()
    serializer_class = GeneratedReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'file_format']
    search_fields = ['name']
    ordering_fields = ['-created_at']
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Get download URL for report."""
        report = self.get_object()
        
        if report.file:
            # Generate signed URL for file download
            # TODO: Implement signed URL generation
            return Response({
                'success': True,
                'download_url': report.file.url
            })
        
        return Response({
            'success': False,
            'message': 'Report file not available'
        }, status=status.HTTP_404_NOT_FOUND)


class AdminNoteViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for admin notes.
    """
    
    serializer_class = AdminNoteSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['color', 'is_private', 'is_pinned']
    search_fields = ['title', 'content']
    
    def get_queryset(self):
        """Get notes visible to current admin."""
        user = self.request.user
        
        # Get own notes and notes shared with user
        return AdminNote.objects.filter(
            Q(admin=user) |
            Q(shared_with=user) |
            Q(is_private=False)
        ).distinct()
    
    def perform_create(self, serializer):
        """Create note for current user."""
        serializer.save(admin=self.request.user)
    
    @action(detail=True, methods=['post'])
    def toggle_pin(self, request, pk=None):
        """Toggle pin status."""
        note = self.get_object()
        note.is_pinned = not note.is_pinned
        note.save()
        
        return Response({
            'success': True,
            'is_pinned': note.is_pinned
        })
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """Share note with other admins."""
        note = self.get_object()
        admin_ids = request.data.get('admin_ids', [])
        
        if note.admin != request.user:
            return Response({
                'success': False,
                'message': 'You can only share your own notes'
            }, status=status.HTTP_403_FORBIDDEN)
        
        admins = User.objects.filter(
            id__in=admin_ids,
            user_type__in=['admin', 'moderator']
        )
        note.shared_with.add(*admins)
        
        return Response({
            'success': True,
            'message': f'Note shared with {admins.count()} admins'
        })


class BackupViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing backups.
    """
    
    queryset = BackupLog.objects.all()
    serializer_class = BackupLogSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['-created_at']
    
    @action(detail=False, methods=['post'])
    def create_backup(self, request):
        """Create new database backup."""
        backup_type = request.data.get('backup_type', 'manual')
        notes = request.data.get('notes', '')
        
        backup = BackupLog.objects.create(
            name=f"Backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}",
            backup_type=backup_type,
            status='pending',
            created_by=request.user,
            notes=notes
        )
        
        # TODO: Trigger async backup process
        # create_backup.delay(backup.id)
        
        return Response({
            'success': True,
            'message': 'Backup started',
            'backup_id': backup.id
        })
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore from backup."""
        backup = self.get_object()
        
        if backup.status != 'completed':
            return Response({
                'success': False,
                'message': 'Backup is not ready for restore'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: Implement restore functionality
        # restore_from_backup.delay(backup.id)
        
        return Response({
            'success': True,
            'message': 'Restore started'
        })
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """Download backup file."""
        backup = self.get_object()
        
        if backup.file:
            # Generate signed URL for download
            return Response({
                'success': True,
                'download_url': backup.file.url
            })
        
        return Response({
            'success': False,
            'message': 'Backup file not available'
        }, status=status.HTTP_404_NOT_FOUND)


class MaintenanceModeView(AdminPermissionMixin, APIView):
    """
    View for managing maintenance mode.
    """
    
    def get(self, request):
        """Get current maintenance mode status."""
        maintenance = MaintenanceMode.objects.first()
        if not maintenance:
            maintenance = MaintenanceMode.objects.create()
        
        serializer = MaintenanceModeSerializer(maintenance)
        return Response(serializer.data)
    
    def post(self, request):
        """Update maintenance mode."""
        maintenance, _ = MaintenanceMode.objects.get_or_create()
        
        serializer = MaintenanceModeSerializer(
            maintenance,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save(enabled_by=request.user)
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action='settings_change',
                content_type=ContentType.objects.get_for_model(MaintenanceMode),
                object_id=maintenance.id,
                object_repr='Maintenance Mode',
                details={'is_active': maintenance.is_active}
            )
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Disable maintenance mode."""
        maintenance = MaintenanceMode.objects.first()
        if maintenance:
            maintenance.is_active = False
            maintenance.enabled_by = request.user
            maintenance.save()
        
        return Response({'success': True, 'message': 'Maintenance mode disabled'})


class AdminNotificationViewSet(AdminPermissionMixin, viewsets.ModelViewSet):
    """
    ViewSet for admin notifications.
    """
    
    serializer_class = AdminNotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'for_all_admins']
    search_fields = ['title', 'message']
    ordering_fields = ['-created_at']
    
    def get_queryset(self):
        """Get notifications for current admin."""
        user = self.request.user
        
        return AdminNotification.objects.filter(
            Q(for_all_admins=True) |
            Q(specific_admins=user)
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        ).distinct()
    
    def perform_create(self, serializer):
        """Create notification."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def dismiss(self, request, pk=None):
        """Dismiss notification."""
        notification = self.get_object()
        notification.dismissed_by.add(request.user)
        
        return Response({'success': True, 'message': 'Notification dismissed'})


class SystemHealthView(AdminPermissionMixin, APIView):
    """
    View for system health checks.
    """
    
    def get(self, request):
        """Get latest system health status."""
        component = request.query_params.get('component')
        
        if component:
            health = SystemHealth.objects.filter(
                component=component
            ).order_by('-checked_at').first()
        else:
            # Get latest for all components
            latest_health = []
            for component_code, _ in SystemHealth.COMPONENT_CHOICES:
                health = SystemHealth.objects.filter(
                    component=component_code
                ).order_by('-checked_at').first()
                if health:
                    latest_health.append(health)
            
            serializer = SystemHealthSerializer(latest_health, many=True)
            return Response(serializer.data)
        
        if health:
            serializer = SystemHealthSerializer(health)
            return Response(serializer.data)
        
        return Response({
            'success': False,
            'message': 'No health data available'
        }, status=status.HTTP_404_NOT_FOUND)
    
    def post(self, request):
        """Run manual health check."""
        # TODO: Implement health check logic
        # This would check database, cache, external services, etc.
        
        return Response({
            'success': True,
            'message': 'Health check initiated'
        })


class QuickActionView(AdminPermissionMixin, APIView):
    """
    View for quick admin actions.
    """
    
    def post(self, request):
        """Execute quick action."""
        serializer = QuickActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            data = serializer.validated_data.get('data', {})
            
            result = {'success': True, 'message': 'Action executed'}
            
            if action == 'create_product':
                # Redirect to product creation
                result['redirect'] = '/admin/products/new'
            
            elif action == 'create_coupon':
                # Redirect to coupon creation
                result['redirect'] = '/admin/coupons/new'
            
            elif action == 'send_newsletter':
                # Redirect to newsletter
                result['redirect'] = '/admin/newsletter/new'
            
            elif action == 'run_report':
                # Run default report
                result['report_id'] = 'default'
            
            elif action == 'backup_db':
                # Create backup
                backup = BackupLog.objects.create(
                    name=f"Quick Backup {timezone.now().strftime('%Y%m%d_%H%M%S')}",
                    backup_type='manual',
                    status='pending',
                    created_by=request.user
                )
                result['backup_id'] = str(backup.id)
            
            elif action == 'clear_cache':
                # Clear cache
                from django.core.cache import cache
                cache.clear()
                result['message'] = 'Cache cleared'
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action='create',
                content_type=ContentType.objects.get_for_model(type('QuickAction', (), {})),
                object_id=action,
                object_repr=f"Quick Action: {action}",
                details=data
            )
            
            return Response(result)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BulkActionView(AdminPermissionMixin, APIView):
    """
    View for bulk actions on objects.
    """
    
    def post(self, request):
        """Execute bulk action."""
        serializer = BulkActionSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            ids = serializer.validated_data['ids']
            data = serializer.validated_data.get('data', {})
            
            model_map = {
                'users': User,
                'orders': Order,
                'products': Product,
            }
            
            model_name = data.get('model')
            if not model_name or model_name not in model_map:
                return Response({
                    'success': False,
                    'message': 'Invalid model'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            model = model_map[model_name]
            objects = model.objects.filter(id__in=ids)
            count = objects.count()
            
            if action == 'delete':
                objects.delete()
                message = f'Deleted {count} {model_name}'
            
            elif action == 'update_status':
                status_value = data.get('status')
                objects.update(status=status_value)
                message = f'Updated status of {count} {model_name}'
            
            elif action == 'export':
                # Trigger export
                message = f'Exporting {count} {model_name}'
            
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid action'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Log activity
            AdminActivityLog.objects.create(
                admin=request.user,
                action=action,
                content_type=ContentType.objects.get_for_model(model),
                object_id=','.join(str(id) for id in ids[:10]),  # First 10 IDs
                object_repr=f"Bulk {action} on {count} {model_name}",
                details={'count': count, 'action': action, 'data': data}
            )
            
            return Response({
                'success': True,
                'message': message,
                'count': count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchAllView(AdminPermissionMixin, APIView):
    """
    Global search across all models.
    """
    
    def get(self, request):
        """Search across users, orders, products."""
        query = request.query_params.get('q', '')
        
        if len(query) < 2:
            return Response([])
        
        results = []
        
        # Search users
        users = User.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query)
        )[:5]
        
        for user in users:
            results.append({
                'id': str(user.id),
                'type': 'user',
                'title': user.email,
                'subtitle': user.get_full_name(),
                'url': f'/admin/users/{user.id}'
            })
        
        # Search orders
        orders = Order.objects.filter(
            Q(order_number__icontains=query) |
            Q(user__email__icontains=query)
        )[:5]
        
        for order in orders:
            results.append({
                'id': str(order.id),
                'type': 'order',
                'title': f"Order #{order.order_number}",
                'subtitle': f"${order.total_amount} - {order.user.email}",
                'url': f'/admin/orders/{order.order_number}'
            })
        
        # Search products
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        )[:5]
        
        for product in products:
            results.append({
                'id': str(product.id),
                'type': 'product',
                'title': product.name,
                'subtitle': f"SKU: {product.sku}",
                'url': f'/admin/products/{product.id}'
            })
        
        return Response(results)