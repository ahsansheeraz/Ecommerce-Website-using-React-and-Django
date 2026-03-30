"""
Serializers for User module.
Handles data validation and transformation for API requests/responses.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, Address, Wishlist
from products.models import Product
from products.serializers import ProductListSerializer


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Handles validation and creation of new users.
    """
    
    password = serializers.CharField(write_only=True, min_length=8, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Validate that password and password2 match.
        
        Args:
            attrs (dict): Request data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with validated data.
        
        Args:
            validated_data (dict): Validated user data
            
        Returns:
            User: Created user instance
        """
        # Remove password2 from data
        validated_data.pop('password2')
        
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', '')
        )
        
        # Create user profile
        #UserProfile.objects.create(user=user)
        
        # TODO: Send welcome notification
        # This will be implemented in notifications app
        # send_welcome_notification(user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates credentials and returns JWT tokens.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """
        Validate user credentials and generate tokens.
        
        Args:
            attrs (dict): Login credentials
            
        Returns:
            dict: User data with tokens
            
        Raises:
            ValidationError: If credentials are invalid
        """
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), 
                              email=email, password=password)
            
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
            
            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return {
                'user': user,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    Handles profile data including nested user information.
    """
    
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone = serializers.CharField(source='user.phone')
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'gender', 'occupation', 'company', 'website',
            'social_links', 'newsletter_subscription',
            'notification_preferences', 'profile_picture', 'user_type'
        ]
    
    def update(self, instance, validated_data):
        """
        Update both UserProfile and related User data.
        
        Args:
            instance (UserProfile): Profile instance to update
            validated_data (dict): Validated data
            
        Returns:
            UserProfile: Updated profile instance
        """
        # Handle user data
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()
        
        # Handle profile data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model.
    Handles CRUD operations for user addresses.
    """
    
    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'name', 'phone',
            'address_line1', 'address_line2', 'city',
            'state', 'country', 'postal_code',
            'is_default', 'instructions', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate(self, attrs):
        """
        Custom validation for addresses.
        """
        # Ensure at least one address is default
        if attrs.get('is_default'):
            user = self.context['request'].user
            if not self.instance and not Address.objects.filter(user=user).exists():
                attrs['is_default'] = True
        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for Wishlist model.
    Shows product details for wishlist items.
    """
    
    product_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_details', 'notes', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def get_product_details(self, obj):
        """
        Get detailed product information for wishlist display.
        
        Args:
            obj (Wishlist): Wishlist instance
            
        Returns:
            dict: Product details
        """
        return ProductListSerializer(obj.product, context=self.context).data


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    """
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """
        Validate that new password and confirm password match.
        
        Args:
            attrs (dict): Password data
            
        Returns:
            dict: Validated data
            
        Raises:
            ValidationError: If passwords don't match
        """
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        return attrs
    
    def validate_old_password(self, value):
        """
        Validate that old password is correct.
        
        Args:
            value (str): Old password
            
        Returns:
            str: Validated old password
            
        Raises:
            ValidationError: If old password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


# Email verification serializers (commented for future use)
"""
class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    def validate_token(self, value):
        # Validate email verification token
        try:
            user = User.objects.get(email_verification_token=value)
            if user.is_email_verified:
                raise serializers.ValidationError("Email already verified.")
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid verification token.")
"""