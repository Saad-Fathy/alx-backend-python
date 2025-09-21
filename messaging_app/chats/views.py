from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import User, Conversation, Message
from .serializers import (
    UserSerializer, ConversationSerializer, 
    CreateMessageSerializer, NestedConversationSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for User management
    """
    queryset = User.objects.select_related().all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """
        Custom permissions: allow registration, restrict other actions
        """
        if self.action in ['create']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filter users based on permissions
        """
        if self.request.user.is_authenticated:
            return User.objects.filter(
                Q(id=self.request.user.id) | 
                Q(role='admin') & Q(id=self.request.user.id)
            )
        return User.objects.none()

    def perform_create(self, serializer):
        """Handle user creation with password"""
        password = self.request.data.get('password')
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()


class ConversationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Conversation management
    """
    queryset = Conversation.objects.select_related().prefetch_related(
        'participants', 'messages__sender'
    ).all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'conversation_id'

    def get_queryset(self):
        """
        Return only conversations that the current user participates in
        """
        return self.queryset.filter(
            participants__user_id=self.request.user.user_id
        ).distinct()

    def perform_create(self, serializer):
        """
        Ensure the creator is added as a participant
        """
        conversation = serializer.save()
        conversation.add_participant(self.request.user)
        return conversation

    @action(detail=False, methods=['get'])
    def my_conversations(self, request):
        """
        Get all conversations for the current user
        """
        conversations = self.get_queryset().select_related(
            'messages__sender'
        ).prefetch_related('participants')
        
        # Get the latest message for each conversation
        conversations_with_last_message = []
        for conversation in conversations:
            last_message = conversation.messages.last()
            conversation.last_message = last_message
            conversations_with_last_message.append(conversation)
        
        serializer = NestedConversationSerializer(
            conversations_with_last_message, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def mark_all_as_read(self, request, conversation_id=None):
        """
        Mark all messages in this conversation as read for the current user
        """
        conversation = self.get_object()
        unread_messages = conversation.messages.filter(
            is_read=False,
            sender__user_id__ne=request.user.user_id
        )
        unread_messages.update(is_read=True, read_at=timezone.now())
        
        return Response({
            'status': 'success',
            'marked_as_read': unread_messages.count(),
            'conversation_id': str(conversation_id)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def create_group_conversation(self, request):
        """
        Create a group conversation with multiple participants
        """
        participant_ids = request.data.get('participant_ids', [])
        
        # Ensure current user is included
        if str(request.user.user_id) not in participant_ids:
            participant_ids.append(str(request.user.user_id))
        
        serializer = self.get_serializer(data={
            'participant_ids': participant_ids,
            **request.data
        })
        
        if serializer.is_valid():
            conversation = serializer.save()
            conversation.add_participant(request.user)
            return Response(
                NestedConversationSerializer(conversation, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Message management
    """
    queryset = Message.objects.select_related(
        'sender', 'conversation__participants'
    ).all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'message_id'

    def get_queryset(self):
        """
        Return messages from conversations the user participates in
        """
        return self.queryset.filter(
            conversation__participants__user_id=self.request.user.user_id
        ).order_by('sent_at')

    def get_serializer_class(self):
        """
        Use different serializers for different actions
        """
        if self.action == 'create':
            return CreateMessageSerializer
        return MessageSerializer

    def perform_create(self, serializer):
        """
        Automatically save message and notify participants
        """
        message = serializer.save()
        
        # Update conversation's last message timestamp
        message.conversation.created_at = message.sent_at
        message.conversation.save(update_fields=['created_at'])
        
        return message

    @action(detail=False, methods=['get'], url_path='conversation/(?P<conversation_id>[^/.]+)')
    def by_conversation(self, request, conversation_id=None):
        """
        Get all messages for a specific conversation
        """
        conversation = get_object_or_404(
            Conversation, 
            conversation_id=conversation_id,
            participants__user_id=request.user.user_id
        )
        
        messages = conversation.messages.select_related('sender').order_by('sent_at')
        
        # Pagination
        page = self.paginate_queryset(messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def mark_as_read(self, request, message_id=None):
        """
        Mark a specific message as read
        """
        message = self.get_object()
        if message.is_read:
            return Response(
                {'error': 'Message is already read'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        message.mark_as_read()
        return Response({
            'status': 'success',
            'message_id': str(message_id),
            'read_at': message.read_at.isoformat()
        })

    @action(detail=False, methods=['post'])
    def send_message(self, request):
        """
        Simplified endpoint for sending messages
        """
        serializer = CreateMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(sender=request.user)
            return Response(
                MessageSerializer(message, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)