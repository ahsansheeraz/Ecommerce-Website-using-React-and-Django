"""
User models for authentication, profiles, addresses and permissions.
This module handles all user-related data including custom user model
with role-based permissions and address management.
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
import uuid

class UserManager(BaseUserManager):
    """
    Custom user manager for handling user creation with email as username.
    Provides methods for creating regular users and superusers.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        
        Args:
            email (str): User's email address (used as username)
            password (str): User's password
            extra_fields: Additional user fields
        
        Returns:
            User: Created user instance
        
        Raises:
            ValueError: If email is not provided
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with admin privileges.
        
        Args:
            email (str): Superuser's email
            password (str): Superuser's password
            extra_fields: Additional superuser fields
        
        Returns:
            User: Created superuser instance
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using email as the unique identifier instead of username.
    Includes user type for role-based access control and profile information.
    """
    
    # User type choices for role-based permissions
    USER_TYPE_CHOICES = (
        ('customer', 'Customer'),  # Regular customer
        ('seller', 'Seller'),      # Seller who can list products
        ('admin', 'Admin'),        # Super admin with full access
        ('moderator', 'Moderator'), # Content moderator
        ('support', 'Support'),    # Customer support staff
    )
    
    # Basic user information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
    # User type and permissions
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='customer')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    
    # Profile information
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email verification fields (commented for future use)
    """
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)
    """
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            models.Index(fields=['email', 'user_type']),
            models.Index(fields=['user_type']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.get_full_name()}"
    
    def get_full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name (first name) of the user."""
        return self.first_name
    
    def has_permission(self, permission):
        """
        Check if user has specific permission based on user_type.
        This is a simple role-based permission system.
        """
        # Admin has all permissions
        if self.user_type == 'admin' or self.is_superuser:
            return True
        
        # Define role-based permissions
        permissions_map = {
            'seller': ['add_product', 'edit_product', 'view_orders', 'manage_inventory'],
            'moderator': ['approve_reviews', 'manage_content', 'view_reports'],
            'support': ['view_tickets', 'reply_tickets', 'view_customers'],
            'customer': ['view_products', 'place_orders', 'write_reviews'],
        }
        
        return permission in permissions_map.get(self.user_type, [])


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    One-to-one relationship with User model.
    """
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    )
    
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='N')
    occupation = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=100, blank=True)
    website = models.URLField(max_length=200, blank=True)
    social_links = models.JSONField(default=dict, blank=True)  # Store social media links
    
    # Preferences
    newsletter_subscription = models.BooleanField(default=False)
    notification_preferences = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile of {self.user.email}"


class Address(models.Model):
    """
    Address model for storing user addresses.
    Users can have multiple addresses (shipping, billing, etc.)
    """
    
    ADDRESS_TYPE_CHOICES = (
        ('shipping', 'Shipping Address'),
        ('billing', 'Billing Address'),
        ('both', 'Both Shipping and Billing'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default='shipping')
    
    # Address fields
    name = models.CharField(max_length=100)  # Recipient name
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Additional info
    is_default = models.BooleanField(default=False)
    instructions = models.TextField(blank=True, help_text="Delivery instructions for this address")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'
        ordering = ['-is_default', '-created_at']
        indexes = [
            models.Index(fields=['user', 'is_default']),
        ]
    
    def __str__(self):
        return f"{self.address_line1}, {self.city} - {self.user.email}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure only one default address per user."""
        if self.is_default:
            # Set all other addresses of same type to not default
            Address.objects.filter(
                user=self.user, 
                address_type=self.address_type
            ).update(is_default=False)
        super().save(*args, **kwargs)


class Wishlist(models.Model):
    """
    User's wishlist items.
    Allows users to save products for later.
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)  # Personal notes about the item
    
    class Meta:
        verbose_name = 'Wishlist'
        verbose_name_plural = 'Wishlists'
        unique_together = ['user', 'product']  # Prevent duplicate wishlist items
        ordering = ['-added_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"