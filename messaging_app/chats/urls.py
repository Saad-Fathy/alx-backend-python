"""
URL configuration for the chats application
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router and register viewsets
router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')

# Custom URL patterns
urlpatterns = [
    path('', include(router.urls)),
    # Custom endpoints
    path('conversations/my/', views.ConversationViewSet.as_view({'get': 'my_conversations'}),
         name='my-conversations'),
    path('conversations/create-group/', 
         views.ConversationViewSet.as_view({'post': 'create_group_conversation'}),
         name='create-group-conversation'),
    path('messages/send/', 
         views.MessageViewSet.as_view({'post': 'send_message'}),
         name='send-message'),
    path('messages/conversation/<uuid:conversation_id>/', 
         views.MessageViewSet.as_view({'get': 'by_conversation'}),
         name='messages-by-conversation'),
]