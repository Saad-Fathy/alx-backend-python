import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    first_name = models.CharField(max_length=50, null=False, blank=False)
    last_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField(unique=True, null=False, blank=False)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(
        max_length=10,
        choices=[
            ('guest', 'Guest'),
            ('host', 'Host'),
            ('admin', 'Admin'),
        ],
        default='guest',
        null=False,
        blank=False
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def clean(self):
        super().clean()
        if self.phone_number and len(self.phone_number) < 10:
            raise ValidationError('Phone number must be at least 10 digits')


class Conversation(models.Model):
    """
    Model representing a conversation between multiple users
    """
    conversation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    created_at = models.DateTimeField(default=timezone.now)
    # Many-to-many relationship with users (participants)
    participants = models.ManyToManyField(
        User,
        related_name='conversations',
        through='ConversationParticipant'
    )

    class Meta:
        indexes = [
            models.Index(fields=['conversation_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        participant_names = ', '.join([
            f"{p.first_name} {p.last_name}" 
            for p in self.participants.all()[:3]
        ])
        count = self.participants.count()
        return f"Conversation ({participant_names}{'...' if count > 3 else ''})"

    @property
    def participant_count(self):
        return self.participants.count()

    def add_participant(self, user):
        """Helper method to add a participant to conversation"""
        if not self.participants.filter(id=user.id).exists():
            ConversationParticipant.objects.create(
                conversation=self,
                user=user
            )

    def remove_participant(self, user):
        """Helper method to remove a participant from conversation"""
        self.participants.remove(user)


class ConversationParticipant(models.Model):
    """
    Junction table for Conversation-Participant many-to-many relationship
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='participant_memberships'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversation_memberships'
    )
    joined_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('conversation', 'user')
        indexes = [
            models.Index(fields=['conversation', 'user']),
        ]

    def __str__(self):
        return f"{self.user.email} in {self.conversation.conversation_id}"


class Message(models.Model):
    """
    Model representing individual messages in a conversation
    """
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    message_body = models.TextField(null=False, blank=False)
    sent_at = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['message_id']),
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['sender', 'sent_at']),
        ]
        ordering = ['sent_at']

    def __str__(self):
        return f"Message from {self.sender.email} in {self.conversation.conversation_id}"

    def mark_as_read(self):
        """Helper method to mark message as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    def clean(self):
        super().clean()
        if len(self.message_body.strip()) < 1:
            raise ValidationError('Message body cannot be empty')
        if len(self.message_body) > 10000:
            raise ValidationError('Message body cannot exceed 10000 characters')