from django_filters import rest_framework as filters
from messaging_app.chats.models import Message
from django.contrib.auth.models import User

class MessageFilter(filters.FilterSet):
    """
    Filter messages by conversation participants or time range.
    """
    participant = filters.ModelMultipleChoiceFilter(
        field_name='conversation__participants',
        queryset=User.objects.all(),
        label='Participants in conversation'
    )
    created_at__gte = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='gte',
        label='Messages created on or after'
    )
    created_at__lte = filters.DateTimeFilter(
        field_name='created_at',
        lookup_expr='lte',
        label='Messages created on or before'
    )

    class Meta:
        model = Message
        fields = ['participant', 'created_at__gte', 'created_at__lte']