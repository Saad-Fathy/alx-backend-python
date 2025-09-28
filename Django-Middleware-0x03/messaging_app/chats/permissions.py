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

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation to view, send, update, or delete messages.
    """
    def has_permission(self, request, view):
        # Ensure the user is authenticated for all actions
        if not request.user.is_authenticated:
            return False
        # Allow access if the action doesn't require object-level checks (e.g., list or create)
        return True

    def has_object_permission(self, request, view, obj):
        # For messages, check if the user is a participant in the associated conversation
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(id=request.user.id).exists()
        # For conversations, check if the user is a participant
        return obj.participants.filter(id=request.user.id).exists()