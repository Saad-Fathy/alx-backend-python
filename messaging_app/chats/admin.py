from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Conversation, Message, ConversationParticipant


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Custom admin interface for User model
    """
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'role', 'email'),
        }),
    )


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Admin interface for Conversation model
    """
    list_display = ['conversation_id', 'participant_count', 'created_at']
    list_filter = ['created_at']
    search_fields = ['conversation_id']
    readonly_fields = ['conversation_id', 'created_at']
    
    filter_horizontal = ['participants']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Admin interface for Message model
    """
    list_display = ['message_id', 'sender', 'conversation', 'sent_at', 'is_read']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['message_id', 'message_body', 'sender__email']
    readonly_fields = ['message_id', 'sent_at', 'read_at']
    date_hierarchy = 'sent_at'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation')


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    """
    Admin interface for ConversationParticipant model
    """
    list_display = ['conversation', 'user', 'joined_at', 'is_active']
    list_filter = ['is_active', 'joined_at']
    search_fields = ['conversation__conversation_id', 'user__email']
    readonly_fields = ['joined_at']