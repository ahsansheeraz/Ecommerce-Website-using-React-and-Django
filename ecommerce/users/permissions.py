"""
Custom permissions for User module.
"""

from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """Allows access only to admin users."""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type == 'admin' or request.user.is_superuser)
        )


class IsAdminOrModerator(permissions.BasePermission):
    """Allows access to admin or moderator users."""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type in ['admin', 'moderator'] or request.user.is_superuser)
        )


class IsAdminOrSeller(permissions.BasePermission):
    """Allows access to admin or seller users."""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type in ['admin', 'seller'] or request.user.is_superuser)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Allows access to object owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        # Admin can access any object
        if request.user.user_type == 'admin' or request.user.is_superuser:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user
        elif hasattr(obj, 'id') and hasattr(obj, '__class__'):
            # If obj is User model
            if obj.__class__.__name__ == 'User':
                return obj.id == request.user.id
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """Allows read-only access to all, write access only to admin/moderator."""
    
    def has_permission(self, request, view):
        # Read-only methods allowed for all
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superuser has full access
        if request.user and request.user.is_superuser:
            return True
        
        # Write methods only for admin/moderator
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type in ['admin', 'moderator']
        )


class IsSellerOrAdmin(permissions.BasePermission):
    """Allows access to sellers and admins."""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type in ['seller', 'admin'] or request.user.is_superuser)
        )