"""
Custom permissions for User module.
Defines role-based access control for different user types.
"""

from rest_framework import permissions


class IsAdminOrModerator(permissions.BasePermission):
    """
    Custom permission to only allow admin or moderator to access the view.
    """
    
    def has_permission(self, request, view):
        """
        Check if user has admin or moderator role.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            bool: True if user is admin or moderator
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type in ['admin', 'moderator'] or request.user.is_superuser)
        )


class IsAdminOrSeller(permissions.BasePermission):
    """
    Custom permission to allow admin or seller access.
    """
    
    def has_permission(self, request, view):
        """
        Check if user has admin or seller role.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            bool: True if user is admin or seller
        """
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type in ['admin', 'seller'] or request.user.is_superuser)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to access it.
    """
    
    def has_object_permission(self, request, view, obj):
        """
        Check if user owns the object or is admin.
        
        Args:
            request: HTTP request
            view: View being accessed
            obj: Object being accessed
            
        Returns:
            bool: True if user owns object or is admin
        """
        # Admin can access any object
        if request.user.user_type == 'admin' or request.user.is_superuser:
            return True
        
        # Check if object has user attribute
        if hasattr(obj, 'user'):
            return obj.user == request.user
        elif hasattr(obj, 'customer'):
            return obj.customer == request.user
        
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to all users,
    but write access only to admins.
    """
    
    def has_permission(self, request, view):
        """
        Check permissions based on request method.
        
        Args:
            request: HTTP request
            view: View being accessed
            
        Returns:
            bool: True if user has permission
        """
        # Allow safe methods for all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write methods only for admins
        return bool(
            request.user and 
            request.user.is_authenticated and 
            (request.user.user_type == 'admin' or request.user.is_superuser)
        )