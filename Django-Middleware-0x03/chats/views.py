from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from messaging_app.chats.permissions import IsParticipantOfConversation
from messaging_app.chats.models import Conversation, Message
from rest_framework import serializers

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ['id', 'participants', 'created_at']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'conversation', 'user', 'content', 'created_at']

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Return only conversations where the user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def perform_create(self, serializer):
        # Ensure the creator is added as a participant
        conversation = serializer.save()
        conversation.participants.add(self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]

    def get_queryset(self):
        # Return only messages in conversations where the user is a participant
        return Message.objects.filter(conversation__participants=self.request.user)

    def perform_create(self, serializer):
        # Ensure the message is associated with the authenticated user
        serializer.save(user=self.request.user)