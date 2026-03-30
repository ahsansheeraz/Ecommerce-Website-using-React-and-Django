"""
Django admin configuration for User module.
Kept as backup, main admin will be in React.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, Address, Wishlist


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    can_delete = False


class AddressInline(admin.TabularInline):
    """Inline admin for Address."""
    model = Address
    extra = 1


class WishlistInline(admin.TabularInline):
    """Inline admin for Wishlist."""
    model = Wishlist
    extra = 1


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin configuration.
    """
    
    inlines = [UserProfileInline, AddressInline, WishlistInline]
    
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone', 'profile_picture')}),
        (_('Permissions'), {
            'fields': ('user_type', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin configuration for Address."""
    
    list_display = ['user', 'name', 'address_type', 'city', 'country', 'is_default']
    list_filter = ['address_type', 'country', 'is_default']
    search_fields = ['user__email', 'name', 'address_line1', 'city']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin configuration for Wishlist."""
    
    list_display = ['user', 'product', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__email', 'product__name']