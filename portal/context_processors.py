from django.contrib.messages.api import get_messages


def logout_messages(request):
    messages = get_messages(request)
    messages = [message for message in messages if message.extra_tags == "logout"]
    return {
        "logout_messages": messages,
    }
