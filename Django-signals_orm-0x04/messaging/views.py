from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Prefetch
from .models import Message, MessageHistory

@login_required
def message_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    history = MessageHistory.objects.filter(message=message).order_by('-edited_at')
    return render(request, 'messaging/message_history.html', {'message': message, 'history': history})

@login_required
def delete_user(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('home')
    return render(request, 'messaging/delete_user.html')

@login_required
@cache_page(60)  # Cache for 60 seconds
def threaded_conversation(request, message_id):
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').prefetch_related(
            Prefetch('replies', queryset=Message.objects.select_related('sender', 'receiver'))
        ),
        id=message_id
    )
    def get_replies(message, replies_list=None):
        if replies_list is None:
            replies_list = []
        replies = message.replies.all()
        for reply in replies:
            replies_list.append(reply)
            get_replies(reply, replies_list)
        return replies_list

    replies = get_replies(message)
    return render(request, 'messaging/threaded_conversation.html', {'message': message, 'replies': replies})

@login_required
def unread_messages(request):
    messages = Message.unread.for_user(request.user)
    return render(request, 'messaging/unread_messages.html', {'messages': messages})