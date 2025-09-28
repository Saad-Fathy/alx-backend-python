from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    All authenticated users can view messages/conversations.
    """
    def has_object_permission(self, request, view, obj):
        # Allow read-only access (GET, HEAD, OPTIONS) for authenticated users
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        # Allow write access (POST, PUT, PATCH, DELETE) only if the user is the owner
        return obj.user == request.user