from django.contrib.messages.api import get_messages
from django.contrib.messages.constants import DEFAULT_LEVELS


def logout_messages(request):
    """
    Return a lazy 'messages' context variable as well as
    'DEFAULT_MESSAGE_LEVELS'.
    """
    messages = get_messages(request)
    messages = [message for message in messages if message.extra_tags == "logout"]
    return {
        "logout_messages": messages,
    }
