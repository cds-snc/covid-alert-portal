from django.contrib.messages.api import get_messages
from django.utils.translation import gettext as _


def logout_messages(request):
    messages = get_messages(request)
    messages = [message for message in messages if message.extra_tags == "logout"]
    return {
        "logout_messages": messages,
    }


def general_settings(request):
    return {"title_suffix": _("— COVID Alert Portal")}
