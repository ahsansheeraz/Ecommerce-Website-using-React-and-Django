"""
Views for User module.
"""

from rest_framework import generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, Address, Wishlist, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, AddressSerializer,
    WishlistSerializer, ChangePasswordSerializer,
    UserListSerializer, AdminUserUpdateSerializer
)
from .permissions import (
    IsAdminUser, IsAdminOrModerator, IsOwnerOrAdmin, IsAdminOrSeller
)

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    POST /api/auth/register/
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    POST /api/auth/login/
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = data['user']
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        return Response({
            'success': True,
            'message': 'Logged in successfully',
            'data': {
                'access_token': data['access'],
                'refresh_token': data['refresh'],
                'user': {
                    'id': str(user.id),
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'user_type': user.user_type,
                    'is_active': user.is_active
                }
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    POST /api/auth/logout/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({
                'success': True,
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile.
    GET /api/auth/profile/
    PUT /api/auth/profile/
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    POST /api/auth/change-password/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class AddressListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating addresses.
    GET /api/auth/addresses/
    POST /api/auth/addresses/
    """
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific address.
    GET /api/auth/addresses/{id}/
    PUT /api/auth/addresses/{id}/
    DELETE /api/auth/addresses/{id}/
    """
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class WishlistView(generics.ListCreateAPIView):
    """
    API endpoint for managing user's wishlist.
    GET /api/auth/wishlist/
    POST /api/auth/wishlist/
    """
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistDeleteView(APIView):
    """
    API endpoint for removing items from wishlist.
    DELETE /api/auth/wishlist/{product_id}/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, product_id):
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )
            wishlist_item.delete()
            return Response({
                'success': True,
                'message': 'Item removed from wishlist'
            }, status=status.HTTP_200_OK)
        except Wishlist.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Item not found in wishlist'
            }, status=status.HTTP_404_NOT_FOUND)


class AdminUserListView(generics.ListAPIView):
    """
    Admin endpoint to list all users with filters.
    GET /api/auth/admin/users/
    Query params: search, role, status, page
    """
    
    serializer_class = UserListSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'last_login', 'email']
    ordering = ['-date_joined']
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Role filter
        role = self.request.query_params.get('role')
        if role and role != 'all':
            queryset = queryset.filter(user_type=role)
        
        # Status filter
        status_param = self.request.query_params.get('status')
        if status_param and status_param != 'all':
            is_active = status_param == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin endpoint to view and update user details.
    GET /api/auth/admin/users/{user_id}/
    PUT /api/auth/admin/users/{user_id}/
    """
    
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'  # ✅ Fixed: Use 'id' instead of 'user_id'
    lookup_url_kwarg = 'user_id'  # ✅ This maps URL parameter 'user_id' to lookup_field 'id'
    
    def get_queryset(self):
        return User.objects.all()
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserListSerializer(user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'User updated successfully',
            'data': UserListSerializer(user).data
        })


class AdminUserToggleStatusView(APIView):
    """
    Admin endpoint to enable/disable user account.
    POST /api/auth/admin/users/{user_id}/toggle-status/
    """
    
    permission_classes = [IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  # ✅ Fixed: Use 'id' field
            
            # Prevent disabling your own account
            if user.id == request.user.id:
                return Response({
                    'success': False,
                    'message': 'You cannot disable your own account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_active = not user.is_active
            user.save()
            
            return Response({
                'success': True,
                'message': f"User account {'enabled' if user.is_active else 'disabled'} successfully",
                'data': {
                    'id': str(user.id),
                    'email': user.email,
                    'is_active': user.is_active
                }
            })
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)


class AdminUserDeleteView(APIView):
    """
    Admin endpoint to delete user account.
    DELETE /api/auth/admin/users/{user_id}/
    """
    
    permission_classes = [IsAdminUser]
    
    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  # ✅ Fixed: Use 'id' field
            
            # Prevent deleting your own account
            if user.id == request.user.id:
                return Response({
                    'success': False,
                    'message': 'You cannot delete your own account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user.delete()
            
            return Response({
                'success': True,
                'message': 'User deleted successfully'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)