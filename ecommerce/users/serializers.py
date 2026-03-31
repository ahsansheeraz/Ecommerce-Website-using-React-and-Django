"""
Serializers for User module.
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, UserProfile, Address, Wishlist


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    
    password = serializers.CharField(
        write_only=True, 
        min_length=8,
        style={'input_type': 'password'},
        error_messages={
            'min_length': 'Password must be at least 8 characters long.'
        }
    )
    password2 = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'password', 'password2']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }
    
    def validate_email(self, value):
        """Check if email already exists."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """Validate that password and password2 match."""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        """Create a new user with validated data."""
        validated_data.pop('password2')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone=validated_data.get('phone', '')
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(
                request=self.context.get('request'), 
                email=email, 
                password=password
            )
            
            if not user:
                raise serializers.ValidationError("Invalid email or password.")
            
            if not user.is_active:
                raise serializers.ValidationError("Your account has been disabled. Please contact support.")
            
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
    """
    
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    phone = serializers.CharField(source='user.phone', required=False, allow_blank=True)
    profile_picture = serializers.ImageField(source='user.profile_picture', read_only=True)
    user_type = serializers.CharField(source='user.user_type', read_only=True)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'email', 'first_name', 'last_name', 'phone',
            'gender', 'occupation', 'company', 'website',
            'social_links', 'newsletter_subscription',
            'notification_preferences', 'profile_picture', 
            'user_type', 'is_active', 'date_joined'
        ]
    
    def update(self, instance, validated_data):
        """Update both UserProfile and related User data."""
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


class UserListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing users (admin only).
    """
    
    full_name = serializers.SerializerMethodField()
    profile_picture_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone', 'user_type', 'is_active', 'is_staff', 'is_superuser',
            'is_email_verified', 'date_joined', 'last_login', 
            'profile_picture_url'
        ]
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            return obj.profile_picture.url
        return None


class AddressSerializer(serializers.ModelSerializer):
    """
    Serializer for Address model.
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
        """Custom validation for addresses."""
        if attrs.get('is_default'):
            user = self.context['request'].user
            # Check if user has any address of this type
            if not self.instance:
                existing = Address.objects.filter(
                    user=user, 
                    address_type=attrs.get('address_type', 'shipping')
                )
                if not existing.exists():
                    attrs['is_default'] = True
        return attrs


class WishlistSerializer(serializers.ModelSerializer):
    """
    Serializer for Wishlist model.
    """
    
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    product_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'product_name', 'product_price', 'product_image', 'notes', 'added_at']
        read_only_fields = ['id', 'added_at']
    
    def get_product_image(self, obj):
        if obj.product.images.exists():
            return obj.product.images.first().image.url
        return None


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    """
    
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=8)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, attrs):
        """Validate that new password and confirm password match."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        return attrs
    
    def validate_old_password(self, value):
        """Validate that old password is correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to update user details.
    """
    
    class Meta:
        model = User
        fields = [
            'user_type', 'is_active', 'is_staff', 'is_superuser',
            'first_name', 'last_name', 'phone'
        ]
    
    def validate_user_type(self, value):
        """Validate user type change."""
        if value not in dict(User.USER_TYPE_CHOICES):
            raise serializers.ValidationError("Invalid user type.")
        return value