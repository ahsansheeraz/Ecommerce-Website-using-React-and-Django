"""
Views for User module.
Handles all HTTP requests related to user management, authentication, and profiles.
"""

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import User, Address, Wishlist, UserProfile
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, AddressSerializer,
    WishlistSerializer, ChangePasswordSerializer
)
from products.models import Product
from notifications.utils import create_notification

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    Allows new users to create an account.
    """
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Register a new user.
        
        Returns:
            Response: Success message with user data
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create welcome notification (commented for now)
        """
        create_notification(
            user=user,
            notification_type='welcome',
            title='Welcome to Our Store!',
            message=f'Welcome {user.first_name}! Thank you for joining us.'
        )
        """
        
        return Response({
            'success': True,
            'message': 'User registered successfully',
            'data': UserProfileSerializer(user.profile).data
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint for user login.
    Authenticates user and returns JWT tokens.
    """
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """
        Authenticate user and return tokens.
        
        Returns:
            Response: JWT tokens and user data
        """
        serializer = UserLoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        user = data['user']
        
        return Response({
            'success': True,
            'message': 'Logged in successfully',
            'data': {
                'access_token': data['access'],
                'refresh_token': data['refresh'],
                'user': UserProfileSerializer(user.profile).data
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    Blacklists the refresh token.
    """
    
    def post(self, request):
        """
        Logout user by blacklisting refresh token.
        
        Returns:
            Response: Success message
        """
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
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
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Get the profile of the currently authenticated user.
        
        Returns:
            UserProfile: User's profile instance
        """
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def put(self, request, *args, **kwargs):
        """
        Update user profile.
        
        Returns:
            Response: Updated profile data
        """
        return super().put(request, *args, **kwargs)


class AddressListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating addresses.
    """
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get addresses for the current user.
        
        Returns:
            QuerySet: User's addresses
        """
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Create a new address for the current user.
        
        Args:
            serializer: Address serializer instance
        """
        serializer.save(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint for retrieving, updating, and deleting a specific address.
    """
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get addresses for the current user.
        
        Returns:
            QuerySet: User's addresses
        """
        return Address.objects.filter(user=self.request.user)


class WishlistView(generics.ListCreateAPIView):
    """
    API endpoint for managing user's wishlist.
    """
    
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Get wishlist items for the current user.
        
        Returns:
            QuerySet: User's wishlist items
        """
        return Wishlist.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """
        Add a product to wishlist.
        
        Args:
            serializer: Wishlist serializer instance
        """
        serializer.save(user=self.request.user)


class WishlistDeleteView(APIView):
    """
    API endpoint for removing items from wishlist.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, product_id):
        """
        Remove a product from wishlist.
        
        Args:
            request: HTTP request
            product_id: ID of product to remove
            
        Returns:
            Response: Success message
        """
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


class ChangePasswordView(APIView):
    """
    API endpoint for changing user password.
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """
        Change user password.
        
        Args:
            request: HTTP request with old and new password
            
        Returns:
            Response: Success message
        """
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        
        # Change password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class UserSearchView(generics.ListAPIView):
    """
    API endpoint for searching users (admin only).
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """
        Search users by email, first name, or last name.
        
        Returns:
            QuerySet: Filtered users
        """
        queryset = User.objects.all()
        search = self.request.query_params.get('search', '')
        
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return queryset


# Email verification views (commented for future use)
"""
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        user = User.objects.get(email_verification_token=token)
        
        user.is_email_verified = True
        user.email_verification_token = None
        user.save()
        
        return Response({
            'success': True,
            'message': 'Email verified successfully'
        })
"""


class UserTypeUpdateView(APIView):
    """
    API endpoint for updating user type (admin only).
    """
    
    permission_classes = [permissions.IsAdminUser]
    
    def post(self, request, user_id):
        """
        Update user's role/type.
        
        Args:
            request: HTTP request with new user_type
            user_id: ID of user to update
            
        Returns:
            Response: Updated user data
        """
        try:
            user = User.objects.get(id=user_id)
            user_type = request.data.get('user_type')
            
            if user_type in dict(User.USER_TYPE_CHOICES).keys():
                user.user_type = user_type
                user.save()
                
                return Response({
                    'success': True,
                    'message': 'User type updated successfully',
                    'data': UserProfileSerializer(user.profile).data
                })
            else:
                return Response({
                    'success': False,
                    'message': 'Invalid user type'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'User not found'
            }, status=status.HTTP_404_NOT_FOUND)
        

class AdminUserListView(generics.ListAPIView):
    """
    Admin view to list all users.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Search filter
        search = self.request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(phone__icontains=search)
            )
        
        # Role filter
        role = self.request.query_params.get('role', '')
        if role and role != 'all':
            queryset = queryset.filter(user_type=role)
        
        # Status filter
        status = self.request.query_params.get('status', '')
        if status and status != 'all':
            is_active = status == 'active'
            queryset = queryset.filter(is_active=is_active)
        
        return queryset.order_by('-date_joined')


class AdminUserUpdateView(generics.UpdateAPIView):
    """
    Admin view to update user role and status.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'user_id'
    lookup_url_kwarg = 'user_id'
    
    def get_queryset(self):
        return User.objects.all()
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        user_type = request.data.get('user_type')
        is_active = request.data.get('is_active')
        is_staff = request.data.get('is_staff')
        is_superuser = request.data.get('is_superuser')
        
        if user_type:
            user.user_type = user_type
        if is_active is not None:
            user.is_active = is_active
        if is_staff is not None:
            user.is_staff = is_staff
        if is_superuser is not None:
            user.is_superuser = is_superuser
        
        user.save()
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)