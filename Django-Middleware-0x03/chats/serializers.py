from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Conversation, Message, ConversationParticipant


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.SerializerMethodField()
    conversation_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'user_id', 'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'role', 'created_at', 'full_name', 
            'conversation_count', 'is_active', 'date_joined'
        ]
        read_only_fields = ['user_id', 'created_at', 'date_joined']

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    def get_conversation_count(self, obj):
        return obj.conversations.count()

    def create(self, validated_data):
        # Handle password creation
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save(using=self.context['request'].database)
        return user


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender = UserSerializer(read_only=True)
    sender_id = serializers.UUIDField(write_only=True, source='sender.user_id')
    sent_at_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = [
            'message_id', 'sender', 'sender_id', 'conversation',
            'message_body', 'sent_at', 'sent_at_formatted',
            'is_read', 'read_at'
        ]
        read_only_fields = [
            'message_id', 'sender', 'sent_at', 'sent_at_formatted', 
            'is_read', 'read_at'
        ]

    def get_sent_at_formatted(self, obj):
        return obj.sent_at.strftime('%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        if not data.get('conversation'):
            raise serializers.ValidationError(
                "Conversation is required for creating a message"
            )
        return data


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for ConversationParticipant model
    """
    user = UserSerializer(read_only=True)
    user_id = serializers.UUIDField(write_only=True, source='user.user_id')

    class Meta:
        model = ConversationParticipant
        fields = [
            'conversation', 'user', 'user_id', 'joined_at', 'is_active'
        ]
        read_only_fields = ['joined_at']


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model with nested relationships
    """
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    participant_count = serializers.SerializerMethodField()
    last_message = MessageSerializer(read_only=True)
    last_message_preview = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    # For creating conversation with participants
    participant_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        min_length=2,
        max_length=50
    )

    class Meta:
        model = Conversation
        fields = [
            'conversation_id', 'created_at', 'created_at_formatted',
            'participants', 'participant_count', 'last_message',
            'last_message_preview', 'participant_ids'
        ]
        read_only_fields = [
            'conversation_id', 'created_at', 'created_at_formatted',
            'participants', 'participant_count', 'last_message'
        ]

    def get_participant_count(self, obj):
        return obj.participant_count

    def get_last_message_preview(self, obj):
        if obj.last_message:
            body = obj.last_message.message_body
            return (body[:50] + '...') if len(body) > 50 else body
        return None

    def get_created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids', [])
        
        # Create conversation
        conversation = Conversation.objects.create(**validated_data)
        
        # Add participants
        for participant_id in participant_ids:
            try:
                user = User.objects.get(user_id=participant_id)
                conversation.add_participant(user)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f"User with ID {participant_id} does not exist"
                )
        
        return conversation

    def validate_participant_ids(self, value):
        if len(value) < 2:
            raise serializers.ValidationError(
                "A conversation must have at least 2 participants"
            )
        return value


class CreateMessageSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating messages
    """
    class Meta(MessageSerializer.Meta):
        fields = ['conversation', 'message_body']
        extra_kwargs = {
            'conversation': {'write_only': True}
        }


class NestedConversationSerializer(ConversationSerializer):
    """
    Extended serializer for detailed conversation views
    """
    messages = serializers.SerializerMethodField()
    unread_message_count = serializers.SerializerMethodField()

    class Meta(ConversationSerializer.Meta):
        fields = ConversationSerializer.Meta.fields + [
            'messages', 'unread_message_count'
        ]

    def get_messages(self, obj):
        # Return recent messages (last 50)
        messages = obj.messages.select_related('sender').order_by('-sent_at')[:50]
        return MessageSerializer(messages, many=True).data

    def get_unread_message_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(
                is_read=False,
                sender__user_id__ne=request.user.user_id
            ).count()
        return 0